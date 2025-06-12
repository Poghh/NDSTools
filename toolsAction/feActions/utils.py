import tkinter as tk


def display_output(self, text):
    for line in text.splitlines():
        tag = "error" if any(keyword in line.lower() for keyword in ["error", "✖", "❌"]) else None
        self.output_text.insert(tk.END, line + "\n", tag)


def clear_all(self):
    self.path_input.delete("1.0", tk.END)
    self.output_text.delete("1.0", tk.END)
    self.status_label.config(text="")
    self.excel_label.config(text="Chưa chọn file", fg="gray")
    self.excel_output.delete("1.0", tk.END)
    self.author_entry.delete(0, tk.END)


def set_running_state(self, running: bool):
    state = tk.DISABLED if running else tk.NORMAL
    self.run_button.config(state=state)
    self.count_button.config(state=state)
    self.clear_button.config(state=state)
    self.upload_excel_btn.config(state=state)
    self.check_title_button.config(state=state)
    self.check_color_button.config(state=state)
    self.check_hardcode_button.config(state=state)
    self.check_console_button.config(state=state)
    self.check_jsdoc_button.config(state=state)
    self.status_label.config(text="⏳ Đang xử lý..." if running else "✅ Sẵn sàng.")
