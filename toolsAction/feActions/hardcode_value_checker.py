import os
import re
import tkinter as tk


def find_hardcoded_comparisons(content: str) -> list[tuple[int, str, str]]:
    """Find hardcoded values in comparisons"""
    hardcoded_values = []
    lines = content.split("\n")

    # Patterns to match different comparison operators with hardcoded values
    patterns = [
        # Equal comparisons
        r'([!=]==?\s*["\'][^"\']*["\'])',  # String literals
        r"([!=]==?\s*-?\d+(?:\.\d+)?)",  # Number literals
        r"([!=]==?\s*true\b)",  # true literal
        r"([!=]==?\s*false\b)",  # false literal
        r"([!=]==?\s*null\b)",  # null literal
        # Reverse order comparisons
        r'(["\'][^"\']*["\'])\s*[!=]==?',  # String literals
        r"(-?\d+(?:\.\d+)?)\s*[!=]==?",  # Number literals
        r"(true)\s*[!=]==?",  # true literal
        r"(false)\s*[!=]==?",  # false literal
        r"(null)\s*[!=]==?",  # null literal
    ]

    # Patterns to ignore (valid constant usages)
    ignore_patterns = [
        r"[A-Z][A-Z0-9_]*\.[A-Z0-9_]*",  # CONSTANT.VALUE
        r"[A-Z][a-zA-Z0-9]*Const\.",  # SomeConst.
        r"Constants\.",  # Constants.
        r"CONSTANTS\.",  # CONSTANTS.
    ]

    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Check if this comparison uses a valid constant
                is_valid_constant = any(
                    re.search(ignore_pat, line.replace(match.group(1), ""))
                    for ignore_pat in ignore_patterns
                )

                if not is_valid_constant:
                    hardcoded_values.append((i, line.strip(), match.group(1)))

    return hardcoded_values


def check_hardcoded_values(file_path: str) -> list[str]:
    """Check file for hardcoded values in comparisons"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f" Error reading file {os.path.basename(file_path)}: {str(e)}"]

    hardcoded_values = find_hardcoded_comparisons(content)
    if not hardcoded_values:
        return []  # Return empty list if no hardcoded values found

    results = []
    for line_num, line_content, value in hardcoded_values:
        suggestion = "Consider using a constant instead"
        results.append(
            f" Line {line_num}: Hardcoded value {value} in comparison\n"
            f"   {line_content}\n"
            f"   💡 {suggestion}"
        )

    return results


def check_hardcoded_values_main(app):
    """Main function to check for hardcoded values in files"""
    files = app.get_file_list()
    if not files:
        return

    app.output_text.delete("1.0", tk.END)
    app.set_running_state(True)

    try:
        found_issues = False
        for file_path in files:
            if file_path.endswith(
                (".js", ".jsx", ".ts", ".tsx", ".vue")
            ):  # Only check JS/TS/Vue files
                results = check_hardcoded_values(file_path)
                if results:
                    found_issues = True
                    app.output_text.insert(
                        tk.END, f"\n {os.path.basename(file_path)}:\n", "highlight"
                    )
                    for result in results:
                        app.output_text.insert(tk.END, f"{result}\n", "warning")

        if not found_issues:
            app.output_text.insert(
                tk.END, " No hardcoded values found in comparisons\n", "success"
            )

    finally:
        app.set_running_state(False)
