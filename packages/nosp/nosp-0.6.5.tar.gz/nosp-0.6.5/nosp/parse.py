import datetime
import re
from dataclasses import dataclass, field
from .lazy import LazyLoader
from typing import Union, List, Optional, Dict, Callable, TYPE_CHECKING

from loguru import logger
from parsel import Selector

if TYPE_CHECKING:
    import dateparser
    import pandas as pd
else:
    dateparser = LazyLoader("dateparser")  # type: ignore
    pd = LazyLoader("pandas")  # type: ignore


@dataclass
class AttachmentsAndImagesResult:
    """
    封装附件和图片的结果
    """
    file_urls: List[str] = field(default_factory=list)  # 文件链接列表
    file_names: List[str] = field(default_factory=list)  # 文件名称列表
    image_urls: List[str] = field(default_factory=list)  # 图片链接列表
    image_names: List[str] = field(default_factory=list)  # 图片名称列表


def get_column_list(text: str, xpath: str, str_add_head: str = '', str_add_tail: str = '', auto_wash: bool = True) -> \
list[str]:
    if isinstance(text, str):
        selector = Selector(text=text)
        value_list = selector.xpath(xpath).getall()
        if auto_wash:
            value_new_list = []
            for value in value_list:
                value = value.replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('\t', '')
                value_new_list.append(str_add_head + value + str_add_tail)
            return list(value_new_list)
        else:
            return value_list
    else:
        return []


def get_column(text: str, xpath: str, str_add_head: str = '', str_add_tail: str = '', auto_wash: bool = True) -> str:
    if isinstance(text, str):
        selector = Selector(text=text)
        value_list = selector.xpath(xpath).getall()
        if auto_wash:
            result = []
            for value in value_list:
                value = value.replace(' ', '').replace('\r', '').replace('\n', '').replace('\xa0', '').replace('\t',
                                                                                                               '').replace(
                    '\u3000', '')
                result.append(value)
            result_result = str_add_head + ''.join(result) + str_add_tail

            return result_result
        else:
            return ''.join(value_list)


def get_content(text: str, xpath_expression: str, auto_space: bool = True) -> str:
    """
    获取正文内容，并忽略style、script标签
    :param text: HTML文本
    :param xpath_expression: XPath表达式
    :param auto_space: 是否自动去除空格（True：去除所有空格，False：保留单个空格）
    :return: 清理后的文本内容
    """
    if not text:
        return ''

    selector = Selector(text=text)

    # 移除style和script标签
    for style in selector.xpath(xpath_expression + '//style'):
        style.drop()
    for script in selector.xpath(xpath_expression + '//script'):
        script.drop()

    # 提取内容并拼接
    contents = selector.xpath(xpath_expression).xpath('string(.)').getall()
    content = ''.join(contents).strip() \
        .replace('\r', '') \
        .replace('\n', '') \
        .replace('\xa0', '') \
        .replace('\t', '') \
        .strip()

    if auto_space:
        content = content.replace(' ', '')
    else:
        content = re.sub(r' +', ' ', content)

    return content


