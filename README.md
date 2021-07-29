# RuneTranslator

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/asset/老婆🐟.gif)

![](https://img.shields.io/github/stars/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/forks/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/issues/ODtian/RuneTranslator.svg)

## 特性

-   基于 .NET Windows.Media.OCR 的 OCR 引擎，系统自带（调用 powershell，没想到吧）；
-   基于 EdgeChromium Webview 构建的 GUI，系统自带，减小体积；
-   支持渲染文本到原来的位置，不丢失位置信息；
-   简单的架构，欢迎 PR;
-   ...

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/asset/flow.svg)

## 使用方法

### 安装依赖

```
pip install -r requirements.txt
```

什么？你说找不到 requirements.txt？先把包拉下来再说啊！

### 运行

```
python main.py
```

注：使用百度翻译 api 前先去填 key 和 secret

## 配置

```javascript
{
    "tempPath": "./temp.jpg",
    "maxSize": 2000,
    "font": {
        "fontPath": "填写你的字体文件",
        "fontColor": "#ffffff",
        "fontSize": null,
        "fontStrokeWidth": 2,
        "fontStrokeColor": "#000000"
    },
    "bgColor": null,
    "bgRectColor": "#ff0000",
    "setWindowWaitingTime": 1,
    "updateInterval": 1,
    "api": {
        "baidu": {
            "name": "百度翻译",
            "kwargs": {
                "app_id": "填写你的参数",
                "secret_key": "填写你的参数"
            }
        },
        "bing": {
            "name": "必应翻译",
            "lang_map": {
                "zh": "zh-Hans",
                "jp": "ja"
            }
        },
        "youdao": {
            "name": "有道翻译",
            "lang_map": {
                "zh": "zh-CHS",
                "jp": "ja"
            }
        },
        "direct": {
            "name": "不翻译"
        }
    },
    "lang": [
        {
            "name": "简体中文",
            "value": "zh"
        },
        {
            "name": "英文",
            "value": "en"
        },
        {
            "name": "日文",
            "value": "jp"
        }
    ],
    "ocrLang": [
        {
            "name": "中文",
            "value": "zh-Hans-CN"
        },
        {
            "name": "英语",
            "value": "en"
        },
        {
            "name": "日语",
            "value": "ja"
        }
    ]
}
{
    "tempPath": "截图临时文件存储位置",
    "maxSize": 5000, // 截图缩放大小，更高的尺寸可以提高准确率
    "font": {
        "fontPath": "填写你的字体文件",
        "fontColor": "#ffffff", // 渲染文本颜色
        "fontSize": null, // 渲染文本大小，为空则自动判断大小
        "fontStrokeWidth": 2, // 渲染文本描边大小
        "fontStrokeColor": "#000000" // 渲染文本描边颜色
    },
    "bgColor": null, // 渲染文本背景颜色，为空则为原背景模糊
    "bgRectColor": "#ff0000", // OCR识别边框的颜色，没有则不上色
    "setWindowWaitingTime": 1, // 设置顶置窗口等待的时间
    "updateInterval": 1, // 自动刷新间隔
    "api": {
        "baidu": { // 翻译API的模块名，也是类名
            "name": "百度翻译",
            "kwargs": { // 实例化API的参数，没有可以不写
                "app_id": "填写你的参数",
                "secret_key": "填写你的参数"
            }
        },
        "bing": {
            "name": "必应翻译",
            "lang_map": { //  API的语言代码别名，没有别名则无需填
                "zh": "zh-Hans",
                "jp": "ja"
            }
        },
        "youdao": {
        // ...
        },
        "direct": {
        // ...
        }
    },
    "lang": [ // 语言
        {
            "name": "简体中文",
            "value": "zh" // 语言代码
        },
        {
            "name": "英文",
            "value": "en"
        },
        {
            "name": "日文",
            "value": "jp"
        }
    ],
    "ocrLang": [
        {
            "name": "中文",
            "value": "zh-Hans-CN"
            // OCR引擎的语言代码
            // 可以运行RuneTranslator/runetranslator/script/check_languages.ps1查看支持的语言
            // 也可以在Windows设置里添加系统语言
        }
    ]
}
```

### End

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/asset/娇羞🐟.webp)
