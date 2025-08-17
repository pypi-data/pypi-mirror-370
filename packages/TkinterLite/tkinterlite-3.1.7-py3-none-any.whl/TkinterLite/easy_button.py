import tkinter
import tkinter.font as tkFont
from tkinter import Button

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyButton:

    def __init__(self, window, text, cmd="", side=tkinter.TOP, expand=False, fill=tkinter.NONE, padx=0, pady=0, ipadx=0,
                 ipady=0, width=17, height=8, font_size=17, layout="pack", anchor=None, row=0, column=0, rowspan=1,
                 columnspan=1, auto_resize_font=False, value=None, sticky="nsew"):
        self._window = window
        self._text = text
        self._command = cmd
        self._width = width
        self._height = height
        self._font_size = font_size
        self._value = value
        self._button = Button(self._window, text=self._text, font=("Arial", self._font_size),
                              command=self._command, relief="raised", width=self._width,
                              height=self._height)

        if auto_resize_font:
            self._button.bind('<Configure>', lambda event, value=self._value: self.on_button_resize(event, value))

        if layout == "grid":
            self._button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky=sticky,
                              padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._button.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                              anchor=anchor)

    def get_button(self):
        return self._button

    def on_button_resize(self, event, value):
        new_width = event.width
        new_height = event.height

        new_font_size = min(new_width, new_height) // value

        button_font = tkFont.Font(size=new_font_size)
        self._button['font'] = button_font


if __name__ == "__main__":
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="Button", window_width_value=150, window_height_value=80, adjust_x=True,
                   adjust_y=True)

    EasyButton(root, "Button", expand=tkinter.YES, fill=tkinter.BOTH, auto_resize_font=True, value=4)

    root.mainloop()
