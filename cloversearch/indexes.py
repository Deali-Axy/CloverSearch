import time

from django.apps import apps
from .config import ConfigManager
import logging
import ujson as json
import copy
import os

logger = logging.getLogger(ConfigManager.logger_name)


class Index:
    """索引类，一个Index对应的就是数据库表里的一行"""

    # App Name
    app_name = ''
    # Model类名称
    model_name = ''
    # 主键
    primary_key = 0
    # 关键词列表, key: field_name, value: keywords list
    keywords = {}
    # 处理后的数据, key: field_name, value: 过滤字符后的content
    clean_data = {}

    def __init__(self, app_name: str, model_name: str, primary_key):
        self.app_name = app_name
        self.model_name = model_name
        self.primary_key = primary_key
        # 不要怀疑，这里再赋值一次是非常有必要的，再复制一次可以在下次调用的使用作为 deepcopy 的新对象获取，而不会保留之前创建对象的旧数据
        self.keywords = dict()
        self.clean_data = dict()
        self.index_manager = None

    @property
    def __id__(self):
        """Index身份：对应的app/model名称和主键"""
        return '{}.{}:{}'.format(self.app_name, self.model_name, self.primary_key)

    def __repr__(self):
        return '{}:[keywords:{}][clean_data:{}]'.format(self.model_name, len(self.keywords), len(self.clean_data))

    def get_model_class(self):
        """获取model类"""
        try:
            app_obj = apps.get_app_config(self.app_name)
            model = app_obj.get_model(self.model_name)
            return model
        except Exception as e:
            logger.error(e)
            return None

    def get_model_instance(self):
        """获取对应的model实例"""
        try:
            instance = self.get_model_class().objects.get(pk=self.primary_key)
            return instance
        except Exception as e:
            logger.error(e)
            return None

    def serialize_keywords(self):
        return json.dumps(self.keywords, ensure_ascii=False)

    def serialize_clean_data(self):
        return json.dumps(self.clean_data, ensure_ascii=False)

    def deserialize_keywords(self, data):
        self.keywords = json.loads(data)

    def deserialize_clean_data(self, data):
        self.clean_data = json.loads(data)


class IndexManager:
    # list of index objects
    indexes = []
    index_manager_instance = None

    @classmethod
    def get_instance(cls):
        if cls.index_manager_instance is None:
            cls.index_manager_instance = IndexManager()
            # 只有在第一次获取实例的时候才加载索引
            cls.load(cls.index_manager_instance)
        return cls.index_manager_instance

    def add(self, index_obj: Index):
        # 这里要使用深度复制，才能把一个新的 index_obj 对象添加到index列表中
        # 如果不这样的话，只能添加 index_obj 的引用地址，结果就是index列表的所有数据都一样了
        self.indexes.append(copy.deepcopy(index_obj))

    def load(self):
        # 没有索引文件夹则立即退出！
        if not os.path.exists(ConfigManager.index_dir):
            logger.error('未找到索引文件夹')
            return

        start_time = time.time()
        for app_dir in os.listdir(ConfigManager.index_dir):
            for model_dir in os.listdir(os.path.join(ConfigManager.index_dir, app_dir)):
                for index_dir in os.listdir(os.path.join(ConfigManager.index_dir, app_dir, model_dir)):
                    primary_key = index_dir
                    index = Index(app_dir, model_dir, primary_key)
                    index_dir = os.path.join(ConfigManager.index_dir, app_dir, model_dir, index_dir)
                    with open(os.path.join(index_dir, 'clean_data.json'), 'r', encoding=ConfigManager.default_file_encoding) as f:
                        index.deserialize_clean_data(f.read())
                    with open(os.path.join(index_dir, 'keywords.json'), 'r', encoding=ConfigManager.default_file_encoding) as f:
                        index.deserialize_keywords(f.read())
                    # 添加到index列表
                    self.indexes.append(index)
        end_time = time.time()
        used_time = end_time - start_time
        logger.info("Loaded indexes data finished. took={}s".format(used_time))

    def save(self):
        # 建立各个app的文件夹
        for app_name in ConfigManager.app_list:
            app_dir = os.path.join(ConfigManager.index_dir, app_name)
            self.create_dir(app_dir)

        start_time = time.time()
        for item in self.indexes:
            # 检查相关文件夹是否建立
            model_dir = os.path.join(ConfigManager.index_dir, item.app_name, item.model_name)
            self.create_dir(model_dir)
            index_dir = os.path.join(model_dir, str(item.primary_key))
            self.create_dir(index_dir)
            # 写入数据
            clean_data_file = os.path.join(index_dir, 'clean_data.json')
            keywords_file = os.path.join(index_dir, 'keywords.json')
            with open(clean_data_file, 'w', encoding='utf-8') as f:
                f.write(item.serialize_clean_data())
                logger.debug('写入索引数据文件:{}'.format(clean_data_file))
            with open(keywords_file, 'w', encoding='utf-8') as f:
                f.write(item.serialize_keywords())
                logger.debug('写入索引数据文件:{}'.format(keywords_file))
        end_time = time.time()
        used_time = end_time - start_time
        logger.info("Loaded indexes data finished. took={}s".format(used_time))

    @classmethod
    def create_dir(cls, path):
        if not os.path.exists(path):
            os.mkdir(path)
            logger.debug('建立文件夹：{}'.format(path))
