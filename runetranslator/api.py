import asyncio
import json
import logging
import uuid
from importlib import import_module

from .ocr import OCR
from .utils import (
    async_ts,
    get_window,
    get_window_title,
    get_window_visibility,
    parse_config,
    snapshot,
    ts,
)

# import webview


class AsyncApi:
    loop = asyncio.new_event_loop()
    async_result = {}

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if name == "window":
            self.window.closed += self._on_closed

    def _on_closed(self):
        self.loop.call_soon_threadsafe(self.loop.stop)

    def async_get_result(self, result_id):
        is_exc, result = self.async_result.pop(result_id)
        if is_exc:
            raise result
        else:
            return result

    def start(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def call_async(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        result_id = uuid.uuid4().hex

        def callback(f):
            exc = f.exception()
            self.async_result[result_id] = (True, exc) if exc else (False, f.result())
            self.window.evaluate_js(f'resultOk("{result_id}")')

        future.add_done_callback(callback)

        return result_id


class Api(AsyncApi):
    def __init__(self, config_path=None):
        self.config_path = config_path

        self.config = None
        self.ocr = None

        self.outer_window = None
        self.ocr_window = None

        self.api = None
        self.source_lang = None
        self.dest_lang = None

        self.update_config()

    @async_ts
    async def _set_window(self, in_window_mode):
        if in_window_mode:
            if self.outer_window is not None:
                self.outer_window.destroy()
                self.outer_window = None
            await asyncio.sleep(self.config["setWindowWaitingTime"])
        else:
            pass
            # TODO
            # if self.outer_window is None:
            #     self.outer_window = webview.create_window(
            #         "Hello world", "https://baidu.com", frameless=True
            #     )
            # self.outer_window.set_on_top()

        self.ocr_window = get_window()
        return get_window_title(self.ocr_window)

    def set_window(self, in_window_mode=False):
        return self.call_async(self._set_window(in_window_mode=in_window_mode))

    @ts
    def set_api(self, api_class):
        module = import_module(f"runetranslator.translate.{api_class.lower()}")
        cls = getattr(module, api_class.capitalize())
        kwargs = self.config["api"][api_class].get("kwargs", {})
        self.api = cls(**kwargs)

    @ts
    def set_ocr_lang(self, ocr_lang=None):
        self.ocr = OCR(ocr_lang=ocr_lang)

    @ts
    def set_language(self, source_lang=None, dest_lang=None):
        lang_map = self.config["api"][self.api.class_name].get("langMap", {})
        self.source_lang = (
            lang_map.get(source_lang, source_lang) if source_lang else self.source_lang
        )
        self.dest_lang = (
            lang_map.get(dest_lang, dest_lang) if dest_lang else self.dest_lang
        )

    @async_ts
    async def _update(self, lazy):
        if not self.ocr_window or not get_window_visibility(self.ocr_window):
            return []

        im = snapshot(self.ocr_window)

        should_update = await self.ocr.recognize(
            im,
            lazy=lazy,
            **parse_config(
                self.config, keys=("tempSnapPath", "tempOcrPath", "maxSize", "diff")
            ),
        )

        if should_update and self.ocr.paragraphs:
            paragraph_texts = []

            for paragraph in self.ocr.paragraphs:
                if paragraph.text_width() > self.config["paragraphBreak"]:
                    paragraph_texts.append((False, [paragraph.texts["nowrap"]]))
                else:
                    paragraph_texts.append(
                        (True, [line.text for line in paragraph.lines])
                    )

            logging.debug(paragraph_texts)
            input_texts = [text for _, texts in paragraph_texts for text in texts]
            ts_texts = await self.api.translate(
                self.source_lang, self.dest_lang, *input_texts
            )

            for (not_break, texts), paragraph in zip(
                paragraph_texts, self.ocr.paragraphs
            ):
                length = len(texts)

                if not_break:
                    paragraph.texts["translate"] = ts_texts[:length]
                else:
                    paragraph.texts["translate"] = ts_texts[:length][0]

                ts_texts = ts_texts[length:]

        # return self.ocr.lines

    @async_ts
    async def _update_with_compose(self, lazy):
        if not self.ocr_window:
            return ""

        await self._update(lazy=lazy)
        return self.ocr.compose(
            **parse_config(
                self.config.get("font", {}),
                keys=(
                    "fontSize",
                    "fontPath",
                    "fontColor",
                    "fontStrokeColor",
                    "fontStrokeWidth",
                ),
            ),
            **parse_config(
                self.config,
                keys=(
                    "lineBgColor",
                    "lineRectColor",
                    "paragraphRectColor",
                    "outSnapPath",
                ),
            ),
        )

    def update(self, lazy=True, compose=True):
        if compose:
            return self.call_async(self._update_with_compose(lazy=lazy))
        else:
            return self.call_async(self._update(lazy=lazy))

    # TODO
    # def move(self, dx, dy):
    #     self.window.move(self.window.x + dx, self.window.y + dy)

    # def minimize(self):
    #     self.window.minimize()

    # def destroy(self):
    #     self.window.destroy()

    def update_config(self):
        with open(self.config_path, "rb") as f:
            self.config = json.loads(f.read())

    def get_config(self):
        return self.config
