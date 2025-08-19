from dataclasses import dataclass
from typing import Optional


@dataclass
class MongoConfig:
    user_name: str
    password: str
    url_str: str
    db_name: str
    auth_db: Optional[str] = "admin"
    max_pool_size: Optional[int] = 100
    min_pool_size: Optional[int] = 20

    def __init__(self, url_str, db_name, user_name, password, auth_db,
                 max_pool_size,
                 min_pool_size):
        """
        mongodb://my_user:my_password@hostname:port/my_db?authSource=admin 这种格式的连接，支持rs和集群
        :param user_name  utf-8 用户名，别用urllib转义
        :param password   utf-8 密码，别用urllib转义
        :param url_str    mongo 连接字符串
        :param db_name
        :param auth_db
        :param max_pool_size
        :param min_pool_size
        """
        self.user_name = user_name
        self.password = password
        self.url_str = url_str
        self.db_name = db_name
        self.auth_db = auth_db
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
