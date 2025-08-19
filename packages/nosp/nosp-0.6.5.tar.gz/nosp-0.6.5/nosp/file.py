import datetime
import os.path
import time
import zipfile
from enum import Enum
import random
from typing import TYPE_CHECKING, Optional
from urllib.parse import unquote

from loguru import logger
import requests
from .config import OssConfig
from .http import Request
from .lazy import LazyLoader
from .utils import get_md5
from requests.exceptions import ProxyError, Timeout

requests.packages.urllib3.disable_warnings()
if TYPE_CHECKING:
    import oss2
else:
    oss2 = LazyLoader("oss2")


class UploadFile(object):
    """
    文件上传
    """

    def __init__(self, prefix: str, access_key: str = "", access_secret: str = "", endpoint: str = "", bucket_name: str = "", retry_num: int = 5):
        auth = oss2.Auth(access_key, access_secret)
        self.prefix = prefix
        self.bucket = oss2.Bucket(auth, endpoint, bucket_name)
        self.oss_path = prefix + '/' + datetime.datetime.now().strftime("%Y%m/%d")
        self.retry_num = retry_num
        logger.debug(f'当前oss根路径:{self.oss_path}')

    @staticmethod
    def simple(config: OssConfig, prefix: str, bucket_name: str = 'bainiudata1') -> 'UploadFile':
        """
        通过配置文件创建对象
        :param config:
        :param prefix:
        :param bucket_name:
        :return:
        """
        return UploadFile(
            prefix=prefix,
            access_key=config.access_key,
            access_secret=config.access_secret,
            endpoint=config.endpoint,
            bucket_name=bucket_name  # 存储桶
        )

    def is_exist(self, osspath):
        return self.bucket.object_exists(osspath)

    def upload(self, filepath: str, filename: str = None) -> str:
        self.oss_path = self.prefix + '/' + datetime.datetime.now().strftime("%Y%m/%d")
        if not filepath or not os.path.exists(filepath):
            logger.warning(f"本地文件不存在: {filepath}")
            return ''
        if filename:
            oss_abs_path = self.oss_path + '/' + filename
        else:
            oss_abs_path = self.oss_path + '/' + filepath.split('/')[-1]

        exist = self.bucket.object_exists(oss_abs_path)
        if exist:
            logger.warning(f"oss 存在相同名的文件 {oss_abs_path}")
            return oss_abs_path
        else:
            num = 0
            while True:
                try:
                    result = self.bucket.put_object_from_file(oss_abs_path, filepath)
                    break
                except Exception as e:
                    num += 1
                    logger.error(f'{e.__class__}')
                    if num > self.retry_num:
                        logger.error(f"oss upload faild {oss_abs_path},error:{e}")
                        return ''

            if int(result.status) == 200:
                logger.success(f"{oss_abs_path} 上传成功")
            else:
                logger.error(f"oss upload faild {oss_abs_path},status:{result.status}")
            return oss_abs_path


