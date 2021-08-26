import json
import logging
import os

import aiofiles
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ImageEnhance
from sklearn.cluster import DBSCAN

# OPTICS
from sklearn.preprocessing import StandardScaler

from .error import ShouldNotUpdateError
from .utils import Powershell, async_ts, create_text_im, im_diff, resize, saveb64, ts

# import re


def build_paragraph(words):
    scaler = StandardScaler().fit_transform([(word.mx, word.my) for word in words])
    db = DBSCAN(eps=0.5, min_samples=3).fit(scaler)
    # db = OPTICS(eps=0.8, min_samples=5).fit(scaler)
    labels = db.labels_
    paragraphs = {
        index: Paragraph.from_words(
            word for group, word in zip(labels, words) if group == index
        )
        for index in set(labels)
    }

    return list(paragraphs.values())


def get_bounding_box(items):
    left = min(item.left for item in items)
    top = min(item.top for item in items)
    right = max(item.right for item in items)
    bottom = max(item.bottom for item in items)
    return (left, top, right, bottom)


class Rect:
    def __init__(self, box):
        self.box = box
        self.left, self.top, self.right, self.bottom = self.box
        self.w = self.right - self.left
        self.h = self.bottom - self.top
        self.size = (self.w, self.h)
        self.x = self.left
        self.y = self.top
        self.mx = (self.left + self.right) / 2
        self.my = (self.top + self.bottom) / 2


class Word(Rect):
    def __init__(self, box, text):
        super().__init__(box)

        self.text = text

    @classmethod
    def from_dict(cls, word):
        rect = word["BoundingRect"]
        box = (rect["Left"], rect["Top"], rect["Right"], rect["Bottom"])
        return cls(box, word["Text"])


class Line(Rect):
    def __init__(self, words):
        super().__init__(get_bounding_box(words))

        self.words = words
        self.text = "".join(word.text for word in self.words)


class Paragraph(Rect):
    def __init__(self, lines):
        super().__init__(get_bounding_box(lines))

        self.lines = lines
        self.text = "\n".join(line.text for line in self.lines)
        self.texts = {"nowrap": "".join(line.text for line in self.lines)}

    def text_width(self):
        return sum(len(line.text) for line in self.lines) / len(self.lines)

    @classmethod
    def from_words(cls, words):
        lines = []

        words = sorted(words, key=lambda word: word.my)
        words_iter = iter(words)
        first = next(words_iter, None)

        if first is None:
            raise ValueError("words is empty")

        temp = [first]
        for rest in words_iter:
            if first.top <= rest.my <= first.bottom:
                temp.append(rest)
            else:
                temp.sort(key=lambda word: word.mx)
                lines.append(Line(temp))
                first = rest
                temp = [rest]

        if temp:
            temp.sort(key=lambda word: word.mx)
            lines.append(Line(temp))

        return cls(lines)

    def iter_text(self, name):
        texts = self.texts[name]
        if isinstance(texts, list):
            yield from zip(self.lines, texts)
        elif isinstance(texts, str):
            ratio = len(texts) / len(self.text)
            start = 0

            for line in self.lines[:-1]:
                length = round(len(line.text) * ratio)
                end = start + length
                yield line, texts[start:end]
                start = end

            if start < len(texts):
                yield self.lines[-1], texts[start:]


# class OcrEngine:
#     async def recognize(self, im, lang):
#         raise NotImplementedError()


# class WinRTOcrEngine(OcrEngine):
#     pass


# class PowershellOcrEngine(OcrEngine):
#     ocr_path = f"{os.path.dirname(__file__)}/script/ocr_from_path.ps1"

#     def __init__(self):
#         self.powershell = Powershell()

#     def get_cmd(self, temp_snap_path, ocr_lang, temp_ocr_path):
#         return " ".join(
#             (
#                 self.ocr_path,
#                 "-Path",
#                 temp_snap_path,
#                 "-Lang",
#                 ocr_lang,
#                 "-OutPath",
#                 temp_ocr_path,
#             )
#         )

#     async def recognize(self, im, lang, temp_snap_path, temp_ocr_path):
#         await self.powershell.execute(self.get_cmd(temp_snap_path, lang, temp_ocr_path))

