# RuneTranslator

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/asset/老婆🐟.gif)

![](https://img.shields.io/github/stars/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/forks/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/issues/ODtian/RuneTranslator.svg)

## 特性
webview2问题太多了，正好pyqt6也出了好几个月了，打算用pyqt6重构一下

powershell调用ocr接口在有的用户上无法使用，计划通过微软官方的winrt python库扩展兼容性，出乎意料的是powershell调用更快一些

目前打包后还有些问题，请先直接使用 python 运行

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

### 参数

```
usage: main.py [-h] [-C CONF] [-D]

可选参数:
  -h, --help            show this help message and exit
  -C CONF, --conf CONF  配置文件路径.
  -D, --debug           Debug模式.
```

注：使用百度翻译 api 前先去填 key 和 secret

## 配置

```javascript
{
    "tempSnapPath": "截图临时文件存储位置",
    "tempOcrPath": "OCR结果临时存放的位置",
    "outSnapPath": "如果不想使用自带的垃圾图片阅览器，请填写这个参数，然后使用系统图片阅览器",
    "paragraphBreak": 10, // 识别段落的阈值，一行文本长度如果小于这个值，那么多行文本全部按照单行处理
    "maxSize": 2000, // 截图缩放大小，更高的尺寸可以提高准确率
    "font": {
        "fontPath": "填写你的字体文件",
        "fontColor": "#ffffff", // 渲染文本颜色
        "fontSize": null, // 渲染文本大小，为空则自动判断大小
        "fontStrokeWidth": 2, // 渲染文本描边大小
        "fontStrokeColor": "#000000" // 渲染文本描边颜色
    },
    "lineBgColor": null,// 渲染文本背景颜色，为空则为原背景模糊
    "lineRectColor": null,// OCR识别边框的颜色，没有则不上色
    "paragraphRectColor": null, // OCR识别段落的颜色，没有不上色
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
            // 运行 RuneTranslator/runetranslator/script/check_languages.ps1 查看支持的语言
            // 也可以在Windows设置里添加系统语言
        }
    ]
}
```

### End

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/asset/娇羞🐟.webp)
