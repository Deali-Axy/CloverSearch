# CloverSearch全文检索框架
## 简介
之前试过HayStack+Whoosh的方案，但是配置麻烦，而且对于接口调用的支持也不友好，
看了一下文档看得云里雾里，索性自己实现一个全文检索功能，其实也不复杂。

## 基本逻辑
1. 构建索引
    1. 运行创建model索引配置文件
    2. 配置哪些model需要加入索引
    3. 运行创建字段索引配置文件
    4. 配置哪些model的字段需要加入索引
    5. 运行构建索引
2. 初始化索引
3. 提交搜索请求
4. 获取搜索结果

## 文件结构
### 配置文件
- `models_index_config.ini`: model索引配置文件
- `fields_index_config.ini`: 字段索引配置文件
- `search`: 检索框架目录
    - `index`: 索引数据目录
        - `{ModelName}/{PrimaryKey}`: 索引数据
            - `clean_data.json`: 经过字符过滤后的数据
            - `keywords.json`: 关键词数据

## 代码结构
- `config.py`: 框架配置管理器，用于解析Django配置
- `encoder.py': 用于处理`SearchQueryObject`的`JsonEncoder`
- `index_builder.py`: 索引构建相关
    - `create_model_config()`: 创建model索引配置文件
    - `create_field_config()`: 创建字段索引配置文件
    - `build()`: 构建索引
- `indexes.py`: 索引操作相关
    - `class Index`: 索引类，一个Index对应的就是数据库表里的一行
    - `class IndexManager`: 用于关于索引的类，单例模式
- `processer.py`: 文本处理
    - `word_segment()`: 分词处理
    - `character_filter()`: 字符过滤器
- `query.py`: 搜索请求处理
    - `class SearchQueryObject`: 搜索结果对象
    - `class SearchQuerySet`: 搜索结果集
    - `class SearchQuery`: 搜索处理核心类

## Django配置
### CloverSearch Config
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOVER_SEARCH = {
    # 需要索引的App列表，必填
    'APP_LIST': ['Essay'],
    # 存放配置的目录，必填
    'CONFIG_DIR': os.path.join(BASE_DIR, 'static', 'search', 'config'),
    # 索引数据保存目录，必填
    'INDEX_DIR': os.path.join(BASE_DIR, 'static', 'search', 'index'),
    # Logger名称
    'LOGGER_NAME': 'console',
    # 文件默认编码
    'DEFAULT_FILE_ENCODING': 'utf-8',
    # 默认的model索引配置 (str)
    'DEFAULT_MODEL_INDEX_ENABLED_STATE': 'true',
    # 默认的字段索引配置 (str)
    'DEFAULT_FIELD_INDEX_ENABLED_STATE': 'true',
    # Model索引配置文件名
    'MODEL_INDEX_CONFIG_FILENAME': 'models_config.ini',
    # 字段索引配置文件名后缀，配置需要搜索引擎索引指定model的哪些字段
    'FIELD_CONFIG_FILENAME_SUFFIX': '_fields_config.ini',
    # 支持的数据库字段类型
    'SUPPORT_FIELDS_TYPE': ['CharField', 'TextField']
}
```

### Logging 日志配置
>注意：配置了名为`console`的logger才可以看到索引构建过程或者搜索详细过程的输出。
```python
import os
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s] %(message)s'}
        # 日志格式
    },
    'filters': {
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
```

## manage.py 命令
> 注意！首次使用搜索引擎时顺序不可以颠倒，一定要创建配置，并且配置了需要加入检索的字段后才可以建立索引。
```bash
# 扫描所有model，并且创建model配置
python manage.py scan_models
# 扫描所有开启索引功能model里的字段，并且创建field配置
python manage.py scan_fields
# 建立索引
python manage.py build_index
```