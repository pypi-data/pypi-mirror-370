import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasySpinbox:
    def __init__(self, window, from_, to, state="readonly", width=10, expand=False, side=tkinter.TOP, fill=tkinter.NONE,
                 padx=0, pady=0, ipadx=0, ipady=0, layout="pack", row=0, column=0, rowspan=1, columnspan=1,
                 font=("Arial", 12), increment=1, cmd=None, anchor=None):
        self._window = window
        self._from_ = from_
        self._to = to
        self._spinbox = tkinter.Spinbox(self._window, from_=self._from_, to=self._to, state=state, width=width,
                                        font=font, increment=increment, command=cmd)
        if layout == "grid":
            self._spinbox.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                               padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._spinbox.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                               anchor=anchor)

    def get_spinbox(self):
        return self._spinbox

    def get_set(self):
        return self._spinbox.get()


if __name__ == '__main__':
    window = tkinter.Tk()
    EasyAutoWindow(window, window_title="Spinbox", window_width_value=290, window_height_value=100, adjust_x=False,
                   adjust_y=False)


    def on_value_change():
        print("Value changed:", spinbox.get_set())


    spinbox = EasySpinbox(window, from_=0, to=5, state='readonly', expand=True, cmd=on_value_change)
    window.mainloop()
