import atexit
import json
import os
import sys
import threading
import time
import uuid
import datetime
from pathlib import Path
import traceback
from typing import Optional
from urllib.parse import urlparse

import requests
from loguru import logger
import socket

from .core import load_env

SPM_CONFIG = os.getenv('SPM_CONFIG', Path("C:\\spm.env") if sys.platform == "win32" else Path("/spm.env"))
load_env(SPM_CONFIG)
LOG_PATH = os.getenv('LOG_PATH', Path("C:\\logs") if sys.platform == "win32" else Path("/logs"))
PY_MONITOR_ENDPOINT = os.getenv('MONITOR_ENDPOINT', 'http://127.0.0.1:14000/api/endpoint')
MAX_RETRY = 100  # 最大上报重试次数
MONITOR_INTERVAL = 10  # 上报间隔


class SpiderInfo:
    def __init__(self, name=None, group_name=None, domain=None, url=None, freq=None, metadata=None, user=None,
                 monitor=True, insert_table=None, task_type=0, wan_ip='0.0.0.0', log=True, show_debug=False,
                 monitor_endpoint=None):
        """
        SpiderInfo 爬虫基础信息监控
        :param name: 名称
        :param group_name: 分组路径 /A/B/C
        :param domain: 目标站点域名
        :param url: 目标站点url
        :param freq: 更新频率: 时更，日更，周更，月更，一次性，任务表
        :param metadata: 其他元数据
        :param user: 所属用户 [ENV:SERVER_USER]
        :param monitor: 是否开启上报数据
        :param insert_table: 插入主表名
        :param task_type: 任务类型 default 0
        :param wan_ip: 外网IP [ENV:WAN_IP]
        :param log: 是否开启本地日志存储
        :param show_debug: 显示调试信息
        :param monitor_endpoint: 上报端点 [ENV:MONITOR_ENDPOINT]
        """
        self.__id = 0
        # 进程ID
        self.pid = str(os.getpid())
        # 运行唯一ID
        self.uid = str(uuid.uuid4())
        # 父ID
        self.parent_uid = None
        # 运行名称
        self.name = name
        # 分组 以 / 分割 eg: '学术/维普/期刊'
        self.group_name = group_name
        # 网址
        self.url = url
        # 域名
        self.domain = domain if domain else (urlparse(url).netloc if self.url else self.url)
        # 更新频率
        self.freq = freq
        # 任务类型
        self.task_type = task_type
        # 其他元数据
        self.metadata: dict = metadata

        # 开始时间
        self.start_time = datetime.datetime.now()
        # 结束时间
        self.end_time = None
        # 运行时间
        self.run_time = None
        # 日志文件
        self.log_file = None
        # py文件
        self.file = None
        # py解释器
        self.interpreter = sys.executable
        # 运行状态 0.待启动 1.运行中 2.完成 -1.异常 -2.断连
        self.status = 0
        # 插入数量
        self.insert_count = 0
        # 插入表名
        self.insert_table = insert_table
        # 进度
        self.progress = 0
        # 总进度
        self.total_progress = 0
        # 异常类名
        self.exception = None
        # 异常堆栈
        self.exception_stack = None

        # 消息
        self.msg = ''
        # 数据
        self.data = ''
        # 服务器名称
        self.server = os.getenv("SERVER_NAME", '未知')
        self.server_location = os.getenv("SERVER_LOCATION", 0)
        self.user = user or os.getenv("SERVER_USER")
        self.lan_ip = '127.0.0.1'
        self.wan_ip = os.getenv("WAN_IP", wan_ip)

        # 是否开启日志输出
        self.__log = log
        # 上报端点
        self.__monitor_endpoint = monitor_endpoint or PY_MONITOR_ENDPOINT
        # 是否输出debug日志
        self.__show_debug = show_debug
        # 是否上报数据
        self.__is_monitor = monitor
        # 获取当前日期
        self.__today = datetime.date.today()
        # 线程锁 (锁:插入量,进度)
        self.__lock = threading.Lock()

        self.__monitor_thread: Optional[threading.Thread] = None
        # self.__stop_event = threading.Event()

        if not monitor:
            return

        # 添加全局异常拦截器
        sys.excepthook = self.__global_exception_handler
        # 注册退出函数
        atexit.register(self.__before_exit)

        self._logeer_id = None
        if self.__log:
            self.__initialize_log_file()
        self.__init_ip()

        self.__last_state = {}

        if self.__is_monitor:
            self.start_monitor()

    def __initialize_log_file(self):
        main_module = sys.modules.get('__main__')
        self.file = main_module.__file__
        # 基础日志目录
        base_log_path = LOG_PATH
        original_path = Path(self.file).resolve()
        stem_name = original_path.stem
        timestamp = self.start_time.strftime("%m%d-%H%M%S.%f")[:-3].replace('.', '')
        log_filename = f"{stem_name}-{timestamp}.log"

        # 获取脚本路径相对于根目录的结构
        rel_path = original_path.parent.relative_to(original_path.anchor)
        full_path = base_log_path.joinpath(rel_path).joinpath(log_filename)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_file = str(full_path)

        if self.log_file:
            self._logeer_id = logger.add(self.log_file, rotation="50 MB")
        self.status = 1

    def __global_exception_handler(self, exc_type, exc_value, exc_traceback):
        self.debug('全局异常捕获')
        stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        logger.error(f"发生异常: {exc_type.__name__}: {exc_value}\n堆栈信息:\n{stack_trace}")
        self.exception = f"{exc_type.__module__}.{exc_type.__name__}"
        self.exception_stack = stack_trace
        self.status = -1
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def __before_exit(self):
        self.debug('程序退出')
        self.end_time = datetime.datetime.now()
        self.run_time = self.end_time - self.start_time
        if self.status != -1:
            self.status = 2
        logger.warning(f'运行时长: {self.run_time} 秒')
        if self.__is_monitor:
            self.report()
        logger.warning(self)

    def __init_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("223.5.5.5", 80))
            self.lan_ip = s.getsockname()[0]
            s.close()
        except Exception:
            try:
                self.lan_ip = socket.gethostbyname(socket.gethostname())
            except:
                pass
        if self.wan_ip == '0.0.0.0':
            try:
                response = requests.get('https://ipinfo.io/json', timeout=5)
                self.wan_ip = response.json()['ip']
            except:
                pass

    def add_count(self, v: int = 1):
        with self.__lock:
            self.insert_count += v

    def add_progress(self, v: int = 1):
        with self.__lock:
            self.progress += v

    def debug(self, msg):
        if self.__show_debug:
            logger.warning(msg)

    def to_dict(self) -> dict:
        data = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                continue

            parts = k.split('_')
            k = parts[0] + ''.join(word.capitalize() for word in parts[1:])

            if isinstance(v, datetime.datetime):
                data[k] = v.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(v, datetime.timedelta):
                data[k] = v.total_seconds()
            elif isinstance(v, dict) and v:
                data[k] = json.dumps(v, ensure_ascii=False)
            else:
                value = str(v)
                data[k] = None if value == 'None' else value
        return data

    def __monitor(self):
        num = 0
        while self.__is_monitor:
            # 如果脚本运行超过一天到达第二天则重置
            if datetime.date.today() > self.__today:
                self.reset()
                result = self.report(False)
            else:
                result = self.report(True)

            if not result:
                num += 1
                if num >= MAX_RETRY:
                    logger.error(f'上传数据失败，超过最大重试次数 {MAX_RETRY} 次，终止上报')
                    break
            else:
                num = 0
            time.sleep(MONITOR_INTERVAL)

    def report(self, filter_data=True):
        """
        上报数据
        :param filter_data: 是否过滤数据 （只上报变化的数据）
        :return:
        """
        try:
            self.debug('上报数据')
            data = self.to_dict()
            if filter_data:
                # 只上报发生变化的数据
                send_data = {k: data[k] for k in data if self.__last_state.get(k) != data.get(k)}
            else:
                send_data = data
            send_data['uid'] = self.uid  # 唯一键
            self.debug(send_data)
            response: dict = requests.post(url=self.__monitor_endpoint, json=send_data, timeout=4).json()
            self.debug(response)
            # 返回这条数据的ID主键
            self.__id = int(response.get('data'))
            # 更新上次上报数据的状态
            self.__last_state.update(data)
            return True
        except Exception as e:
            self.debug(f'上报失败: {e}')
            return False

    def start_monitor(self):
        self.debug('启动监控')
        self.__monitor_thread = threading.Thread(target=self.__monitor)
        self.__monitor_thread.setDaemon(True)
        self.__monitor_thread.start()

    def reset(self):
        # 重置
        now = datetime.datetime.now()
        data = self.to_dict()
        data['run_time'] = (now - self.start_time).total_seconds()
        data['end_time'] = now.strftime("%Y-%m-%d %H:%M:%S")
        data['status'] = 2
        success = False
        for _ in range(5):
            try:
                self.debug('上报数据reset')
                self.debug(data)
                response = requests.post(url=self.__monitor_endpoint, json=data, timeout=4)
                self.debug(response.text)
                success = True
                break
            except Exception as e:
                self.debug(f'上报失败: {e}')
                continue
        if success:
            self.parent_uid = self.uid
            self.uid = str(uuid.uuid4())
            self.start_time = now
            self.insert_count = 0
            self.__today = now.date()

    def close(self):
        atexit.unregister(self.__before_exit)
        sys.excepthook = sys.__excepthook__
        self.__before_exit()
        self.__is_monitor = False

    def __repr__(self):
        return (
            f"SpiderInfo(pid={self.pid}, uid={self.uid}, name={self.name}, group={self.group_name}, "
            f"lan_ip={self.lan_ip}, wan_ip={self.wan_ip}, start_time={self.start_time}, "
            f"end_time={self.end_time}, run_time={self.run_time}, log_file={self.log_file}, "
            f"file={self.file}, interpreter={self.interpreter}, status={self.status}, "
            f"insert_count={self.insert_count}, progress={self.progress}, "
            f"total_progress={self.total_progress}, exception={self.exception})")
