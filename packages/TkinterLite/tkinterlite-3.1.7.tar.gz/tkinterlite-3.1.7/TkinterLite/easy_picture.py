import os
import tkinter

from PIL import Image, ImageTk


class EasyPicture:
    def __init__(self, window, img_path, size=(350, 350), side=tkinter.RIGHT, expand=False, fill=tkinter.NONE,
                 padx=0, pady=0, layout="pack", row=0, column=0, rowspan=1, columnspan=1,
                 keep_aspect_ratio=True, auto_resize=False, **kwargs):
        self._window = window
        self._img_path = img_path
        self._size = size
        self._keep_aspect_ratio = keep_aspect_ratio
        self._auto_resize = auto_resize
        self._kwargs = kwargs

        if not os.path.isfile(self._img_path):
            raise FileNotFoundError(f"Image file not found: {self._img_path}")

        # 加载原始图片
        self._orig_img = Image.open(self._img_path)
        self._photo = None  # 占位

        # 创建Label
        self._label = tkinter.Label(self._window)
        self._label.image = None  # 占位

        # 初始显示
        self._update_image(self._size)

        # 布局
        if layout == "grid":
            self._label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan, sticky="nsew",
                             padx=padx, pady=pady, **self._kwargs)
        else:
            self._label.pack(side=side, expand=expand, fill=fill, padx=padx, pady=pady, **self._kwargs)

        # 自动调整大小
        if self._auto_resize:
            self._label.bind('<Configure>', self._on_resize)

    def _parse_target_size(self, size, orig_size):
        """
        支持 ("auto", 高度) 或 (宽度, "auto")，返回最终缩放目标尺寸
        """
        orig_w, orig_h = orig_size
        w, h = size

        def as_int(val):
            if isinstance(val, str) and val.strip().lower() == "auto":
                return "auto"
            try:
                return int(val)
            except:
                raise ValueError(f"Invalid size value: {val}")

        w = as_int(w)
        h = as_int(h)

        # 两边都给定
        if w != "auto" and h != "auto":
            return (w, h)
        # 只给定宽度
        if w != "auto" and h == "auto":
            scale = w / orig_w
            new_w = w
            new_h = max(1, int(orig_h * scale))
            return (new_w, new_h)
        # 只给定高度
        if w == "auto" and h != "auto":
            scale = h / orig_h
            new_h = h
            new_w = max(1, int(orig_w * scale))
            return (new_w, new_h)
        # 都是 auto，返回原始尺寸
        return (orig_w, orig_h)

    def _update_image(self, size):
        """根据目标size和锁定比例设置图片"""
        img = self._orig_img
        if self._keep_aspect_ratio:
            actual_size = self._parse_target_size(size, img.size)
            img = img.resize(actual_size, Image.LANCZOS)
        else:
            # 原逻辑
            # 防止传了字符串
            actual_size = (int(size[0]), int(size[1]))
            img = img.resize(actual_size, Image.LANCZOS)
        self._photo = ImageTk.PhotoImage(img)
        self._label.config(image=self._photo)
        self._label.image = self._photo  # 防止被回收

    def _on_resize(self, event):
        """容器大小变化时自动调整图片（auto_resize 模式下）"""
        new_size = (event.width, event.height)
        # 在自动调整时，两边尺寸都来自事件，所以不用'auto'
        self._update_image(new_size)

    def get_label(self):
        return self._label
