class MysqlConfig(object):
    def __init__(self, host: str, port: int, username: str, password: str, db: str, charset: str = 'utf8mb4'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        self.charset = charset


class RedisConfig(object):
    def __init__(self, host: str, port: int, password: str, db: int):
        self.host = host
        self.port = port
        self.password = password
        self.db = db


class RabbitMQConfig(object):
    def __init__(self, host: str, port: int, username: str, password: str, virtual_host: str = '/'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host


class OssConfig(object):
    def __init__(self, access_key: str, access_secret: str, endpoint: str, bucket_name: str, region: str = None):
        self.access_key = access_key
        self.access_secret = access_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.region = region
