from .baidu import Baidu
from .bing import Bing
from .direct import Direct
from .microsoft import Microsoft
from .sogou import Sogou
from .youdao import Youdao

baidu = Baidu
bing = Bing
direct = Direct
microsoft = Microsoft
sogou = Sogou
youdao = Youdao

__all__ = [
    "baidu",
    "bing",
    "direct",
    "microsoft",
    "sogou",
    "youdao",
]
