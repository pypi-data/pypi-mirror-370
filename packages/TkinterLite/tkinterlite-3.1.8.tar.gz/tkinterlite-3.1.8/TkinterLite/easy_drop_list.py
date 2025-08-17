import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow


class EasyDropList:
    def __init__(self, window, options=None, default=1, cmd=None, side=tkinter.TOP, expand=False, fill=tkinter.NONE,
                 padx=0, pady=0, ipadx=0, ipady=0, width=17, height=8, font_size=17, layout="pack", row=0, column=0,
                 rowspan=1, columnspan=1, anchor=None):
        if options is None:
            options = ['选项1', '选项2', '选项3']
        self._window = window
        self._options = options
        self._command = cmd
        self._width = width
        self._height = height
        self._font_size = font_size
        self._default = default - 1

        self._selected_option = tkinter.StringVar(self._window)
        self._selected_option.set(self._options[self._default])  # 默认选中第一个选项
        self._selected_option.trace("w", self._command)  # 在选项改变时调用 cmd 函数

        self._combo = tkinter.OptionMenu(self._window, self._selected_option, *self._options)
        if layout == "grid":
            self._combo.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                             padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
        else:
            self._combo.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, ipadx=ipadx, ipady=ipady,
                             anchor=anchor)

    def get_combo(self):
        return self._combo

    def get_combo_value(self):
        return self._selected_option.get()

    def set_combo_value(self, value):
        self._selected_option.set(value)


if __name__ == '__main__':
    root = tkinter.Tk()
    EasyAutoWindow(root, window_title="DropList", window_width_value=200, window_height_value=50, adjust_x=False,
                   adjust_y=False)


    def on_option_change(*args):
        index, mode, name = args
        print("Index:", index)
        print("Mode:", mode)
        print("Name:", name)
        print("Option changed to:", drop_list.get_combo_value())


    drop_list = EasyDropList(root, options=['选项1', '选项2', '选项3'], default=2, cmd=on_option_change,
                             expand=tkinter.YES)


    def change_value():
        drop_list.set_combo_value('选项3')


    button = tkinter.Button(root, text="改变值", command=change_value)
    button.pack()

    root.mainloop()
