# coding=utf-8
"""
@author: noybzy
@time: 2025/5/13 14:34
@file: amqp.py
@describe: TODO
"""
import functools
import time
import threading
from optparse import Option
from queue import Queue
from typing import Callable, TYPE_CHECKING

from loguru import logger
from nosp.config import RabbitMQConfig
from nosp.lazy import LazyLoader

if TYPE_CHECKING:
    import pika
else:
    pika = LazyLoader("pika")


class Message:
    def __init__(self, ch, delivery_tag, body):
        self.body = body
        self.delivery_tag = delivery_tag
        self.ch = ch

    def __ack_message(self, ch, delivery_tag):
        if ch.is_open:
            ch.basic_ack(delivery_tag)

    def __nack_message(self, ch, delivery_tag, requeue):
        if ch.is_open:
            ch.basic_nack(delivery_tag, requeue)

    def __reject_message(self, ch, delivery_tag, requeue):
        if ch.is_open:
            ch.basic_reject(delivery_tag, requeue)

    def ack(self):
        cb = functools.partial(self.__ack_message, self.ch, self.delivery_tag)
        self.ch.connection.add_callback_threadsafe(cb)

    def nack(self, requeue=True):
        try:
            cb = functools.partial(self.__nack_message, self.ch, self.delivery_tag, requeue)
            self.ch.connection.add_callback_threadsafe(cb)
        except Exception as e:
            logger.error(e)

    def reject(self, requeue=True):
        try:
            cb = functools.partial(self.__reject_message, self.ch, self.delivery_tag, requeue)
            self.ch.connection.add_callback_threadsafe(cb)
        except Exception as e:
            logger.error(e)


class RabbitMQ:
    def __init__(self, host='127.0.0.1', port=5672, username='admin', password='123456', queue_name='test',
                 virtual_host='/'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.queue_name = queue_name
        self.virtual_host = virtual_host
        self.lock = threading.Lock()
        self.connection = None
        self.channel = None
        self.queue = Queue()
        self.callback: Option(Callable[[Message], None]) = None

    @staticmethod
    def simple(conf: RabbitMQConfig, queue_name='test') -> 'RabbitMQ':
        return RabbitMQ(conf.host, conf.port, conf.username, conf.password, queue_name, conf.virtual_host)

    def creat_queue(self, queue_name, dlq_name=None):
        self.ensure_channel()
        arguments = None
        if dlq_name:
            # 声明死信队列
            self.channel.queue_declare(queue=dlq_name, durable=True)
            arguments = {
                'x-dead-letter-exchange': '',  # 使用默认交换机
                'x-dead-letter-routing-key': dlq_name  # 死信消息发送到死信队列的路由键
            }
        # 声明主队列，并配置死信交换机和路由键
        self.channel.queue_declare(
            queue=queue_name,
            durable=True,
            arguments=arguments
        )
        print(f"队列 '{queue_name}' 创建成功，死信队列 '{dlq_name}'")

    def _create_connection(self):
        """创建一个新的连接"""
        credentials = pika.PlainCredentials(self.username, self.password)
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        return pika.BlockingConnection(parameters)

    def ensure_channel(self):
        """确保 channel 可用，若不可用则重新建立连接和 channel"""
        if not self.connection or self.connection.is_closed:
            self.connection = self._create_connection()
            self.channel = self.connection.channel()
        elif not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()

    def consume(self, callback: Callable[[Message], None], num):
        self.callback = callback
        while True:
            try:
                self.ensure_channel()
                self.channel.basic_qos(prefetch_count=num + 1)
                self.channel.basic_consume(on_message_callback=self.__on_message, queue=self.queue_name, auto_ack=False)
                logger.debug('Waiting for task. To exit press CTRL+C')
                self.channel.start_consuming()
            except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosedByBroker) as e:
                self._safe_close()
                logger.warning(f"连接错误: {e}. 将在5秒后重试...")
                time.sleep(5)
            except KeyboardInterrupt:
                self._safe_close()
                logger.warning("手动终止")
                break
            except Exception as e:
                self._safe_close()
                logger.error(f"未知错误: {e}. 将在5秒后重试...")
                time.sleep(5)

    def produce(self, queue_name, body=''):
        """
        向队列发送消息（注意这不是线程安全的）
        :param queue_declare:
        :param body:
        :param queue_name:
        :return:
        """
        with self.lock:
            if not queue_name:
                queue_name = self.queue_name
            while True:
                try:
                    self.ensure_channel()
                    self.channel.basic_publish(
                        exchange='',
                        routing_key=queue_name,
                        body=str(body),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    break
                except (pika.exceptions.AMQPConnectionError, pika.exceptions.ConnectionClosedByBroker) as e:
                    self._safe_close()
                    logger.warning(f"生产者连接错误: {e}. 将在5秒后重试...")
                    time.sleep(5)
                except Exception as e:
                    self._safe_close()
                    logger.error(f"未知错误: {e}. 将在5秒后重试...")
                    time.sleep(5)

    def _safe_close(self):
        """安全地关闭连接"""
        if self.connection and not self.connection.is_closed:
            try:
                self.connection.close()
            except pika.exceptions.ConnectionWrongStateError:
                pass
        self.connection = None
        self.channel = None

    def __do_work(self, ch, delivery_tag, body):
        message = Message(ch, delivery_tag, body)
        self.callback(message)

    def __start_work(self):
        while True:
            args = self.queue.get()
            if args is None:
                time.sleep(1)
                continue
            self.__do_work(*args)

    def __on_message(self, ch, method_frame, _header_frame, body):
        delivery_tag = method_frame.delivery_tag
        self.queue.put((ch, delivery_tag, body))


    def start_consuming(self, callback: Callable[[Message],None], num=1):
        for i in range(num):
            t = threading.Thread(target=self.__start_work)
            t.setDaemon(True)
            t.start()
        self.consume(callback, num)
