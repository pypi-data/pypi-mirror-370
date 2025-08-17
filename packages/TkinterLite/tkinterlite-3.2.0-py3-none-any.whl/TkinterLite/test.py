import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow
from TkinterLite.easy_button import EasyButton

root = tkinter.Tk()
EasyAutoWindow(root, window_title="Button", window_width_value=300, window_height_value=80, adjust_x=True,
               adjust_y=True)

EasyButton(root, text="退出", fill=tkinter.BOTH, expand=True, side=tkinter.LEFT, height=2, auto_resize_font=True,
           value=3)

EasyButton(root, text="设置", fill=tkinter.BOTH, expand=True, side=tkinter.LEFT, height=2, auto_resize_font=True,
           value=3)

EasyButton(root, text="使用方法", fill=tkinter.BOTH, expand=True, side=tkinter.LEFT, height=2,
           auto_resize_font=True, value=3)

root.mainloop()
