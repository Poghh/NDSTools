import tkinter as tk


def generate_comment(tab_instance):
    author = tab_instance.author_entry.get().strip()
    screen_code = tab_instance.screen_code_entry.get().strip()
    selected_date = tab_instance.date_entry.get_date()

    if not author:
        tab_instance.output_text.delete(1.0, tk.END)
        tab_instance.output_text.insert(tk.END, "Vui lòng nhập tên tác giả.")
        return

    if not screen_code:
        tab_instance.output_text.delete(1.0, tk.END)
        tab_instance.output_text.insert(tk.END, "Vui lòng nhập mã màn hình.")
        return

    formatted_date = selected_date.strftime("%Y/%m/%d")

    comment_in_head_class = (
        f"/**\n"
        f" * @since {formatted_date}\n"
        f" * @author {author}\n"
        f" * @implNote {screen_code}\n"
        f" */"
    )

    comment_in_dto_class = (
        f"/**\n"
        f" * @since {formatted_date}\n"
        f" * @author {author}\n"
        f" * @implNote {screen_code}の入力Dto\n"
        f" */"
    )

    comment_out_dto_class = (
        f"/**\n"
        f" * @since {formatted_date}\n"
        f" * @author {author}\n"
        f" * @implNote {screen_code}の出力Dto\n"
        f" */"
    )

    # Hiển thị cả 3 comment vào output
    tab_instance.output_text.delete(1.0, tk.END)
    tab_instance.output_text.insert(tk.END, "【COMMENT ĐẦU CLASS】\n")
    tab_instance.output_text.insert(tk.END, comment_in_head_class + "\n\n")

    tab_instance.output_text.insert(tk.END, "【COMMENT ĐẦU CLASS IN DTO】\n")
    tab_instance.output_text.insert(tk.END, comment_in_dto_class + "\n\n")

    tab_instance.output_text.insert(tk.END, "【COMMENT ĐẦU CLASS OUT DTO】\n")
    tab_instance.output_text.insert(tk.END, comment_out_dto_class + "\n")