def get_attachments_and_images(text: str, xpath_expression: str, file_str: str = None) -> AttachmentsAndImagesResult:
    """
    获取正文中的附件和图片链接及名称
    :param text: HTML文本
    :param xpath_expression: XPath表达式
    :param file_str: 额外的文件后缀（可选）
    :return: AttachmentsAndImagesResult 对象，包含文件链接、文件名称、图片链接、图片名称
    """
    # 定义文件后缀列表和图片后缀列表
    file_extensions = ['.rar', '.zip', '.7z', '.tar', '.gz', '.docx', '.doc', '.xlsx', '.xls', '.pdf', '.txt', '.csv',
                       '.et']
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']

    # 添加大写后缀
    file_extensions += [ext.upper() for ext in file_extensions]
    image_extensions += [ext.upper() for ext in image_extensions]

    # 如果有额外的文件后缀，添加到文件后缀列表
    if file_str:
        file_extensions.append(file_str)

    # 构建文件和图片链接的 XPath 表达式
    file_extensions_xpath = ' or '.join([f'contains(@href, "{ext}")' for ext in file_extensions])
    image_extensions_xpath = ' or '.join([f'contains(@src, "{ext}")' for ext in image_extensions])
    image_a_extensions_xpath = ' or '.join([f'contains(@href, "{ext}")' for ext in image_extensions])

    # 构建完整的 XPath 表达式
    file_xpath_expression = f'{xpath_expression}//a[{file_extensions_xpath}]/@href'
    file_name_xpath_expression = f'{xpath_expression}//a[{file_extensions_xpath}]//text()'
    image_xpath_expression = f'{xpath_expression}//a[{image_a_extensions_xpath}]/@href | {xpath_expression}//img[{image_extensions_xpath}]/@src'
    image_name_xpath_expression = f'{xpath_expression}//img[{image_extensions_xpath}]/@alt'

    # 创建Selector对象
    selector = Selector(text=text)

    # 获取文件链接和名称
    file_urls = selector.xpath(file_xpath_expression).getall()
    file_names = selector.xpath(file_name_xpath_expression).getall()

    # 获取图片链接和名称
    image_urls = selector.xpath(image_xpath_expression).getall()
    image_names = selector.xpath(image_name_xpath_expression).getall()

    # 过滤掉 base64 图片
    image_urls = [url for url in image_urls if not url.startswith('data:image')]

    # 返回封装的结果
    return AttachmentsAndImagesResult(
        file_urls=file_urls,
        file_names=file_names,
        image_urls=image_urls,
        image_names=image_names
    )


def get_p_list(xpath: str, text: str) -> list[str]:
    """
    获取这一级所有 p 标签的 content
    :param xpath: XPath 表达式
    :param text: HTML 文本
    :return: 清理后的 p 标签内容列表
    """
    selector = Selector(text=text)
    p_tags = selector.xpath(xpath).getall()
    ps = []
    for p in p_tags:
        # 使用 Selector 解析每个 p 标签的内容
        p_content = Selector(text=p).xpath('string(.)').get().strip() \
            .replace(' ', '') \
            .replace('\r', '') \
            .replace('\n', '') \
            .replace('\xa0', '') \
            .replace('\t', '') \
            .replace(' ', '')
        ps.append(p_content)
    return ps


def get_p_value(p_list: list[str], *keys: str) -> Optional[str]:
    """
    从 p_list 中查找以任意一个 key 开头的内容，并返回匹配的值
    """
    for p in p_list:
        for key in keys:
            if re_match := re.search(f'^{key}(.*)', p):
                return re_match.group(1).strip()
    return None


def parse_date(date_str: str) -> Union[datetime.date, None]:
    """
    动态解析日期字符串(严格模式)
    :param date_str:
    :return:
    """
    if not date_str:
        return None

    return dateparser.parse(str(date_str), settings={'STRICT_PARSING': True})


