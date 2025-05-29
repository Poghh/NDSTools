import tkinter as tk


def generate_comment(tab_instance):
    author = tab_instance.author_entry.get().strip()
    screen_code = tab_instance.screen_code_entry.get().strip()
    selected_date = tab_instance.date_entry.get_date()

    if not author:
        tab_instance.output_text.delete(1.0, tk.END)
        tab_instance.output_text.insert(tk.END, "Vui lòng nhập tên tác giả.")
        return  # cần return tại đây, nếu thiếu author thì không nên tiếp tục

    if not screen_code:
        tab_instance.output_text.delete(1.0, tk.END)
        tab_instance.output_text.insert(tk.END, "Vui lòng nhập mã màn hình.")
        return  # return ở đây nếu thiếu mã màn hình

    formatted_date = selected_date.strftime("%Y/%m/%d")
    comment = (
        f"/**\n"
        f" * @since {formatted_date}\n"
        f" * @author {author}\n"
        f" * @implNote {screen_code}\n"
        f" */"
    )
    tab_instance.output_text.delete(1.0, tk.END)
    tab_instance.output_text.insert(tk.END, comment)
