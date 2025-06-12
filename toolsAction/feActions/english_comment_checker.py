import os
import re
import tkinter as tk


def is_english_word(word: str) -> bool:
    """Check if a word contains only English letters"""
    return bool(re.match(r"^[a-zA-Z]+$", word))


def find_english_comments(content: str) -> list[tuple[int, str, list[str]]]:
    """Find comments containing English words"""
    english_comments = []

    # Regex patterns for different types of comments
    patterns = [
        # Single line comments
        r"//.*$",
        # Multi-line comments
        r"/\*(?:[^*]|\*(?!/))*\*/",
        # Vue template comments
        r"<!--.*?-->",
    ]

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        for pattern in patterns:
            comments = re.finditer(pattern, line, re.MULTILINE)
            for match in comments:
                comment = match.group()
                words = re.findall(r"\b\w+\b", comment)
                english_words = [
                    w for w in words if is_english_word(w) and len(w) > 1
                ]  # Skip single letters

                if english_words:
                    english_comments.append((i, comment.strip(), english_words))

    return english_comments


def check_english_comments(file_path: str) -> list[str]:
    """Check file for English comments"""
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"❌ Error reading file {os.path.basename(file_path)}: {str(e)}"]

    english_comments = find_english_comments(content)
    if not english_comments:
        return [f"✅ No English comments found in {os.path.basename(file_path)}"]

    results = []
    for line_num, comment, eng_words in english_comments:
        results.append(
            f"⚠️ Line {line_num}: Found English words in comment: {', '.join(eng_words)}\n   {comment}"
        )

    return results


def check_english_comments_main(app):
    """Main function to check for English comments in files"""
    files = app.get_file_list()
    if not files:
        return

    app.output_text.delete("1.0", tk.END)
    app.set_running_state(True)

    try:
        found_english = False
        for file_path in files:
            results = check_english_comments(file_path)
            if any("⚠️" in result for result in results):
                found_english = True
                app.output_text.insert(
                    tk.END, f"\n🔍 {os.path.basename(file_path)}:\n", "highlight"
                )
                for result in results:
                    tag = "warning" if "⚠️" in result else "success"
                    app.output_text.insert(tk.END, f"{result}\n", tag)

        if not found_english:
            app.output_text.insert(tk.END, "✅ No English comments found in any files\n", "success")

    finally:
        app.set_running_state(False)
