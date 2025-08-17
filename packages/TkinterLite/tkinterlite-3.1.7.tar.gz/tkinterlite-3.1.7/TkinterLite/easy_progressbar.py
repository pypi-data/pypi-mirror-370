import time
import tkinter as tk
from tkinter import ttk

from TkinterLite.easy_auto_window import EasyAutoWindow
from TkinterLite.easy_button import EasyButton


class EasyProgressbar:
    def __init__(self, window, length=200, mode='determinate', increase=1, maximum=100, destroy=False, clear=False,
                 side=tk.TOP, expand=False, fill=tk.NONE, padx=0, pady=0, ipadx=0, ipady=0, layout="pack", row=0,
                 column=0, rowspan=1, columnspan=1, anchor=None):
        self._window = window
        self._length = length
        self._mode = mode
        self._increase = increase
        self._destroy = destroy
        self._clear = clear
        self._increase_v = 1
        self._maximum = maximum
        self._progressbar = ttk.Progressbar(self._window, length=self._length, mode=self._mode)

        if layout == "grid":
            self._progressbar.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                                   padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._progressbar.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                                   anchor=anchor)

    def increase_progressbar(self):
        if self._increase_v < self._maximum:
            self._increase_v += self._increase
            self._progressbar['maximum'] = self._maximum
            self._progressbar['value'] = self._increase_v
            self._progressbar.update()
        if self._increase_v == self._maximum and self._destroy:
            self._progressbar.destroy()
        if self._clear:
            self._progressbar['value'] = 0

    def get_progressbar(self):
        return self._progressbar


if __name__ == "__main__":
    num = 0


    def start_progressbar():
        global num

        if num == 0:
            num += 1
            for _ in range(100):
                progressbar.increase_progressbar()
            time.sleep(0.5)
            window.destroy()


    window = tk.Tk()
    EasyAutoWindow(window, window_title="progressbar", window_width_value=250, window_height_value=100, adjust_x=False,
                   adjust_y=False)

    progressbar = EasyProgressbar(window, length=200, mode='determinate', increase=1, maximum=100, destroy=False,
                                  clear=False)

    EasyButton(window, "Start", expand=tk.YES, width=10, height=1, font_size=12, cmd=start_progressbar, side=tk.LEFT)

    window.mainloop()
