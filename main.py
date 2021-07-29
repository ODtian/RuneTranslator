import os

import webview

from runetranslator.api import Api

api = Api()
api.window = webview.create_window(
    "RuneTranslator",
    f"{os.path.dirname(__file__)}/runetranslator/frontend/index.vue.html",
    js_api=api
)

webview.start(api.start)