#         async with aiofiles.open(temp_ocr_path, "rb") as f:
#             result = json.loads(await f.read())
#             logging.debug(result)
#             words = [
#                 Word.from_dict(word)
#                 for line in result["Lines"]
#                 for word in line["Words"]
#             ]
#             return build_paragraph(words)


class OCR:
    ocr_path = f"{os.path.dirname(__file__)}/script/ocr_from_path.ps1"
    # need_trim_lang = ("ja", "zh-Hans")

    def __init__(
        self,
        ocr_lang=None,
    ):
        self.ocr_lang = ocr_lang
        self.im = None
        self.resized_im = None
        self.paragraphs = []
        self.powershell = Powershell()

        # self.im = Image.frombytes("RGB", (1, 1), bytes(3), "raw")

    def get_cmd(self, temp_snap_path, temp_ocr_path):
        return " ".join(
            (
                self.ocr_path,
                "-Path",
                temp_snap_path,
                "-Lang",
                self.ocr_lang,
                "-OutPath",
                temp_ocr_path,
            )
        )

    # @property
    # def line_text(self):
    #     if self.ocr_lang in self.need_trim_lang:
    #         # return [re.sub(r"\s", "", line.text) for line in self.lines]
    #         return []
    #     else:
    #         return [line.text for line in self.lines]

    @async_ts
    async def recognize(
        self,
        im,
        lazy=False,
        temp_snap_path="temp.jpg",
        temp_ocr_path="temp.json",
        max_size=1000,
        diff=100,
    ):
        if lazy and self.im and im_diff(im, self.im) < diff:
            raise ShouldNotUpdateError()

        self.im = im
        self.resized_im = resize(im, (max_size, max_size))

        if os.path.exists(temp_snap_path):
            os.remove(temp_snap_path)
        self.resized_im.save(temp_snap_path)
        # ImageEnhance.Contrast(self.resized_im).enhance(factor=2).save(temp_snap_path)

        await self.powershell.execute(self.get_cmd(temp_snap_path, temp_ocr_path))
        async with aiofiles.open(temp_ocr_path, "rb") as f:
            result = json.loads(await f.read())
            logging.debug(result)
            words = [
                Word.from_dict(word)
                for line in result["Lines"]
                for word in line["Words"]
            ]
            # logging.debug(words)
            self.paragraphs = build_paragraph(words)

    @ts
    def compose(
        self,
        font_size=None,
        font_path="黑体",
        font_color=(0, 0, 0),
        font_stroke_width=1,
        font_stroke_color=(255, 255, 255),
        line_bg_color=None,
        line_rect_color=None,
        paragraph_rect_color=None,
        out_snap_path=None,
    ):
        if not self.im:
            return ""

        im = self.resized_im.copy()
        draw = ImageDraw.Draw(im)

        for paragraph in self.paragraphs:

            if paragraph_rect_color:
                draw.rectangle(
                    paragraph.box,
                    fill=None,
                    outline=paragraph_rect_color,
                    width=font_stroke_width,
                )

            for line, text in paragraph.iter_text("translate"):
                font = ImageFont.truetype(font_path, font_size or line.h)

                if line_bg_color:
                    draw.rectangle(line.box, fill=line_bg_color, outline=line_bg_color)
                else:
                    upper_im = im.crop(line.box).filter(ImageFilter.BoxBlur(20))
                    im.paste(upper_im, line.box)

                if line_rect_color:
                    draw.rectangle(
                        line.box,
                        fill=None,
                        outline=line_rect_color,
                        width=font_stroke_width,
                    )

                text_im = create_text_im(
                    text,
                    font=font,
                    fill=font_color,
                    stroke_width=font_stroke_width,
                    stroke_fill=font_stroke_color,
                    # ).resize(line.size, Image.ANTIALIAS)
                ).resize(line.size, Image.NEAREST)
                im.paste(text_im, line.box, text_im)

        if out_snap_path:
            if os.path.exists(out_snap_path):
                os.remove(out_snap_path)
            im.save(out_snap_path)
            return ""
        else:
            return saveb64(im)
