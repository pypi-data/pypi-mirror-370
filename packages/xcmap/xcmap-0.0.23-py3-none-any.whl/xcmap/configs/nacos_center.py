import threading
from multiprocessing import set_start_method
from typing import Optional

import nacos
import yaml
from nacos.client import logger
from pydantic import BaseModel
from yaml.resolver import ResolverError


class NacosConfig(BaseModel):
    server_addresses: str
    namespace: Optional[str] = "public"
    username: str
    password: str
    data_id: str
    group: Optional[str] = "DEFAULT_GROUP"
    data_type: Optional[str] = "yaml"

class NacosWatcher:
    def __init__(self, nacos_config: NacosConfig, update_callback):
        self.client = nacos.NacosClient(
            server_addresses= nacos_config.server_addresses,
            namespace=nacos_config.namespace,
            username=nacos_config.username,
            password=nacos_config.password
        )
        self.DATA_ID = nacos_config.data_id
        self.GROUP_NAME = nacos_config.group
        self.DATA_TYPE = nacos_config.data_type
        self.update_callback = update_callback

    def _init_process(self):
        """独立进程初始化"""
        try:
            # 设置多进程启动方式
            set_start_method('fork', force=True)

            # 添加监听器
            self.client.add_config_watcher(
                self.DATA_ID,
                self.GROUP_NAME,
                self._config_callback
            )
        except Exception as e:
            raise SystemError(f"监听器初始化失败: {e}")

    def _config_callback(self, cb_config):
        """配置更新回调"""
        if self.DATA_TYPE == "yaml":
            try:
                self.update_callback(yaml.safe_load(cb_config.get('content')))
            except Exception as e:
                print(f'解析Yaml失败: {e}')


    def start(self):
        """启动监听进程"""
        watcher_thread = threading.Thread(target=self._init_process, daemon=True)
        watcher_thread.start()
        logger.info("Nacos 配置监听器已启动")

class NacosStore:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, nacos_config: NacosConfig):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, nacos_config: NacosConfig):
        # 防止重复初始化
        if hasattr(self, "_initialized"):
            return
        self.lock = threading.Lock()
        self._config = None
        self._initialized = True

        # 初始化监听器
        self.client = NacosWatcher(nacos_config, self._update_config)
        self._init_config()
        self.client.start()

    def _init_config(self):
        """初始化配置"""
        raw_config = self.client.client.get_config(
            data_id=self.client.DATA_ID,
            group=self.client.GROUP_NAME,
            timeout=10
        )
        if self.client.DATA_TYPE == "yaml":
            try:
                with self.lock:
                    self._config = yaml.safe_load(raw_config)
            except Exception as e:
                raise ResolverError(f'解析Yaml失败: {e}')
    def _update_config(self, new_config):
        """配置更新回调（线程安全）"""
        with self.lock:
            self._config = new_config

    def get_config(self):
        """获取配置（线程安全）"""
        with self.lock:
            return self._config