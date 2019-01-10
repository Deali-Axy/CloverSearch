from .config import ConfigManager
import jieba
import logging

# 字符过滤器
CHARACTER_FILTER = [',', '.', '?', '!', '<', '>', ':', ';', '\\', '/', '|', '[', ']', '{', '}', '-', '=', '+', '-',
                    '_', '(', ')', '*', '&', '^', '%', '$', '#', '@', '`', '~']
CHARACTER_CN_FILTER = ['，', '。', '？', '《', '》', '：', '；', '“', '”', '‘', '’', '【', '】', '——', '！', '……', '￥', '（',
                       '）', '、']

logger = logging.getLogger(ConfigManager.logger_name)


def word_segment(data: str) -> list:
    """分词：句子->列表"""
    try:
        return jieba.lcut(data)
    except Exception as e:
        logger.error(e)
        return []


def character_filter(data: str) -> str:
    """英文字符过滤"""
    output = data
    for item in CHARACTER_FILTER:
        output = output.replace(item, '')
    return output


def character_cn_filter(data: str) -> str:
    """中文字符过滤"""
    output = data
    for item in CHARACTER_CN_FILTER:
        output = output.replace(item, '')
    return output