class DownloadFile(object):
    """
    下载文件
    """

    class NameMode(Enum):
        URL = 1
        Content_Disposition = 2
        Custom = 3

    def __init__(self, url, method='get', data=None, json_data: dict = None, headers: dict = None, cookies: dict = None, timeout: int = 20, proxy=False, save_path='file/', retry_num=5, name_mode=NameMode.URL,proxy_url=None):
        self.url = url
        self.headers = headers
        self.cookies = cookies
        self.proxy = proxy
        self.timeout = timeout
        self.method = method
        self.data = data
        self.json_data = json_data

        self.save_path = save_path  # 文件保存位置
        self.response = None  # 响应体
        self.filename = None  # 文件名
        self.filepath = None  # 文件路径
        self.prefix = None  # 文件前缀
        self.suffix = None  # 文件后缀
        self.name_mode: DownloadFile.NameMode = name_mode  # 文件名模式
        self.retry_num = retry_num  # 下载重试次数

        self.proxy_url = proxy_url


    def get_proxy(self) -> Optional[dict]:
        if self.proxy_url:
            num = 0
            while True:
                num += 1
                try:
                    proxy = requests.get(self.proxy_url, timeout=6).json()
                    break
                except Exception as e:
                    logger.warning(f'获取代理出错_{num}:{e.__class__}')
                    time.sleep(5)
            return proxy
        return None
    # def get_filename(self):
    #     """
    #     获取文件名
    #     模式：
    #         1，通过url获取
    #         2. 通过content-type获取
    #         3. 指定文件后缀
    #     :return:
    #     """
    #
    #     if self.name_mode == DownloadFile.NameMode.URL:
    #         self.suffix = '.' + self.url.split('?')[0].split('.')[-1]
    #         self.prefix = get_md5(self.url)
    #     if self.name_mode == DownloadFile.NameMode.Content_Disposition:
    #         dis = self.response.headers.get('Content-Disposition')
    #         if dis:
    #             filename = re.findall('filename=(.*)', dis)
    #             if filename:
    #                 self.suffix = filename[0].strip('\"').split('.')[-1]
    #                 self.suffix = '.' + self.suffix
    #         if not self.suffix:
    #             self.suffix = self.response.headers.get('Content-Type').split('/')[-1].split(';')[0]
    #             self.suffix = '.' + self.suffix
    #         self.prefix = get_md5(self.url)
    #     if self.name_mode == DownloadFile.NameMode.Custom:
    #         if self.filename:
    #             self.filepath = os.path.join(self.save_path, self.filename)
    #             return
    #         else:
    #             self.prefix = get_md5(self.url)
    #             if self.suffix is None:
    #                 logger.warning(f"未指定文件后缀")
    #                 self.suffix = ''
    #     self.filename = f"{self.prefix}{self.suffix}"
    #     self.filepath = os.path.join(self.save_path, self.filename)
    def get_filename(self):
        """
        根据指定模式生成文件名并构建完整存储路径
        模式：
            1，通过url获取
            2. 通过content-type获取
            3. 指定文件后缀
        :return:
        """

        if self.name_mode == DownloadFile.NameMode.URL:
            try:
                path_part = self.url.split('?', 1)[0]
                filename_part = path_part.split('/')[-1]
                if '.' in filename_part:
                    self.suffix = '.' + filename_part.rsplit('.', 1)[-1]
                    if len(self.suffix) > 10:
                        self.suffix = ''
                else:
                    self.suffix = ''  # 无有效扩展名时留空
                self.prefix = get_md5(self.url)
            except Exception as e:
                logger.exception(e)
                self.suffix = ''
                self.prefix = get_md5(self.url)
        elif self.name_mode == DownloadFile.NameMode.Content_Disposition:
            # 从Content-Disposition头解析文件名
            content_disposition = self.response.headers.get('Content-Disposition', '')
            filename = self._parse_content_disposition(content_disposition)
            if filename:
                if '.' in filename:
                    self.suffix = '.' + filename.rsplit('.', 1)[-1]
                else:
                    # 无扩展名时从Content-Type获取类型
                    self.suffix = self._get_suffix_from_content_type()
            else:
                # 无法解析文件名时从Content-Type获取
                self.suffix = self._get_suffix_from_content_type()
            self.prefix = get_md5(self.url)
        elif self.name_mode == DownloadFile.NameMode.Custom:
            if self.filename:
                # 直接使用用户指定的文件名
                self.filepath = os.path.join(self.save_path, self.filename)
                return
            else:
                # 生成基础文件名
                self.prefix = get_md5(self.url)
                if self.suffix is None:
                    logger.warning("未指定文件后缀，将使用空后缀")
                    self.suffix = ''
        else:
            raise ValueError(f"未知的文件命名模式：{self.name_mode}")

        # 构建最终文件名和路径
        self.filename = f"{self.prefix}{self.suffix}"
        self.filepath = os.path.join(self.save_path, self.filename)

    def _parse_content_disposition(self, content_disposition):
        """解析Content-Disposition头获取文件名"""
        if not content_disposition:
            return None

        filename = None
        parts = [p.strip() for p in content_disposition.split(';')]

        for part in parts:
            if part.lower().startswith('filename='):
                filename = part[len('filename='):].strip()
                # 去除包裹的引号
                if filename.startswith(('"', "'")):
                    filename = filename[1:-1]
                filename = unquote(filename)
                break
            elif part.lower().startswith('filename*='):
                filename_part = part[len('filename*='):]
                try:
                    encoding, _, filename_encoded = filename_part.split("'", 2)
                    filename = unquote(filename_encoded)
                    break
                except ValueError:
                    continue

        return filename

    def _get_suffix_from_content_type(self):
        """从Content-Type头提取文件后缀"""
        # MIME_MAPPING = {
        #     # 常见文档类型
        #     'application/pdf': '.pdf',
        #     'application/msword': '.doc',
        #     'application/vnd.ms-excel': '.xls',
        #     'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
        #     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
        #     'application/vnd.ms-powerpoint': '.ppt',
        #
        #     # 图片类型
        #     'image/jpeg': '.jpg',
        #     'image/png': '.png',
        #     'image/gif': '.gif',
        #     'image/webp': '.webp',
        #     'image/svg+xml': '.svg',
        #
        #     # 压缩文件
        #     'application/zip': '.zip',
        #     'application/x-rar-compressed': '.rar',
        #     'application/x-tar': '.tar',
        #     'application/gzip': '.gz',
        #
        #     # 文本类型
        #     'text/plain': '.txt',
        #     'text/csv': '.csv',
        #     'text/html': '.html',
        #     'application/json': '.json',
        #     'application/xml': '.xml',
        #
        #     # 二进制流
        #     'application/octet-stream': ''
        # }
        content_type = self.response.headers.get('Content-Type', 'application/octet-stream').split(';', 1)[0]
        mime_type = content_type.split('/', 1)[-1] if '/' in content_type else 'octet-stream'
        return '.' + mime_type

    def download(self, mode='stream'):
        logger.debug(f"下载文件：{self.url}")
        num = 0
        while True:
            try:
                if self.method == 'get':
                    response = requests.get(url=self.url, headers=self.headers, cookies=self.cookies, timeout=self.timeout,
                                            verify=False, proxies=self.proxy)
                elif self.method == 'post':
                    response = requests.post(url=self.url, data=self.data, json=self.json_data, headers=self.headers,
                                             cookies=self.cookies, timeout=self.timeout, verify=False, proxies=self.proxy)
                self.response = response

                if response.status_code == 404:
                    logger.warning(f"下载文件出错code:{response.status_code},放弃下载")
                    break

                if response.status_code != 200:
                    num = num + 1
                    logger.warning(f"下载文件出错code:{response.status_code} :retry：{num}")
                    if num > self.retry_num:
                        logger.error(f"下载失败：{self.url},达到最大重试次数，放弃下载")
                        break
                    time.sleep(3)
                    continue
            except ProxyError as e:
                self.proxy = self.get_proxy()
                logger.debug(f'{e.__class__}')
                continue
            except Exception as e:
                num += 1
                logger.error(f"{e}")
                logger.warning(f"下载文件出错：{self.url},retry：{num}")
                if num > self.retry_num:
                    logger.error(f"下载失败：{self.url},达到最大重试次数，放弃下载")
                    break
                time.sleep(random.randint(3, 5))
                continue

            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            self.get_filename()
            with open(self.filepath, "wb") as f:
                f.write(response.content)
            logger.success(f"下载文件成功：{self.filepath}")
            break

    def remove(self):
        if not self.filepath:
            return
        if os.path.exists(self.filepath):
            os.remove(self.filepath)


def unzip(filepath, target='file', buffer_size=1024 * 64):
    """
    解压zip文件
    :param filepath:
    :param target:
    :param buffer_size:
    :return:
    """
    file_list = []
    with zipfile.ZipFile(filepath, 'r') as zip_file:
        for file_info in zip_file.infolist():
            filename = file_info.filename.encode('cp437').decode('gbk')
            file_path = os.path.join(target, filename)
            if file_info.is_dir():
                os.makedirs(file_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with zip_file.open(file_info) as source_file:
                    with open(file_path, "wb") as target_file:
                        while True:
                            buffer = source_file.read(buffer_size)
                            if not buffer:
                                break
                            target_file.write(buffer)
                file_list.append(file_path)
    return file_list


def get_file_content(filepath: str) -> str:
    if not os.path.exists(filepath):
        return ''
    with open(filepath, 'r', encoding='UTF-8') as file:
        result = file.read()
    return result
