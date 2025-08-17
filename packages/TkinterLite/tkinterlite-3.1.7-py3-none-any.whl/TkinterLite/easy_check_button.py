import tkinter


class EasyCheckButton:
    def __init__(self, window, text=None, set_text_list=None, master_win=None, cmd=None, side=tkinter.TOP, expand=False,
                 fill=tkinter.NONE, padx=0, pady=0, ipadx=0, ipady=0, layout="pack", row=0, column=0, rowspan=1,
                 columnspan=1, anchor=tkinter.W):
        if text is None:
            text = ["选项1", "选项2", "选项3"]
        self._window = window
        self._text = text
        self._set = set_text_list
        self._cmd = cmd
        self._anchor = anchor
        self._vars = {}
        for options in self._text:
            var = tkinter.IntVar(master_win)
            check_button = tkinter.Checkbutton(self._window, text=options, variable=var, command=self._cmd)
            self._vars[options] = var
            if options in self._set:
                check_button.select()
            if layout == "grid":
                check_button.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                                  padx=padx, pady=pady, ipadx=ipadx, ipady=ipady)
            else:
                check_button.pack(side=side, anchor=anchor, expand=expand, fill=fill, padx=padx, pady=pady,
                                  ipadx=ipadx,
                                  ipady=ipady)

    def get_set(self):
        selected_options = []
        for option, var in self._vars.items():
            if var.get() == 1:
                selected_options.append(option)
        return selected_options

    def get_vars(self):
        return self._vars

    def set(self, values):
        for option, var in self._vars.items():
            if option in values:
                var.set(1)
            else:
                var.set(0)


if __name__ == "__main__":
    def on_button_click():
        print(f"after selected_list={fruit_check_button.get_set()}")
        fruit_check_button.set(["苹果(默认)", "橙子(默认)"])


    def on_checkbutton_click():
        print(f"Checkbutton clicked, current selected_list={fruit_check_button.get_set()}")


    root = tkinter.Tk()
    root.title("示例")

    fruit_check_button = EasyCheckButton(root,
                                         text=["苹果(默认)", "香蕉(默认)", "橙子(默认)", "葡萄", "梨子(默认)", "榴莲",
                                               "荔枝", "草莓", "柚子", "樱桃", "杏子", "菠萝", "西瓜"],
                                         set_text_list=["梨子(默认)", "香蕉(默认)"],
                                         cmd=on_checkbutton_click,
                                         expand=tkinter.YES)
    print(f"before selected_list={fruit_check_button.get_set()}")

    button = tkinter.Button(root, text="改变选中值", command=on_button_click)
    button.pack()

    root.mainloop()
