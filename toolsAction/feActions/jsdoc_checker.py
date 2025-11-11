import os
import re
import tkinter as tk


def check_jsdoc(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    # Patterns for function detection
    arrow_func_pattern = re.compile(
        r"^\s*(const|let|var)\s+\w+\s*=\s*(async\s*)?\((.*?)\)\s*=>\s*{"
    )
    named_func_pattern = re.compile(r"^\s*function\s+\w+\s*\((.*?)\)\s*{")
    watch_pattern = re.compile(r"\bwatch\s*\((.*?)\)")
    computed_pattern = re.compile(r"\bcomputed\s*\((.*?)\)")
    vue_lifecycle_pattern = re.compile(
        r"\bon(Mounted|Updated|Unmounted|BeforeMount|BeforeUpdate|BeforeUnmount|Activated|Deactivated)\b"
    )

    # Pattern for high-level variable declarations
    var_patterns = [
        # Basic variable declarations with optional type
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*(?::\s*[^=]+)?\s*="),
        # Vue ref declarations
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*=\s*ref\("),
        # Vue reactive declarations
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*=\s*reactive\("),
        # Vue computed declarations
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*=\s*computed\("),
        # Vue defineProps
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*=\s*defineProps"),
        # Type declarations with initialization
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*:\s*\w+\s*="),
        # Interface type declarations
        re.compile(r"^\s*(const|let|var)\s+(\w+)\s*:\s*[A-Z]\w+(?:<[^>]+>)?\s*="),
    ]

    # Patterns for JSDoc validation
    re.compile(r"@param\s+(?:{[^}]*}\s+)?(\w+)|@param\s+(\w+)")
    re.compile(r"@returns?")
    return_statement_pattern = re.compile(r"\breturn\s+\S+")
    type_pattern = re.compile(r"@type\s+")

    # Pattern to identify section comments
    section_comment_pattern = re.compile(r"^/\*{2,}\s*\n\s*\*\s*[A-Za-z]+.*\n\s*\*{2,}/\s*$")

    def is_inside_function(lines, current_idx):
        brace_count = 0
        for i in range(current_idx, -1, -1):
            line = lines[i].strip()
            brace_count += line.count("}") - line.count("{")
            if brace_count > 0:  # We've found more closing braces than opening ones
                return True
            if arrow_func_pattern.match(line) or named_func_pattern.match(line):
                return True
        return False

    def is_section_comment(line):
        return bool(section_comment_pattern.match(line))

    def extract_param_names(comment_lines):
        documented_params = set()
        for line in comment_lines:
            # Remove asterisks and leading/trailing whitespace
            line = re.sub(r"^\s*\*\s*", "", line.strip())
            # Look for @param followed by optional type and parameter name
            param_matches = re.finditer(r"@param\s+(?:{[^}]*}\s+)?(\w+)|@param\s+(\w+)", line)
            for match in param_matches:
                param_name = match.group(1) or match.group(2)
                if param_name:
                    documented_params.add(param_name.strip())
        return documented_params

    def has_return_doc(comment_lines):
        for line in comment_lines:
            # Remove asterisks and leading/trailing whitespace
            line = re.sub(r"^\s*\*\s*", "", line.strip())
            if re.search(r"@returns?(?:\s+{[^}]*})?\s+", line):
                return True
        return False

    def has_valid_comment(lines, idx):
        comment_lines = []
        has_comment = False
        is_after_section = False

        # Check if we're right after a section comment
        for lookback in range(1, 4):
            if idx - lookback >= 0:
                prev_line = lines[idx - lookback].strip()
                if is_section_comment(prev_line):
                    is_after_section = True
                    break
                if (
                    prev_line.startswith("/*")
                    or prev_line.startswith("/**")
                    or prev_line.startswith("*")
                    or prev_line.startswith("<!--")
                ):
                    has_comment = True
                    # Collect all comment lines
                    for comment_idx in range(idx - lookback, idx):
                        comment_line = lines[comment_idx].strip()
                        if comment_line and not comment_line.startswith(
                            "*/"
                        ):  # Skip empty lines and closing tags
                            comment_lines.append(comment_line)
                    break

        return has_comment or is_after_section, comment_lines

    for file_path in files:
        if not file_path.endswith(".vue"):
            continue

        if not os.path.exists(file_path):
            self.output_text.insert(tk.END, f" Không tìm thấy file: {file_path}\n", "error")
            continue

        error_count = 0
        error_messages = []

        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()

        for idx in range(len(lines)):
            line = lines[idx].strip()
            func_match = None
            params = []

            # Extract parameter names without type information
            def extract_params(param_str):
                if not param_str:
                    return []
                # Split by comma and extract just the parameter name before any type annotation
                return [p.split(":")[0].strip() for p in param_str.split(",") if p.strip()]

            # Check for variable declarations at program level
            var_match = None
            for pattern in var_patterns:
                match = pattern.match(line)
                if match:
                    var_match = match
                    break

            if var_match and not is_inside_function(lines, idx):
                # Skip checking if this is a section comment
                if is_section_comment(line):
                    continue

                # Check for comments for variable declaration
                has_comment, comment_lines = has_valid_comment(lines, idx)

                if not has_comment:
                    error_count += 1
                    snippet = lines[max(0, idx - 1) : min(len(lines), idx + 3)]
                    error_messages.append(
                        f"- dòng {idx + 1} thiếu comment giải thích cho biến:\n{''.join(snippet)}\n"
                    )
                else:
                    # Check if variable has type documentation
                    comment_text = " ".join(comment_lines)
                    has_type_doc = type_pattern.search(comment_text) is not None
                    if (
                        not has_type_doc and comment_lines
                    ):  # Only check for @type if there are actual comment lines
                        error_count += 1
                        error_messages.append(
                            f"- dòng {idx + 1} thiếu tài liệu @type cho biến:\n{''.join(lines[max(0, idx - 3) : min(len(lines), idx + 1)])}\n"
                        )

            # Check for function definitions and extract parameters
            if arrow_func_pattern.match(line):
                func_match = arrow_func_pattern.match(line)
                if func_match:
                    params = extract_params(func_match.group(3))
                else:
                    params = []
            elif named_func_pattern.match(line):
                func_match = named_func_pattern.match(line)
                if func_match:
                    params = extract_params(func_match.group(1))
                else:
                    params = []
            elif (
                watch_pattern.search(line)
                or computed_pattern.search(line)
                or vue_lifecycle_pattern.search(line)
            ):
                func_match = True
                params = []

            if func_match:
                # Check for return statement in function body
                has_return = False
                brace_count = 0
                for future_idx in range(idx, min(len(lines), idx + 50)):  # Look ahead max 50 lines
                    future_line = lines[future_idx].strip()
                    brace_count += future_line.count("{") - future_line.count("}")
                    if return_statement_pattern.search(future_line):
                        has_return = True
                    if brace_count <= 0:
                        break

                # Check for comments
                has_comment, comment_lines = has_valid_comment(lines, idx)

                if not has_comment:
                    error_count += 1
                    snippet = lines[max(0, idx - 1) : min(len(lines), idx + 3)]
                    error_messages.append(
                        f"- dòng {idx + 1} thiếu comment giải thích:\n{''.join(snippet)}\n"
                    )
                else:
                    # Extract documented parameters
                    documented_params = extract_param_names(comment_lines)
                    has_return_documentation = has_return_doc(comment_lines)

                    # Check if all parameters are documented
                    if params:
                        missing_params = [p for p in params if p and p not in documented_params]
                        if missing_params:
                            error_count += 1
                            error_messages.append(
                                f"- dòng {idx + 1} thiếu tài liệu cho các tham số: {', '.join(missing_params)}:\n{''.join(lines[max(0, idx - 3) : min(len(lines), idx + 1)])}\n"
                            )

                    # Check if return is documented when function has return statement
                    if has_return and not has_return_documentation:
                        error_count += 1
                        error_messages.append(
                            f"- dòng {idx + 1} thiếu tài liệu cho giá trị trả về:\n{''.join(lines[max(0, idx - 3) : min(len(lines), idx + 1)])}\n"
                        )

        # Display error count and messages for this file
        self.output_text.insert(
            tk.END, f"file {os.path.basename(file_path)}: {error_count} lỗi\n", "title-color"
        )
        for message in error_messages:
            self.output_text.insert(tk.END, message)

    self.output_text.insert(tk.END, "\n Kiểm tra comment hoàn tất.\n")
    self.set_running_state(False)
