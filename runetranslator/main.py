import os

import webview

from ocr.api import Api

api = Api()
api.window = webview.create_window(
    "RuneOCR", f"{os.path.dirname(__file__)}/ocr/frontend/index.vue.html", js_api=api
)

webview.start(api.start, debug=False)
