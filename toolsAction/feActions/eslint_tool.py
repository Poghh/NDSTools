import subprocess
import tkinter as tk
import os

def run_eslint(self):
    self.set_running_state(True)
    self.output_text.delete("1.0", tk.END)
    files = self.get_file_list()
    if not files:
        self.set_running_state(False)
        return

    for file_path in files:
        self.output_text.insert(tk.END, f"\n🔧 ESLint: {file_path}\n")
        self.output_text.see(tk.END)
        self.root.update()

        try:
            result = subprocess.run(
                ["npx", "eslint", "--no-warn-ignored", file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                shell=True,
                cwd=os.getcwd()
            )
            self.display_output(result.stdout)
            self.display_output(result.stderr)

            if result.returncode != 0:
                self.output_text.insert(tk.END, f"❌ ESLint lỗi ở: {file_path}\n", "error")

        except Exception as e:
            self.output_text.insert(tk.END, f"❌ Lỗi khi xử lý ESLint: {str(e)}\n", "error")

    self.output_text.insert(tk.END, "\n✅ ESLint hoàn tất.\n")
    self.set_running_state(False) 