import os
import re
import tkinter as tk


def get_css_properties_to_ignore() -> list[str]:
    """Returns a list of CSS properties that might contain color names but should be ignored"""
    return [
        "white-space",
        "background-clip",
        "text-decoration-style",
        "border-style",
        "outline-style",
        "font-style",
        "font-family",
        "list-style",
        "background-repeat",
        "background-position",
        "background-origin",
        "background-size",
        "background-attachment",
        "text-align",
        "vertical-align",
        "float",
        "clear",
    ]


def find_color_in_css(content: str) -> list[tuple[int, str, str]]:
    """Find color values in CSS content"""
    color_values = []
    lines = content.split("\n")

    # Common color names that should be replaced with variables
    color_names = [
        "white",
        "black",
        "red",
        "green",
        "blue",
        "yellow",
        "purple",
        "orange",
        "gray",
        "grey",
        "pink",
        "brown",
        "cyan",
        "magenta",
    ]

    # CSS properties to ignore
    ignore_properties = get_css_properties_to_ignore()
    ignore_pattern = "|".join(ignore_properties)

    # Pattern for hex colors (3 or 6 digits)
    hex_pattern = r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b"

    for i, line in enumerate(lines, 1):
        # Skip lines that contain ignored properties
        if re.search(rf"\b({ignore_pattern})\b", line):
            continue

        # Check for hex colors
        hex_matches = re.finditer(hex_pattern, line)
        for match in hex_matches:
            color_values.append((i, line.strip(), match.group(0)))

        # Check for color names
        for color in color_names:
            # Only match color names that are values, not property names
            # This avoids matching things like "background-color"
            if re.search(rf":\s*{color}\b", line, re.IGNORECASE):
                color_values.append((i, line.strip(), color))

        # Check for rgb/rgba values
        if "rgb" in line.lower():
            # Skip rgb values that use CSS variables
            if "rgb(var(--" in line:
                continue

            rgb_matches = re.finditer(r"rgba?\([^)]+\)", line)
            for match in rgb_matches:
                # Double check that this isn't using a CSS variable
                if "var(--" not in match.group(0):
                    color_values.append((i, line.strip(), match.group(0)))

    return color_values


def check_css_color(file_path: str) -> list[str]:
    """Check file for hardcoded CSS color values"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f" Error reading file {os.path.basename(file_path)}: {str(e)}"]

    color_values = find_color_in_css(content)
    if not color_values:
        return []  # Return empty list if no color values found

    results = []
    for line_num, line_content, value in color_values:
        suggestion = "Consider using a CSS variable (--color-name) instead"
        results.append(
            f" Line {line_num}: Found hardcoded color value: {value}\n"
            f"   {line_content}\n"
            f"   💡 {suggestion}"
        )

    return results


def check_css_color_main(app):
    """Main function to check CSS color values in files"""
    files = app.get_file_list()
    if not files:
        return

    app.output_text.delete("1.0", tk.END)
    app.set_running_state(True)

    try:
        found_issues = False
        for file_path in files:
            if file_path.endswith((".css", ".scss", ".vue")):  # Only check CSS/SCSS/Vue files
                results = check_css_color(file_path)
                if results:
                    found_issues = True
                    app.output_text.insert(
                        tk.END, f"\n {os.path.basename(file_path)}:\n", "highlight"
                    )
                    for result in results:
                        app.output_text.insert(tk.END, f"{result}\n", "warning")

        if not found_issues:
            app.output_text.insert(tk.END, " No hardcoded color values found\n", "success")

    finally:
        app.set_running_state(False)
