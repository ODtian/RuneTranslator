# RuneTranslator

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/icon/1.gif)

![](https://img.shields.io/github/stars/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/forks/ODtian/RuneTranslator.svg)
![](https://img.shields.io/github/issues/ODtian/RuneTranslator.svg)

## 特性

-   基于 .NET Windows.Media.OCR 的 OCR 引擎，系统自带（调用 powershell，没想到吧）；
-   基于 EdgeChromium Webview 构建的 GUI，系统自带，减小体积；
-   支持渲染文本到原来的位置，不丢失位置信息；
-   简单的架构，欢迎 PR;
-   ...

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
    "tempPath": "截图临时文件存储位置",
    "maxSize": 5000, // 截图缩放大小，更高的尺寸可以提高准确率
    "font": {
        "fontPath": "填写你的字体文件",
        "fontColor": "#ffffff", // 渲染文本颜色
        "fontSize": 16, // 渲染文本大小
        "fontStrokeWidth": 2, // 渲染文本描边大小
        "fontStrokeColor": "#000000" // 渲染文本颜色
    },
    "bgColor": null, // 渲染文本背景颜色，为空则为原背景模糊
    "setWindowWaitingTime": 1, // 渲染文本
    "updateInterval": 1, // 渲染文本
    "api": {
        "baidu": { // 翻译API的模块名，也是类名
            "name": "百度翻译",
            "lang": [
                {
                    "name": "简体中文",
                    "value": "zh" // 翻译语言代码
                }
            ],
            "kwargs": { // 实例化API的参数，没有可以不写
                "app_id": "填写你的参数",
                "secret_key": "填写你的参数"
            }
        },
        "bing": {
        // ...
        },
        "youdao": {
        // ...
    },
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

![](https://raw.githubusercontent.com/ODtian/RuneTranslator/master/icon/0.webp)
