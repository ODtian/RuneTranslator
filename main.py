import os

import webview

from runetranslator.api import Api
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-C",
        "--conf",
        default="./config.json",
        type=str,
        help="Path to the config file.",
    )

    parser.add_argument(
        "-C",
        "--conf",
        default="./config.json",
        type=str,
        help="Path to the config file.",
    )
    
    conf_path = parser.parse_known_args()[0].conf

    api = Api(conf_path)
    api.window = webview.create_window(
        "RuneTranslator",
        f"{os.path.dirname(__file__) or '.'}/runetranslator/frontend/index.vue.html",
        js_api=api,
    )

    webview.start(api.start, debug=True)
