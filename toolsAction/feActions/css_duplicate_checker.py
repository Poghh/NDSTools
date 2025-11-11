import os
import re
import tkinter as tk


def extract_css_classes(content: str) -> set[str]:
    """Extract CSS class names from content"""
    # Match class names in CSS/SCSS
    # Handles both regular .class and nested classes
    class_pattern = r"\.([a-zA-Z0-9_-]+)\s*[{,]"
    classes = set()

    # Find all class declarations
    matches = re.finditer(class_pattern, content)
    for match in matches:
        classes.add(match.group(1))

    return classes


def find_scss_imports(content: str) -> list[str]:
    """Find all SCSS imports in the content"""
    # Match @use and @import statements
    import_pattern = r'@(?:use|import)\s+[\'"]([^\'"]*)[\'"]\s*;'
    imports = []

    matches = re.finditer(import_pattern, content)
    for match in matches:
        path = match.group(1)
        # Convert @/styles to absolute path
        if path.startswith("@/styles"):
            path = path.replace("@/styles", "styles")
        imports.append(path)

    return imports


def resolve_scss_path(base_path: str, import_path: str) -> str:
    """Resolve the actual path of an imported SCSS file"""
    # Remove extension if present
    import_path = os.path.splitext(import_path)[0]

    # Get the directory of the base file
    base_dir = os.path.dirname(base_path)

    # Try different possible paths
    possible_paths = [
        os.path.join(base_dir, f"{import_path}.scss"),
        os.path.join(base_dir, f"_{import_path}.scss"),
        os.path.join(base_dir, import_path, "index.scss"),
        os.path.join(base_dir, import_path, "_index.scss"),
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return ""


def extract_style_content(vue_content: str) -> str:
    """Extract the content of the <style> block from Vue file"""
    style_pattern = r"<style[^>]*>(.*?)</style>"
    match = re.search(style_pattern, vue_content, re.DOTALL)
    return match.group(1) if match else ""


def check_duplicate_css(file_path: str) -> list[str]:
    """Check for duplicate CSS classes between Vue file and its imported SCSS files"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f" Error reading file {os.path.basename(file_path)}: {str(e)}"]

    # Extract style content from Vue file
    style_content = extract_style_content(content)
    if not style_content:
        return []  # No style block found

    # Get CSS classes defined in Vue file
    vue_classes = extract_css_classes(style_content)
    if not vue_classes:
        return []  # No classes defined in Vue file

    # Find SCSS imports
    imports = find_scss_imports(style_content)
    if not imports:
        return []  # No imports found

    results = []
    for import_path in imports:
        # Resolve actual path of imported file
        scss_path = resolve_scss_path(file_path, import_path)
        if not scss_path:
            results.append(f" Could not resolve import path: {import_path}")
            continue

        try:
            with open(scss_path, encoding="utf-8") as f:
                scss_content = f.read()
        except Exception as e:
            results.append(f" Error reading imported file {scss_path}: {str(e)}")
            continue

        # Get CSS classes defined in imported file
        scss_classes = extract_css_classes(scss_content)

        # Find duplicates
        duplicates = vue_classes.intersection(scss_classes)
        if duplicates:
            results.append(
                f" Found duplicate classes in {os.path.basename(file_path)} that are already defined in {os.path.basename(scss_path)}:"
            )
            for cls in sorted(duplicates):
                results.append(f"   • .{cls}")
            results.append(
                f"   💡 Consider removing these duplicate classes and using the ones from {os.path.basename(scss_path)}"
            )

    return results


def check_duplicate_css_main(app):
    """Main function to check for duplicate CSS classes"""
    files = app.get_file_list()
    if not files:
        return

    app.output_text.delete("1.0", tk.END)
    app.set_running_state(True)

    try:
        found_issues = False
        for file_path in files:
            if file_path.endswith(".vue"):  # Only check Vue files
                results = check_duplicate_css(file_path)
                if results:
                    found_issues = True
                    app.output_text.insert(
                        tk.END, f"\n {os.path.basename(file_path)}:\n", "highlight"
                    )
                    for result in results:
                        tag = "error" if "" in result else ("warning" if "" in result else None)
                        app.output_text.insert(tk.END, f"{result}\n", tag)

        if not found_issues:
            app.output_text.insert(tk.END, " No duplicate CSS classes found\n", "success")

    finally:
        app.set_running_state(False)
