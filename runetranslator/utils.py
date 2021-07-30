import asyncio
import base64
import ctypes
import ctypes.wintypes
import functools
import io
import logging
import math
import operator
import time

import win32gui
from PIL import Image, ImageDraw, ImageGrab


def async_ts(func):
    async def inner(*args, **kwargs):
        t1 = time.time()
        result = await func(*args, **kwargs)
        t2 = time.time()
        logging.debug(f"{func.__name__} use {t2 - t1}s")
        return result

    return inner


def ts(func):
    import time

    def inner(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        logging.debug(f"{func.__name__} use {t2 - t1}s")
        return result

    return inner


def get_window():
    return win32gui.GetForegroundWindow()


@ts
def im_diff(im1, im2):
    h1 = im1.histogram()
    h2 = im2.histogram()

    result = math.sqrt(
        functools.reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1)
    )

    return result


@ts
def saveb64(im):
    buffered = io.BytesIO()
    im.save(buffered, format="jpeg")
    b64 = base64.b64encode(buffered.getvalue())
    return b64.decode()


def get_current_size(handle):
    rect = ctypes.wintypes.RECT()
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    ctypes.windll.dwmapi.DwmGetWindowAttribute(
        ctypes.wintypes.HWND(handle),
        ctypes.wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    return (rect.left, rect.top, rect.right, rect.bottom)


def get_window_title(handle):
    return win32gui.GetWindowText(handle)


def get_window_visibility(handle):
    return win32gui.IsWindowVisible(handle) and not win32gui.IsIconic(handle)


@ts
def snapshot(handle):
    return ImageGrab.grab(get_current_size(handle))


class Powershell:
    def __init__(self):
        self.popen = None

    async def create_process(self):
        self.popen = await asyncio.create_subprocess_shell(
            "powershell -NoLogo",
            limit=1024 * 128,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

    @async_ts
    async def excute(self, cmd):
        logging.debug(cmd)

        if not self.popen:
            await self.create_process()

        self.popen.stdin.write(f"{cmd}\n".encode())
        await self.popen.stdin.drain()
        await self.popen.stdout.readline()
        result = await self.popen.stdout.readline()
        logging.debug(result[:100] + b"\n ... \n" + result[100:])
        return result.rstrip().decode()


@ts
def resize(im, size):
    w, h = im.size
    w_box, h_box = size
    f1 = 1 * w_box / w
    f2 = 1 * h_box / h
    factor = min(f1, f2)
    width = int(w * factor)
    height = int(h * factor)
    # return im.resize((width, height), Image.ANTIALIAS)
    return im.resize((width, height), Image.NEAREST)


def create_text_im(text, font, stroke_width, *args, **kwargs):
    size = ImageDraw.Draw(Image.new("RGBA", (1, 1), (0, 0, 0, 0))).textsize(
        text, font, stroke_width=stroke_width
    )

    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).text(
        (stroke_width, stroke_width),
        text,
        font=font,
        stroke_width=stroke_width,
        *args,
        **kwargs,
    )

    return im


def underline_to_hump(text):
    return "".join(
        f"_{char}" if char.isupper() and i != 0 else char for i, char in enumerate(text)
    ).lower()


def parse_config(config, keys=()):
    return {underline_to_hump(k): v for k, v in config.items() if k in keys and v}
