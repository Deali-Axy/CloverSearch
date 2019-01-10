from django.apps import apps
from .config import ConfigManager
from .indexes import Index, IndexManager
from .processer import character_filter, character_cn_filter, word_segment
import configparser
import logging
import os

logger = logging.getLogger(ConfigManager.logger_name)


def create_model_config():
    """创建model索引配置文件"""
    config_file = open(ConfigManager.model_index_config_file, 'w', encoding=ConfigManager.default_file_encoding)

    # 打开配置文件
    cf = configparser.ConfigParser()
    cf.read(ConfigManager.model_index_config_file, encoding=ConfigManager.default_file_encoding)

    # 遍历配置中的App列表
    for app_name in ConfigManager.app_list:
        app_obj = apps.get_app_config(app_name)
        # 先创建对应的section
        if not cf.has_section(app_name):
            cf.add_section(app_name)
        # 获取App里的所有model类
        for model in app_obj.get_models():
            cf.set(app_name, model.__name__, ConfigManager.default_model_index_enabled_state)
            logger.debug('Init Model Class: {}.{} {}'.format(app_name, model.__name__, model))

    # 保存配置文件
    cf.write(config_file)
    config_file.close()


def create_field_config():
    """创建字段索引配置文件"""

    # 打开Model配置文件
    model_cf = configparser.ConfigParser()
    model_cf.read(ConfigManager.model_index_config_file, encoding=ConfigManager.default_file_encoding)

    # 处理每个model对象里的字段
    for app_name in ConfigManager.app_list:
        app_obj = apps.get_app_config(app_name)
        # 打开各个app的字段配置文件
        field_config_filepath = os.path.join(ConfigManager.config_dir, app_name + ConfigManager.field_config_filename_suffix)
        field_config_file = open(field_config_filepath, 'w+', encoding=ConfigManager.default_file_encoding)
        for model in app_obj.get_models():
            model_name = model.__name__
            if model_cf.getboolean(app_name, model_name):
                # 从配置文件加载数据
                field_cf = configparser.ConfigParser()
                field_cf.read(field_config_filepath)
                if not field_cf.has_section(model_name):
                    field_cf.add_section(model_name)
                for field in model._meta.fields:
                    # 如果字段类型在支持列表里，就添加到配置文件里面
                    if type(field).__name__ in ConfigManager.support_fields_type:
                        logger.debug('Found Model Field: {}.{} {}'.format(app_name, model, field))
                        field_cf.set(model_name, field.name, ConfigManager.default_field_index_enabled_state)
                # 保存配置文件
                field_cf.write(field_config_file)
        # 关闭配置文件
        field_config_file.close()


def build():
    for app_name in ConfigManager.app_list:
        logger.debug("正在建立App:{}的索引".format(app_name))
        field_config_filepath = os.path.join(ConfigManager.config_dir, app_name + ConfigManager.field_config_filename_suffix)
        # 打开配置文件
        cf = configparser.ConfigParser()
        cf.read(field_config_filepath, encoding=ConfigManager.default_file_encoding)

        # 获取App对象
        app_obj = apps.get_app_config(app_name)

        # 清空原有索引数据
        IndexManager.get_instance().indexes.clear()

        # 遍历配置文件
        for section in cf.sections():
            # 通过Model名称获取Model类
            model = app_obj.get_model(section)
            index_fields = []
            # 读取这个Model类要加入索引的所有字段
            for field_name, is_index in cf.items(section):
                if is_index.lower() == 'true':
                    index_fields.append(str(field_name))
                    logger.debug('{}:{} 加入索引'.format(section, field_name))

            # 从数据库读取待索引数据
            for model_obj in model.objects.all():
                index_obj = Index(app_name, section, model_obj.pk)
                for field_name in index_fields:
                    content = model_obj.__dict__[field_name]
                    # 处理关键词，分词处理
                    words_list = word_segment(content)
                    index_obj.keywords[field_name] = words_list
                    # logger.debug('{}:{} 分词处理，共{}词'.format(section, field_name, len(words_list)))
                    # 过滤符号
                    clean_data = character_filter(content)
                    clean_data = character_cn_filter(clean_data)
                    index_obj.clean_data[field_name] = clean_data
                    # logger.debug('{}:{} 数据字符过滤，处理后长度: {}'.format(section, field_name, len(clean_data)))
                # 添加到索引管理器的列表中
                IndexManager.get_instance().add(index_obj)

        # 保存索引数据
        IndexManager.get_instance().save()

# if __name__ == '__main__':
# create_model_config()
# create_field_config()
# build()
# IndexManager.get_instance()
# for field in models.Post._meta.get_fields():
#     if type(field).__name__ in SUPPORT_FIELDS_TYPE:
#         print(field)
#         print(field.name)

# for item in models.Post.objects.all():
#     print(item.__dict__['post_title'])
