import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyMultiText:
    def __init__(self, window, side=tkinter.TOP, expand=False, fill=tkinter.NONE, padx=0, pady=0, ipadx=0, ipady=0,
                 width=30, height=5, font_size=17, state_str="normal", layout="pack", row=0, column=0, rowspan=1,
                 columnspan=1, anchor=None):
        self._window = window
        self._width = width
        self._height = height
        self._font_size = font_size
        self._state_str = state_str
        f1 = tkinter.Frame(self._window)
        if layout == "grid":
            f1.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                    padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            f1.pack(side=side, expand=expand, fill=fill,
                    padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)

        self._scroll_bar = tkinter.Scrollbar(f1, orient=tkinter.VERTICAL)
        self._scroll_bar.pack(side=tkinter.RIGHT, expand=False, fill=tkinter.Y, pady=2, anchor=anchor)

        self._entry = tkinter.Text(f1, font=("Aria", self._font_size),
                                   width=self._width, height=self._height, state=self._state_str,
                                   yscrollcommand=self._scroll_bar.set)
        self._entry.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._scroll_bar.config(command=self._entry.yview)

    def get_text(self):
        return self._entry

    def get_content(self):
        return self._entry.get("1.0", tkinter.END).strip()


if __name__ == '__main__':
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="MultiText", window_width_value=200, window_height_value=50, adjust_x=False,
                   adjust_y=False)
    text_box = EasyMultiText(root)
    root.mainloop()
