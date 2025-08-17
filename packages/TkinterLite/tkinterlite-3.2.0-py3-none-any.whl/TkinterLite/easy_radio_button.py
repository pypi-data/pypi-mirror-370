import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyRadioButton:
    def __init__(self, window, text=None, int_var=None, cmd=None, side=tkinter.TOP, expand=False, fill=tkinter.NONE,
                 padx=0, pady=0, ipadx=0, ipady=0, width=17, height=8, font_size=17, layout="pack", row=0, column=0,
                 rowspan=1, columnspan=1, anchor=None):
        if text is None:
            text = ['选项1', '选项2', '选项3']
        self._window = window
        self._options = text
        self._command = cmd
        self._width = width
        self._height = height
        self._font_size = font_size
        self._int_var = int_var
        self._radio_buttons = []
        for i, option in enumerate(self._options, start=1):
            radio_button = tkinter.Radiobutton(self._window, text=option, variable=self._int_var, value=i)
            if layout == "grid":
                radio_button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                                  padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
            else:
                radio_button.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx,
                                  ipady=ipady, anchor=anchor)
            self._radio_buttons.append(radio_button)

    def get_radio_buttons(self):
        return self._radio_buttons

    def get_radio_button_value(self):
        return self._int_var.get()


if __name__ == '__main__':
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="RadioButton", window_width_value=200, window_height_value=100, adjust_x=False,
                   adjust_y=False)
    var = tkinter.IntVar()
    var.set(1)
    EasyRadioButton(root, int_var=var, expand=tkinter.YES)
    root.mainloop()
