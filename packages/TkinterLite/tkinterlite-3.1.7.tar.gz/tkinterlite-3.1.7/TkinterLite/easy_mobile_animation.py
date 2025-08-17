import random
import tkinter

from TkinterLite.easy_auto_window import EasyAutoWindow
from TkinterLite.easy_fade_animation import fade_in, fade_out
from TkinterLite.easy_label import EasyLabel

num = 0
mouse_in_window = False


def cubic_bezier(t, p0, p1, p2, p3):
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def cubic_easing(t):
    if t < 0.5:
        return 4 * t * t * t
    t = t - 1
    return 4 * t * t * t + 1


def move_window_to(window, target_x, target_y, steps=200, amplitude=0.5, way='ordinary'):
    global num

    if num == 0:
        num += 1
        window.update_idletasks()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        geometry = window.geometry().split('+')
        current_x = int(geometry[1])
        current_y = int(geometry[2])

        # 随机生成控制点，根据amplitude参数调整生成范围
        control_x1 = random.randint(int(current_x - amplitude * screen_width),
                                    int(current_x + amplitude * screen_width))
        control_y1 = random.randint(int(current_y - amplitude * screen_height),
                                    int(current_y + amplitude * screen_height))
        control_x2 = random.randint(int(target_x - amplitude * screen_width), int(target_x + amplitude * screen_width))
        control_y2 = random.randint(int(target_y - amplitude * screen_height),
                                    int(target_y + amplitude * screen_height))

        for i in range(steps + 1):
            t = i / steps
            eased_t = cubic_easing(t) if way == 'magic' else t

            x = int(cubic_bezier(eased_t, current_x, control_x1, control_x2, target_x))
            y = int(cubic_bezier(eased_t, current_y, control_y1, control_y2, target_y))

            window.geometry(f"+{x}+{y}")
            window.update()

        window.geometry(f"+{target_x}+{target_y}")
        num -= 1


def quit_window(event=None):
    fade_out(root)


def on_mouse_enter(event):
    global mouse_in_window
    mouse_in_window = True


def on_mouse_leave(event):
    global mouse_in_window
    mouse_in_window = False


def on_mouse_move(event):
    if mouse_in_window:
        screen_width = event.widget.winfo_screenwidth()
        screen_height = event.widget.winfo_screenheight()

        target_x = random.randint(400, screen_width - 400)
        target_y = random.randint(400, screen_height - 400)

        move_window_to(event.widget.winfo_toplevel(), target_x, target_y, steps=1000, amplitude=0.05, way='ordinary')


if __name__ == '__main__':
    root = tkinter.Tk()
    root.geometry("200x200")

    EasyAutoWindow(root, window_title="会跑的窗口", window_width_value=280, window_height_value=100, adjust_x=False,
                   adjust_y=False)

    EasyLabel(root, text="请将鼠标移动到窗口内", expand=tkinter.YES, fill=tkinter.BOTH)
    EasyLabel(root, text="按下q键退出", expand=tkinter.YES, fill=tkinter.BOTH)

    root.bind('<Enter>', on_mouse_enter)
    root.bind('<Leave>', on_mouse_leave)
    root.bind('<Motion>', on_mouse_move)
    root.bind('<q>', quit_window)
    root.bind('<Q>', quit_window)
    root.protocol("WM_DELETE_WINDOW", quit_window)

    for child in root.winfo_children():
        child.bind('<Enter>', on_mouse_enter)
        child.bind('<Leave>', on_mouse_leave)
        child.bind('<Motion>', on_mouse_move)

    fade_in(root)

    root.mainloop()
