import argparse
import logging
import os

import webview

from runetranslator.api import Api

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
        "-D",
        "--debug",
        default=False,
        action="store_true",
        help="debug mode.",
    )
    args, _ = parser.parse_known_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    api = Api(args.conf)
    api.window = webview.create_window(
        "RuneTranslator",
        f"{os.path.dirname(__file__) or '.'}/runetranslator/frontend/index.vue.html",
        js_api=api,
    )

    webview.start(api.start, debug=True)
