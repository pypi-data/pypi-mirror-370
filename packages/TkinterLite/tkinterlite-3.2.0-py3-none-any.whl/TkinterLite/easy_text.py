import tkinter
from tkinter import Entry

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyText:
    def __init__(self, window, side=tkinter.TOP, expand=False, fill=tkinter.NONE, padx=0, pady=0, ipadx=0, ipady=0,
                 width=30, font_size=17, state_str="normal", layout="pack", row=0, column=0, rowspan=1, columnspan=1,
                 anchor=None):
        self._window = window
        self._width = width
        self._font_size = font_size
        self._state_str = state_str
        self._entry = Entry(self._window, font=("Aria", self._font_size), width=self._width, state=self._state_str)
        if layout == "grid":
            self._entry.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                             padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._entry.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                             anchor=anchor)

    def get_text(self):
        return self._entry


if __name__ == "__main__":
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="Text", window_width_value=500, window_height_value=200, adjust_x=False,
                   adjust_y=False)
    text = EasyText(root, expand=tkinter.YES)
    text.get_text().insert(tkinter.END, "Text")
    root.mainloop()
