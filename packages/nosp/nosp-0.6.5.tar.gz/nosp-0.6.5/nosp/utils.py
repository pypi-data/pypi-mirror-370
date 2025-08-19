import hashlib
import re
from typing import Union, Callable, Any, Optional, List
from urllib.parse import urljoin


def get_md5(text: str, sep: str = "", *args: Any) -> str:
    """
    md5,支持自定义分隔符
    :param text: md5字符串
    :param sep: 拼接时的分隔符
    """
    args_str = sep.join(str(arg) for arg in args)
    combined_text = text + sep + args_str if args_str else text
    m = hashlib.md5()
    m.update(combined_text.encode('utf-8'))
    return m.hexdigest()


def filter_dict(data: dict, condition_func: Callable[[Any], bool], default_value: Any = None) -> Optional[dict]:
    """
    过滤字典符合的键值对，将其设为自定义默认值
    :param data: 字典
    :param condition_func: 过滤条件函数（可以是lambda表达式）
    :param default_value: 自定义默认值，默认为 None
    :return: 过滤后的字典，如果输入不是字典则返回 None
    """
    if isinstance(data, dict):
        # 遍历字典的键值对
        for key, value in data.items():
            if condition_func(value):  # 如果值符合条件
                data[key] = default_value  # 设置为自定义默认值
        return data
    return None


def join_url(base_url, url: Union[str, list]) -> Union[str, list]:
    """
    获取完整路径
    :param base_url:
    :param url:
    :return:
    """
    if isinstance(url, list):
        urls = []
        for i in url:
            urls.append(urljoin(base_url, i))
        return urls
    if isinstance(url, str):
        return urljoin(base_url, url)


def get_re_value(res: Union[list[str], str], content: str) -> str:
    """
    从 content 中查找匹配正则表达式的结果，并返回第一个匹配的值
    :param res: 正则表达式（字符串或字符串列表）
    :param content: 需要匹配的内容
    :return: 匹配到的值（字符串），如果没有匹配到则返回空字符串
    """
    patterns = [res] if isinstance(res, str) else res
    # 遍历正则表达式列表
    for pattern in patterns:
        if match := re.search(pattern, content):
            return match.group(1)
    # 如果没有匹配到，返回空字符串
    return ''


def get_single_or_list(ls: List[Any], default: Any = None,
                       is_empty_func: Callable[[List[Any]], bool] = lambda x: not x) -> Union[Any, List[Any], None]:
    """
    获取列表中的单个元素或整个列表，支持自定义空值检查和默认返回值。
    :param ls: 输入的列表
    :param default: 如果列表为空，返回的默认值
    :param is_empty_func: 自定义的空值检查函数
    :return: 单个元素、整个列表或默认值
    """
    if is_empty_func(ls):
        return default
    if len(ls) == 1:
        return ls[0]
    return ls
