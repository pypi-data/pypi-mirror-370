import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyScale:
    def __init__(self, window, from_=0, to=100, orient=tkinter.HORIZONTAL, length=500, variable=None, cmd=None,
                 layout="pack", side=tkinter.TOP, expand=False, fill=tkinter.NONE, padx=0, pady=0, ipadx=0, ipady=0,
                 row=0, column=0, rowspan=1, columnspan=1, anchor=None):
        self._window = window
        self._from = from_
        self._to = to
        self._orient = orient
        self._length = length
        if variable is not None:
            self._variable_v = tkinter.IntVar(value=variable)
        self._cmd = cmd
        self._layout = layout

        slider = tkinter.Scale(self._window, from_=self._from, to=self._to, orient=self._orient, length=self._length,
                               command=self._cmd, variable=self._variable_v)

        if layout == "grid":
            slider.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                        padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            slider.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx,
                        ipady=ipady, anchor=anchor)


if __name__ == '__main__':
    root = tkinter.Tk()

    initial_value = 25

    EasyAutoWindow(root, window_title="Scale", window_width_value=600, window_height_value=200, adjust_x=False,
                   adjust_y=False)

    EasyScale(root, from_=1, to=100, orient=tkinter.HORIZONTAL, length=500, variable=initial_value, expand=tkinter.YES)
    root.mainloop()
