from django.conf import settings
import os, logging

# 简单的配置一下搜索模块名称和配置名
MODULE_NAME = 'CloverSearch'
CONFIG_NAME = 'CLOVER_SEARCH'

logger = logging.getLogger('')


class _SearchConfig:
    def __init__(self, app_list: list, config_dir: str, index_dir: str):
        self.__app_list = app_list
        # Logging配置: Logger名称
        self.__logger_name = ''
        # 文件默认编码
        self.__default_file_encoding = ''
        # 默认的model索引配置 (str)
        self.__default_model_index_enabled_state = 'true'
        # 默认的字段索引配置 (str)
        self.__default_field_index_enabled_state = 'true'
        # 存放配置的文件夹
        self.__config_dir = config_dir
        # Model索引配置文件路径
        self.__model_index_config_file = ''
        # Model索引配置文件名
        self.__model_index_config_filename = 'models_config.ini'
        # 字段索引配置文件名后缀
        self.__field_config_filename_suffix = '_fields_config.ini'
        # 索引数据保存目录
        self.__index_dir = index_dir
        # 支持的数据库字段类型
        self.__support_fields_type = ['CharField', 'TextField']

    @property
    def app_list(self) -> list:
        return self.__app_list

    @app_list.setter
    def app_list(self, value: list):
        self.__app_list = value

    @property
    def logger_name(self) -> str:
        return self.__logger_name

    @logger_name.setter
    def logger_name(self, value: str):
        self.__logger_name = value

    @property
    def default_file_encoding(self) -> str:
        return self.__default_file_encoding

    @default_file_encoding.setter
    def default_file_encoding(self, value: str):
        self.__default_file_encoding = value

    @property
    def default_model_index_enabled_state(self) -> str:
        return self.__default_model_index_enabled_state

    @default_model_index_enabled_state.setter
    def default_model_index_enabled_state(self, value: str):
        self.__default_model_index_enabled_state = value

    @property
    def default_field_index_enabled_state(self) -> str:
        return self.__default_field_index_enabled_state

    @default_field_index_enabled_state.setter
    def default_field_index_enabled_state(self, value: str):
        self.__default_field_index_enabled_state = value

    @property
    def config_dir(self) -> str:
        return self.__config_dir

    @config_dir.setter
    def config_dir(self, value: str):
        self.__config_dir = value

    @property
    def model_index_config_file(self) -> str:
        return os.path.join(self.config_dir, self.model_index_config_filename)

    @property
    def model_index_config_filename(self) -> str:
        return self.__model_index_config_filename

    @model_index_config_filename.setter
    def model_index_config_filename(self, value: str):
        self.__model_index_config_filename = value

    @property
    def field_config_filename_suffix(self) -> str:
        return self.__field_config_filename_suffix

    @field_config_filename_suffix.setter
    def field_config_filename_suffix(self, value: str):
        self.__field_config_filename_suffix = value

    @property
    def index_dir(self) -> str:
        return self.__index_dir

    @index_dir.setter
    def index_dir(self, value: str):
        self.__index_dir = value

    @property
    def support_fields_type(self) -> list:
        return self.__support_fields_type

    @support_fields_type.setter
    def support_fields_type(self, value: list):
        self.__support_fields_type = value


class _ConfigParser:
    @classmethod
    def init(cls) -> _SearchConfig or None:
        if hasattr(settings, CONFIG_NAME):
            config_dict = settings.__getattr__(CONFIG_NAME)

            if 'APP_LIST' not in config_dict:
                print('未配置 APP_LIST！')
                return None
            if 'CONFIG_DIR' not in config_dict:
                print('未配置 CONFIG_DIR！')
                return None
            if 'INDEX_DIR' not in config_dict:
                print('未配置 INDEX_DIR！')
                return None
            search_config = _SearchConfig(config_dict['APP_LIST'], config_dict['CONFIG_DIR'], config_dict['INDEX_DIR'])

            search_config.logger_name = 'hello'
            setattr(search_config, 'logger_name', 'hello')

            for key, value in config_dict.items():
                attr_name = key.lower()
                logger.debug('set {} to {}'.format(attr_name, value))
                if hasattr(search_config, attr_name):
                    setattr(search_config, attr_name, value)

            return search_config
        else:
            print('未找到 {} 配置！'.format(MODULE_NAME))
            return None


ConfigManager = _ConfigParser.init()
