"""
@author: noybzy
@time: 2024/9/19 上午1:02
@file: database.py
@describe: 数据库操作 mysql，redis
@updated: 2025/2/14
"""
import json
import time
from typing import Union, TYPE_CHECKING, Optional

import pymysql
import pymysql.cursors
from dbutils.pooled_db import PooledDB
from loguru import logger

from .config import MysqlConfig, RedisConfig
from .lazy import LazyLoader

if TYPE_CHECKING:
    import redis
else:
    redis = LazyLoader("redis")


class ConnManager:
    def __init__(self, sql_pool, kv=False):
        self.kv = kv
        self.sql_pool = sql_pool
        self.conn: Union[pymysql.connections.Connection, None] = None
        self.cursor: Union[pymysql.cursors.Cursor, None] = None

    def __enter__(self) -> 'ConnManager':
        self.conn = self.sql_pool.connection()
        if self.kv:
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        else:
            self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()


class Mysql(object):
    def __init__(self, host: str = '127.0.0.1', username: str = 'root', password: str = '123456', db: str = 'test',
                 drop_column: list = None, pool_num: int = 4, max_pool: int = None, port: int = 3306, monitor=None,test=False):
        # monitor 历史遗留问题，后续计划删掉
        if drop_column is None:
            drop_column = ["id", "updated", 'created', 'isonline', 'islocal']
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        self.drop_column = drop_column
        self.pool_num = pool_num
        self.sql_pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=max_pool,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=self.pool_num,  # 初始化时，连接池中至少创建的空闲的连接，0表示不创建
            # maxcached=5,  # 连接池中空闲的最多连接数，0和None表示不限制
            # maxshared=3,  # 连接池中最多共享的连接数量，0和None表示全部共享
            blocking=True,  # 连接池中如果没有可用连接后，阻塞等待，而不是报错
            # maxusage=None,  # 一个连接最多被重复使用的次数，None表示无限制
            # setsession=[],  # 开始会话前执行的命令列表
            # ping=0,  # ping MySQL服务端，检查服务是否可用
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.db,
            charset='utf8mb4'
        )
        self.sql_pool.connection()
        self.table_name_list = self.get_db_name()  # 获取所有表名
        self.column_list = {}
        self.test = test

    @staticmethod
    def simple(config: MysqlConfig, pool_num=4, db: str = None, monitor=None, max_pool: int = None, test=False) -> 'Mysql':
        """
        创建Mysql
        :param max_pool: 最大连接数
        :param config: 连接配置
        :param pool_num: 线程池数量
        :param db: 数据库
        :param monitor: 监控
        :return:
        """

        if db is None:
            db = config.db
        mysql = Mysql(
            host=config.host,
            port=config.port,
            username=config.username,
            password=config.password,
            db=db,
            pool_num=pool_num,
            max_pool=max_pool,
            test=test
        )
        return mysql

    def get_db_name(self, db: str = None) -> list:
        """
        获取指定库的所有表
        :return:
        """
        if db is None:
            db = self.db

        sql = "select table_name from information_schema.tables where table_schema='{}'".format(db)
        with ConnManager(self.sql_pool) as cm:
            cm.cursor.execute(sql)
            db_list = cm.cursor.fetchall()
            db_list = [i[0] for i in db_list]
            return db_list

    def get_table_column_list(self, table_name: str) -> dict:
        """
        获取指定表的所有字段
        :param table_name: 表名
        :return:
        """
        column_list = self.column_list.get(table_name)
        if column_list:
            return column_list
        else:
            sql = 'select column_name,data_type from information_schema.columns where table_name=%s and table_schema=%s'
            with ConnManager(self.sql_pool) as cm:
                cm.cursor.execute(sql, (table_name, self.db))
                column_list = cm.cursor.fetchall()
                insert_columns = {}
                for i in column_list:
                    if i[0] in self.drop_column:
                        continue
                    insert_columns[i[0]] = i[1]
                self.column_list[table_name] = insert_columns
                return insert_columns

    def execute_sql(self, sql, params=None, kv=True) -> Union[list, int]:
        """
        执行sql语句
        :param sql: sql代码
        :param params: 参数
        :param kv: 查询结果是否转成字典
        :return: 返回查询结果 | 受影响行数
        """
        try:
            with ConnManager(self.sql_pool, kv=kv) as cm:
                cm.cursor.execute(sql, params)
                if sql.strip().lower().startswith("select"):
                    result = cm.cursor.fetchall()  # 查询语句返回所有结果
                    return result
                else:
                    # 非查询语句，返回受影响的行数
                    cm.conn.commit()
                    return cm.cursor.rowcount
        except Exception as e:
            logger.error(f'执行sql失败：{e.__class__.__name__}|{e.args}>>{sql}, {params}')
            raise e

    @staticmethod
    def wrapper_value(key, value, insert_columns):
        if value is None:
            if insert_columns.get(key) in ('datetime', 'date', 'time', 'year'):
                return None
            else:
                return ''
        else:
            if isinstance(value, bool):
                return value
            else:
                return str(value)

    def insert_data(self, item: dict, table_name: str, replace: bool = False) -> int:
        """
        插入单条数据(默认表里的字段不允许为空[除 'datetime', 'date', 'time', 'year' 字段],['bigint','int', 'decimal' 字段为None时取得默认值] )
        :param item: 数据
        :param table_name: 表名
        :param replace: 是否使用replace，默认insert
        :return: 返回成功的行数
        """
        if item:
            insert_columns = self.get_table_column_list(table_name)
            # 过滤字段，并移除 'int' 或 'decimal' 类型为 None 的字段 (采用数据库默认值)
            filtered_item = {
                k: v for k, v in item.items() if
                k in insert_columns.keys() and not (
                        (v is None or v=='') and insert_columns[k] in ('bigint', 'int', 'decimal', 'tinyint'))
            }
            if not filtered_item:
                logger.warning(f"没有找到可插入的字段: {item}")
                return 0

            insert_columns_new = ['`%s`' % i for i in filtered_item.keys()]
            # 选择 SQL 操作：INSERT 或 REPLACE
            operation = "REPLACE" if replace else "INSERT"
            columns = ', '.join(insert_columns_new)
            placeholders = ', '.join(['%s'] * len(filtered_item))
            sql = f"{operation} INTO {table_name} ({columns}) VALUES ({placeholders})"

            values_list = []
            for key in filtered_item.keys():
                value = filtered_item.get(key)
                values_list.append(self.wrapper_value(key, value, insert_columns))
            values = tuple(values_list)

            try:
                with ConnManager(self.sql_pool) as cm:
                    cm.cursor.execute(sql, values)
                    if self.test:
                        cm.conn.rollback()
                        logger.warning(f'[TEST MODE] {operation} {table_name} would affect rows: {cm.cursor.rowcount}')
                        return 0
                    cm.conn.commit()  # 提交事务
                    logger.success(f'{operation} {table_name} rows:{cm.cursor.rowcount} successfully')
                    rowcount = cm.cursor.rowcount
                    return rowcount
            except pymysql.IntegrityError as e:
                error_code, error_message = e.args  # 获取错误码和错误信息
                if error_code == 1062:
                    # 提取唯一键冲突的详细信息
                    duplicate_key = error_message.split("for key")[1].strip().replace('\'', '').replace('\"',
                                                                                                        '') if "for key" in error_message else "Unknown key"
                    duplicate_value = item.get(duplicate_key.split('.')[-1])
                    logger.warning(f"IntegrityError: {duplicate_key}: {duplicate_value}")
                else:
                    logger.warning(f"IntegrityError: {e.args}")
                return 0
            except pymysql.ProgrammingError as e:
                logger.error(f'sql 语法错误 {e.__class__.__name__},sql:{sql}')
                raise e
            except Exception as e:
                logger.error(f'insert error {e.__class__.__name__}')
                raise e

        else:
            logger.warning('插入为空')

    def insert_data_many(self, item_list: list[dict], table_name: str, batch_size: int = 500, replace: bool = False,
                         ignore: bool = False) -> int:
        """
        批量插入数据(默认表里的字段不允许为空[除 'datetime', 'date', 'time', 'year' 字段],注意['bigint','int', 'decimal' 字段为None时请手动设置默认值] )
        :param item_list: 数据列表
        :param table_name: 表名
        :param batch_size: 批量插入大小
        :param replace: 是否使用replace，默认insert
        :param ignore: 是否忽略掉插入错误
        :return:
        """
        # 批量插入不过滤插入参数

        if not item_list:
            logger.warning("插入的数据列表为空")
            return 0

        # 获取表的列名
        insert_columns = self.get_table_column_list(table_name)
        if not insert_columns:
            logger.warning(f"表 {table_name} 的列名列表为空")
            return 0

        insert_columns_new = ['`%s`' % i for i in insert_columns.keys()]
        # 生成批量插入的 SQL 和数据
        operation = "REPLACE" if replace else "INSERT"
        if ignore:
            operation = operation + ' ' + 'ignore '
        columns = ', '.join(insert_columns_new)
        placeholders = ', '.join(['%s'] * len(insert_columns))
        sql = f"{operation} INTO {table_name} ({columns}) VALUES ({placeholders})"

        rows = []
        for item in item_list:
            values_list = []
            for key in insert_columns.keys():
                value = item.get(key)
                values_list.append(self.wrapper_value(key, value, insert_columns))
            rows.append(tuple(values_list))
        total_inserted = 0
        try:
            with ConnManager(self.sql_pool) as cm:
                # 批量插入，每次插入 batch_size 条记录
                for i in range(0, len(rows), batch_size):
                    batch = rows[i:i + batch_size]
                    try:
                        cm.cursor.executemany(sql, batch)  # 批量插入
                        cm.conn.commit()  # 提交事务
                        inserted_rows = cm.cursor.rowcount
                        total_inserted += inserted_rows
                        logger.success(f"insert {inserted_rows}/{len(batch)} rows into {table_name} successfully.")
                    except pymysql.IntegrityError as e:
                        # 捕获批量插入时的唯一键冲突错误
                        logger.warning(f"IntegrityError during batch insert,尝试单条插入")
                        cm.conn.rollback()
                        for item in item_list[i:i + batch_size]:
                            try:
                                # 逐条插入调用 insert_data 方法
                                self.insert_data(item, table_name, replace)
                            except Exception as individual_e:
                                logger.error(f"insert error during individual inserts: {individual_e}")
                                raise individual_e
        except pymysql.ProgrammingError as e:
            logger.error(f"SQL 语法错误: {e}, SQL: {sql}")
            raise e
        except Exception as e:
            logger.error(f"Insert error: {e.__class__.__name__} - {str(e)}")
            raise e
        return total_inserted


