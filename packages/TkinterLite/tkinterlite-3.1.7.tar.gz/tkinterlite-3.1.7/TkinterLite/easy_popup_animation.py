import random
import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow
from TkinterLite.easy_fade_animation import fade_out, fade_in
from TkinterLite.easy_label import EasyLabel


def close_window(event=None):
    fade_out(root)


def center_window(root):
    width = root.winfo_width()
    height = root.winfo_height()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2 - 20

    root.focus_set()
    root.lift()
    root.geometry(f"+{x}+{y}")


def cubic_easing(t):
    if t < 0.5:
        return 4 * t * t * t
    t = t - 1
    return 4 * t * t * t + 1


def animate_resize_window(root, target_width, target_height, steps=20, way='ordinary', center=False, update_interval=5):
    root.update()

    if center:
        center_window(root)

    # 获取当前窗口大小和位置
    geometry = root.geometry()
    current_width = int(geometry.split('x')[0])
    rest = geometry.split('x')[1].split('+')
    current_height = int(rest[0])
    current_x = int(rest[1])
    current_y = int(rest[2])

    for i in range(steps + 1):
        t = i / steps
        eased_t = cubic_easing(t) if way == 'magic' else t

        new_width = current_width + (target_width - current_width) * eased_t
        new_height = current_height + (target_height - current_height) * eased_t
        new_x = current_x - (target_width - current_width) * eased_t / 2
        new_y = current_y - (target_height - current_height) * eased_t / 2

        root.geometry(f"{int(new_width)}x{int(new_height)}+{int(new_x)}+{int(new_y)}")

        if i % update_interval == 0:  # 只有在每update_interval步才调用root.update()
            root.update()
    if center:
        center_window(root)


if __name__ == '__main__':
    root = tkinter.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    random_x = random.randint(600, screen_width - 600)
    random_y = random.randint(400, screen_height - 400)

    EasyAutoWindow(root, window_title="动画演示", window_width_value=1, window_height_value=1, adjust_x=False,
                   adjust_y=False, window_x_value=random_x, window_y_value=random_y)

    EasyLabel(root, text="动画演示", expand=True, font_size=100)

    fade_in(root, ms=2)
    animate_resize_window(root, 1000, 600, 100, "ordinary", False, 5)

    root.protocol("WM_DELETE_WINDOW", close_window)
    root.mainloop()