def parse_table(
        trs: List[str],
        header_str: Optional[str] = None,
        skip_line: Optional[int] = None,
        nested: bool = False,
        column_mapper: Optional[Dict[str, str]] = None,
        multi_header: bool = False,
        skip_empty_rows: bool = True,
        cell_formatter: Optional[Callable[[str], str]] = None
) -> List[Dict[str, Union[str, List[Dict[str, str]]]]]:
    """
        解析 HTML 表格，支持嵌套表格、自定义列名映射、多表头行
        :param trs: 表格里的 tr 标签数组
        :param header_str: 判断表头的字符串
        :param skip_line: 跳过指定行数
        :param nested: 是否解析嵌套表格
        :param column_mapper: 自定义列名映射规则
        :param multi_header: 是否支持多行表头
        :param skip_empty_rows: 是否跳过空行
        :param cell_formatter: 自定义单元格内容格式化函数
        :return: 解析后的表格数据（字典列表）
        """

    if not trs:
        return []

    # 跳过指定行数
    if skip_line and skip_line > 0:
        trs = trs[skip_line:]

    # 检查表头下标
    header_index = -1
    for i, tr in enumerate(trs):
        if header_str and header_str in tr:
            header_index = i
            break
    if header_index == -1:
        return []

    # 获取表头
    header_trs = [trs[header_index]]
    if multi_header:
        # 如果支持多行表头，继续向上查找表头行
        for i in range(header_index - 1, -1, -1):
            if any(tag in trs[i] for tag in ['<th>', '<td>']):
                header_trs.insert(0, trs[i])
            else:
                break

    columns = []
    for header_tr in header_trs:
        header_selector = Selector(text=header_tr)
        header_tds = header_selector.xpath('//td | //th').getall()
        current_columns = [
            Selector(text=td).xpath('string(.)').get().strip()
            .replace(' ', '')
            .replace('\r', '')
            .replace('\n', '')
            .replace('\xa0', '')
            .replace('\t', '')
            for td in header_tds
        ]
        if not columns:
            columns = current_columns
        else:
            # 合并多行表头
            columns = [f"{col1}_{col2}" if col2 else col1 for col1, col2 in zip(columns, current_columns)]

    # 自定义列名映射
    if column_mapper:
        columns = [column_mapper.get(col, col) for col in columns]

    # 解析表格内容
    result = []
    for tr in trs[header_index + 1:]:
        content_selector = Selector(text=tr)
        content_tds = content_selector.xpath('//td').getall()

        if len(content_tds) != len(columns):  # 如果列数不匹配，跳过该行
            continue

        item = {}
        for i, td in enumerate(content_tds):
            td_selector = Selector(text=td)
            td_text = (td_selector.xpath('string(.)').get().strip()
                       .replace('\r', '')
                       .replace('\n', '')
                       .replace('\xa0', '')
                       .replace('\t', ''))

            # 自定义单元格内容格式化
            if cell_formatter:
                td_text = cell_formatter(td_text)

            # 解析嵌套表格
            if nested and '<table' in td:
                nested_tables = td_selector.xpath('//table').getall()
                if nested_tables:
                    td_text = parse_table(nested_tables, header_str=header_str, nested=True)

            item[columns[i]] = td_text

        # 跳过空行
        if skip_empty_rows and all(not value for value in item.values()):
            continue

        result.append(item)

    return result


def parse_excel(path, header_str, merge=False):
    try:
        p = pd.read_excel(path)
    except Exception as e:
        logger.error(e)
        return []
    # header_str = '案件名称'
    # 获取表头那一行
    header_index = -1

    if header_str in p.columns:
        columns = p.columns
        header_index = 0
    else:
        for i, v in enumerate(p.values):
            if header_str in v:
                header_index = i
                break
        columns = p.values[header_index]
    if header_index == -1:
        return []
    result = []
    for v in p.values[header_index + 1:]:
        item = {}
        for i, column in enumerate(columns):
            item[column] = v[i]
        result.append(item)

    return result


def parse_excel_v2(path, header_str: Union[list[str], str]):
    # 如果header_str是字符串，则调用parse_excel
    if not isinstance(header_str, list):
        return parse_excel(path, header_str)
    if len(header_str) < 2:
        return []

    try:
        df = pd.read_excel(path, header=None)
    except Exception as e:
        logger.error(e)
        return []

    # 查找最后一个表头的索引
    last_header = header_str[-1]
    last_index = next((i for i, row in enumerate(df.values) if last_header in row), -1)

    if last_index == -1:
        return []

    # 验证表头行是否包含header_str中的元素
    header_start_index = last_index - len(header_str) + 1
    if header_start_index < 0 or not all(any(header_str[j] in str(cell) for cell in df.iloc[idx]) for j, idx in
                                         enumerate(range(header_start_index, last_index + 1))):
        columns = df.iloc[last_index].tolist()
    else:
        # 前向填充表头行
        header_df = df.iloc[header_start_index:last_index + 1].ffill(axis=0)
        # 取最后一行作为真正的表头
        columns = header_df.iloc[-1].tolist()

    # 生成结果列表
    result = []
    for row in df.values[last_index + 1:]:
        item = {col: value for col, value in zip(columns, row)}
        result.append(item)

    return result
