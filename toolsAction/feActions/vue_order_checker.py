import os
import re
import tkinter as tk


def get_section_patterns() -> dict[str, tuple]:
    """Returns regex patterns to identify different sections of a Vue component"""
    return {
        "imports": (1, r"import\s+.*from\s+['\"]\S+['\"]\s*"),
        "directives": (2, r"(v-[\w-]+|\s+directive\s*)"),
        "defineOptions": (3, r"defineOptions\s*\(\s*{[^}]*}\s*\)"),
        "props": (4, r"(defineProps|props\s*:|props\s*=)"),
        "emits": (5, r"(defineEmits|emits\s*:|emits\s*=)"),
        "slots": (6, r"useSlots\s*\(\s*\)"),
        "provide/inject": (7, r"(provide|inject)\s*\(\s*['\"]"),
        "constants": (8, r"const\s+[A-Z_][A-Z0-9_]*\s*="),
        "refs": (9, r"ref\s*\(\s*(?:null|''|\"\"|\[\]|{\s*}|\d+)\s*\)"),
        "reactive_state": (10, r"(reactive|ref)\s*\(\s*"),
        "computed": (11, r"computed\s*\(\s*\(\s*\)\s*=>"),
        "watch": (12, r"watch\s*\(\s*"),
        "lifecycle": (
            13,
            r"(onMounted|onBeforeMount|onUnmounted|onBeforeUnmount|onUpdated|onBeforeUpdate)\s*\(\s*",
        ),
        "methods": (14, r"(function\s+\w+|const\s+\w+\s*=\s*\([^)]*\)\s*=>)"),
        "expose": (15, r"defineExpose\s*\(\s*{"),
    }


def find_sections(content: str) -> list[tuple[int, str, int]]:
    """Find all sections in the content with their line numbers and order"""
    sections = []
    patterns = get_section_patterns()
    lines = content.split("\n")

    for i, line in enumerate(lines, 1):
        for section_name, (order, pattern) in patterns.items():
            if re.search(pattern, line):
                sections.append((i, section_name, order))

    return sections


def check_vue_order(file_path: str) -> list[str]:
    """Check if the Vue component sections are in the correct order"""
    if not os.path.exists(file_path):
        return [f"❌ File not found: {file_path}"]

    if not file_path.endswith(".vue"):
        return []  # Skip silently if not a Vue file

    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"❌ Error reading file {file_path}: {str(e)}"]

    sections = find_sections(content)
    if not sections:
        return [f"⚠️ No recognizable Vue sections found in {file_path}"]

    errors = []
    last_order = -1
    last_line = -1
    last_section = ""

    for line_num, section_name, order in sorted(sections, key=lambda x: x[0]):
        if order < last_order:
            errors.append(
                f"❌ Line {line_num}: '{section_name}' should come before '{last_section}' (line {last_line})"
            )
        last_order = order
        last_line = line_num
        last_section = section_name

    if not errors:
        return [f"✅ All sections are in correct order in {file_path}"]

    return errors


def check_vue_order_main(app):
    """Main function to check Vue component order for all input files"""
    files = app.get_file_list()
    if not files:
        return

    app.output_text.delete("1.0", tk.END)
    app.set_running_state(True)

    try:
        for file_path in files:
            results = check_vue_order(file_path)
            if results:  # Only show results if it's a Vue file
                app.output_text.insert(
                    tk.END, f"\n🔍 Checking {os.path.basename(file_path)}...\n", "highlight"
                )
                for result in results:
                    tag = "error" if "❌" in result else ("warning" if "⚠️" in result else "success")
                    app.output_text.insert(tk.END, f"{result}\n", tag)
    finally:
        app.set_running_state(False)
