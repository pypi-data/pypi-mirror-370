import json

from .mysql_module.shein_return_order_model import SheinReturnOrderManager
from .fun_base import log

class SheinMysql:
    def __init__(self, config):
        self.config = config

    def upsert_shein_return_order(self, json_file):
        log(f'当前使用的数据库: {self.config.db.database_url}')
        # 创建管理器实例
        manager = SheinReturnOrderManager(self.config.db.database_url)
        # 创建数据表
        manager.create_tables()
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            dict = json.load(f)
            for store_username, data_list in dict.items():
                manager.upsert_return_order_data(store_username, data_list)