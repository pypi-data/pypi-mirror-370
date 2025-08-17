import tkinter as tk


def auto_size(window, window_width_value=None, window_height_value=None):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    if window_width_value is None:
        window_width_value = screen_width - 100
    if window_height_value is None:
        window_height_value = int(screen_height * 8.4) // 10

    window_x_value = (screen_width - window_width_value) // 2
    window_y_value = (screen_height - window_height_value) // 2 - 20

    return window_width_value, window_height_value, window_x_value, window_y_value


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Auto Size')
    window_width_value, window_height_value, window_x_value, window_y_value = auto_size(root, 800, 600)
    root.geometry(f'{window_width_value}x{window_height_value}+{window_x_value}+{window_y_value}')
    root.resizable(False, False)
    root.mainloop()
