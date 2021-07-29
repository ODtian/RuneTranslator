import json
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .utils import async_ts, create_text_im, im_diff, resize, run_shell, saveb64, ts


class Line:
    def __init__(self, text=None, box=None):
        self.text = text
        self.box = box
        self.left, self.top, self.right, self.bottom = self.box
        self.size = (self.right - self.left, self.bottom - self.top)
        self.ts = ""

    @classmethod
    def from_dict(cls, line):
        words = line["Words"]
        top = min(word["BoundingRect"]["Top"] for word in words)
        left = min(word["BoundingRect"]["Left"] for word in words)
        right = max(word["BoundingRect"]["Right"] for word in words)
        bottom = max(word["BoundingRect"]["Bottom"] for word in words)
        return cls(text=line["Text"], box=(left, top, right, bottom))


class OCR:
    ocr_path = f"{os.path.dirname(__file__)}/script/ocr_from_path.ps1"

    def __init__(
        self,
        ocr_lang=None,
    ):
        self.ocr_lang = ocr_lang
        self.im = None
        self.resized_im = None
        self.lines = []

        # self.im = Image.frombytes("RGB", (1, 1), bytes(3), "raw")

    def get_cmd(self, temp_path):
        return " ".join(
            (
                "powershell",
                self.ocr_path,
                "-Path",
                temp_path,
                "-Lang",
                self.ocr_lang,
            )
        )

    @property
    def line_text(self):
        return [line.text for line in self.lines]

    @async_ts
    async def recognize(
        self, im, lazy=False, temp_path="./temp.bmp", max_size=1000, diff=100
    ):
        if lazy and self.im and im_diff(im, self.im) < diff:
            return False

        self.im = im
        self.resized_im = resize(im, (max_size, max_size))
        self.resized_im.save(temp_path)

        ocr_result = await run_shell(self.get_cmd(temp_path))

        if ocr_result:
            lines = json.loads(ocr_result)
            if isinstance(lines, dict):
                self.lines = [Line.from_dict(lines)]
            else:
                self.lines = [Line.from_dict(line) for line in lines]

        return True

    @ts
    def compose(
        self,
        font_size=16,
        font_path="黑体",
        font_color=(0, 0, 0),
        font_stroke_width=1,
        font_stroke_color=(255, 255, 255),
        bg_color=None,
    ):
        if not self.im:
            return ""

        im = self.resized_im.copy()
        draw = ImageDraw.Draw(im)

        for line in self.lines:
            font = ImageFont.truetype(font_path, font_size)

            if not bg_color:
                upper_im = im.crop(line.box).filter(ImageFilter.BoxBlur(10))
                im.paste(upper_im, line.box)
            else:
                draw.rectangle(line.box, fill=bg_color, outline=bg_color)

            text_im = create_text_im(
                line.ts,
                font=font,
                fill=font_color,
                stroke_width=font_stroke_width,
                stroke_fill=font_stroke_color,
                # ).resize(line.size, Image.ANTIALIAS)
            ).resize(line.size, Image.NEAREST)

            im.paste(text_im, line.box, text_im)

        return saveb64(im)
