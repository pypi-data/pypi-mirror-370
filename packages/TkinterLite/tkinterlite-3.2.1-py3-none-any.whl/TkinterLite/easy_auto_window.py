import tkinter as tk


class EasyAutoWindow:
    def __init__(self, window, window_y_value=None, window_height_value=None, screen_height=None,
                 window_width_value=None, window_x_value=None, screen_width=None, window_title="window", adjust_x=True,
                 adjust_y=True, minimum_value_x=20, minimum_value_y=20, maximum_value_x=4096, maximum_value_y=4096):
        self._window_y_value = window_y_value
        self._window_height_value = window_height_value
        self._screen_height = screen_height
        self._window_width_value = window_width_value
        self._window_x_value = window_x_value
        self._screen_width = screen_width
        self._window = window
        self._window_title = window_title
        self._adjust_x = adjust_x
        self._adjust_y = adjust_y
        self._minimum_value_x = minimum_value_x
        self._minimum_value_y = minimum_value_y
        self._maximum_value_x = maximum_value_x
        self._maximum_value_y = maximum_value_y

        if self._screen_width is None:
            self._screen_width = self._window.winfo_screenwidth()

        if self._screen_height is None:
            self._screen_height = self._window.winfo_screenheight()

        if self._window_width_value is None:
            self._window_width_value = self._screen_width - 100

        if self._window_height_value is None:
            self._window_height_value = int(self._screen_height * 8.4) // 10

        if self._window_y_value is None:
            self._window_y_value = (self._screen_height - self._window_height_value) // 2 - 20

        if self._window_x_value is None:
            self._window_x_value = (self._screen_width - self._window_width_value) // 2

        self._auto_position()

    def _auto_position(self):

        # 最终设置好位置
        self._window.geometry(
            f"{self._window_width_value}x{self._window_height_value}+{self._window_x_value}+{self._window_y_value}")
        self._window.title(self._window_title)
        self._window.resizable(self._adjust_x, self._adjust_y)
        self._window.minsize(self._minimum_value_x, self._minimum_value_y)
        self._window.maxsize(self._maximum_value_x, self._maximum_value_y)
        return self

    def get_window_width(self):
        return self._window_width_value

    def get_window_height(self):
        return self._window_height_value

    def get_window_x(self):
        return self._window_x_value

    def get_window_y(self):
        return self._window_y_value

    def get_window_title(self):
        return self._window_title


if __name__ == '__main__':
    root = tk.Tk()
    EasyAutoWindow(root, window_title="EasyAutoWindow", window_width_value=400, window_height_value=300, adjust_y=False,
                   adjust_x=False)
    root.mainloop()