class Message(object):

    def __init__(self, r, queue_name, queue_name_tmp, data):
        self.r = r
        self.queue_name = queue_name
        self.queue_name_tmp = queue_name_tmp
        self.data = data

    def ack(self):
        self.r.lrem(self.queue_name_tmp, 0, self.data)

    def nack(self):
        """
        原子性的否定确认 - 通过Lua脚本保证操作原子性
        """
        lua_script = """
        if redis.call('LREM', KEYS[2], 0, ARGV[1]) > 0 then
            return redis.call('LPUSH', KEYS[1], ARGV[1])
        else
            return 0
        end
        """
        result = self.r.eval(lua_script, 2, self.queue_name, self.queue_name_tmp, self.data)
        if result == 0:
            raise ValueError(f"消息 {self.data} 未在临时队列 {self.queue_name_tmp} 中找到")


class Redis(object):
    def __init__(self, host: str, port: int, password: str, db: int, decode_responses: bool = False):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.r = redis.StrictRedis(host=host, port=port, password=password, db=db, decode_responses=decode_responses)

    @staticmethod
    def simple(config: RedisConfig, db: int = None, decode_responses: bool = True) -> 'Redis':
        """
        使用配置创建Redis对象
        :param config: 配置
        :param db: 数据库
        :param decode_responses: 是否自动解析字节
        :return:
        """
        if not db:
            db = config.db
        return Redis(
            host=config.host,
            port=config.port,
            password=config.password,
            db=db,
            decode_responses=decode_responses
        )

    def flush(self, dst: str):
        """
        使用Lua脚本原子性转移整个列表内容
        """
        lua_script = """
        local items = redis.call('LRANGE', KEYS[1], 0, -1)
        if #items > 0 then
            redis.call('DEL', KEYS[1])
            return redis.call('LPUSH', KEYS[2], unpack(items))
        end
        return 0
        """
        src = f'{dst}_tmp'
        self.r.eval(lua_script, 2, src, dst)

    def pop_message(self, queue_name: str, wait: bool = False) -> Optional[Message]:
        temp_queue_name = f'{queue_name}_tmp'
        if not wait:
            data = self.r.rpoplpush(queue_name, temp_queue_name)
        else:
            data = self.r.brpoplpush(queue_name, temp_queue_name)

        if data:
            return Message(self.r, queue_name, temp_queue_name, data)

    def push(self, queue_name: str, data: Union[dict, str]):
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False)
            self.r.lpush(queue_name, data_str)
        else:
            self.r.lpush(queue_name, data)

    def pop(self, queue_name: str, decode_json: bool = False) -> Union[dict, str]:
        data_str = self.r.rpop(queue_name)
        if decode_json:
            return json.loads(data_str)
        return data_str

    def delay_push(self, queue_name: str, data: Union[dict, str], delay: int = 125):
        """
        延迟添加数据到队列(配合delay_pop用)
        :param queue_name: 队列名称
        :param data: 数据
        :param delay: 延迟执行时间（单位：秒）
        """
        if isinstance(data, dict):
            data_str = json.dumps(data, ensure_ascii=False)
        else:
            data_str = data
        execute_time = time.time() + delay  # 计算任务的执行时间戳
        self.r.zadd(queue_name, {data_str: execute_time})

    def delay_pop(self, queue_name: str, delay=125, wait: bool = False) -> Union[str, None]:
        """
        延迟获取队列数据
        :param queue_name: 队列名称
        :param delay: 延迟时间
        :param wait: 是否等待获取
        :return:
        """
        while True:
            current_time = time.time()
            task_info = self.r.zpopmin(queue_name, 1)
            if task_info:
                task, score = task_info[0]
                if score <= current_time:
                    new_time = current_time + delay
                    self.r.zadd(queue_name, {task: new_time})
                    return task
                else:
                    self.r.zadd(queue_name, {task: score})
                    if wait:
                        logger.debug(f'等待队列 {queue_name}')
                        time.sleep(5)
                        continue
                    else:
                        return None
            else:
                return None
