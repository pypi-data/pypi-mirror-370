import tkinter
from tkinter import Label

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyLabel:
    def __init__(self, window, text, side=tkinter.TOP, expand=False, fill=tkinter.NONE, padx=0, pady=0, ipadx=0,
                 ipady=0, font_size=17, layout="pack", row=0, column=0, rowspan=1, columnspan=1, text_color="black",
                 anchor=None):
        self._window = window
        self._text = text
        self._font_size = font_size

        self._label = Label(window, text=self._text, font=("Arial", self._font_size), fg=text_color)
        if layout == "grid":
            self._label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                             padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._label.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                             anchor=anchor)

    def set_text(self, text):
        self._text = text
        self._label.config(text=text)

    def get_label(self):
        return self._label


if __name__ == "__main__":
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="Label", window_width_value=200, window_height_value=100, adjust_x=False,
                   adjust_y=False)
    l1 = EasyLabel(root, text="Label", expand=tkinter.YES)


    def change_text():
        l1.set_text("你好，世界！")


    btn = tkinter.Button(root, text="切换", command=change_text)
    btn.pack()

    root.mainloop()
