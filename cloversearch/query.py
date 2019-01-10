from enum import Enum, unique
from .config import ConfigManager
from .indexes import IndexManager, Index
from .processer import character_filter, character_cn_filter, word_segment

import logging
import re

logger = logging.getLogger(ConfigManager.logger_name)


@unique
class SearchResultObjectType(Enum):
    """
    搜索结果匹配类型
    """
    FullMatch = 1,
    WordMatch = 2,
    RegexMatch = 3


class SearchResultObject:
    """
    搜索结果对象，一个搜索结果对象对应一条数据
    """
    index = None  # Index对象
    raw = ''  # 输入的原始关键词
    keyword_count = 0  # 输入的关键词数量
    matching_type = None  # 匹配的类型
    matching_count = 0  # 匹配到的词数量
    matching_score = 0  # 匹配度，全匹配则为1；词匹配：输入的关键词在索引中出现的次数 / 总关键词数量

    def __init__(self, index: Index, raw: str, keyword_count: int, matching_type: SearchResultObjectType):
        """
        搜索结果对象初始化
        :param index: 索引对象
        :param raw: 输入的匹配内容
        :param keyword_count: 关键词数量，用于计算词模式的匹配度
        :param matching_type: 匹配的类型
        """
        self.index = index
        self.raw = raw
        self.keyword_count = keyword_count
        self.matching_type = matching_type

    @property
    def __id__(self):
        return self.index.__id__

    def __repr__(self):
        return '<SearchQueryObject {}:{} index:{} raw:{} matching_score:{}>'. \
            format(self.index.model_name,
                   self.index.primary_key,
                   self.index,
                   self.raw,
                   self.matching_score)

    @property
    def __dict__(self) -> dict:
        """
        获取序列化的搜索结果对象，dict结构
        :return: dict
        """
        model_dict = self.index.get_model_instance().__dict__
        # 删掉无法序列化的字段
        if '_state' in model_dict:
            del model_dict['_state']

        data_dict = {
            'model_name': self.index.model_name,
            'primary_key': self.index.primary_key,
            'model_data': model_dict
        }
        return data_dict


class SearchResultSet:
    """
    搜索结果集，用于传递、管理搜索结果对象，API方面部分参考了Django ORM的设计
    """

    objects = []  # SearchResultObject 对象列表

    def __init__(self):
        self.objects = list()

    def add(self, obj: SearchResultObject) -> None:
        """
        向搜索结果集中添加搜索结果对象
        :param obj: 搜索结果对象
        :return: None
        """
        self.objects.append(obj)

    def extend(self, query_set) -> None:
        """
        对搜索结果集进行扩展，一般用于多种匹配方式得到的结果集的合并处理
        :param query_set: SearchResultSet 搜索结果集对象
        :return: None
        """
        self.objects.extend(query_set.objects)

    @property
    def all(self) -> list:
        """
        获取搜索结果列表
        :return: list
        """
        # 使用lambda表达式对搜索结果进行排序
        self.objects.sort(key=lambda elem: elem.matching_score, reverse=True)
        return self.objects

    def remove_duplicates(self) -> None:
        """
        删除重复搜索结果
        :return: None
        """
        temp_list = []
        new_objects = self.objects.copy()
        for item in self.objects:
            if item.__id__ in temp_list:
                new_objects.remove(item)
            else:
                temp_list.append(item.__id__)
        self.objects = new_objects

    def print(self) -> None:
        """
        遍历输出所有结果的匹配度
        :return: None
        """
        print('{} 匹配度 {}'.format(item.index.model_name, item.matching_score) for item in self.all)


class SearchQuery:
    """
    搜索处理核心类
    """

    @classmethod
    def query(cls, raw: str, full_match: bool = True, word_match: bool = True, regex_match: bool = False) -> SearchResultSet:
        """
        开始一个搜索请求
        :param full_match: 是否开启全匹配
        :param word_match: 是否开启词匹配
        :param regex_match: 是否开启正则匹配
        :param raw: 输入的原始搜索词
        :return: SearchResultSet
        """
        all_set = SearchResultSet()

        if full_match:
            full_set = cls.full_match(raw)
            all_set.extend(full_set)

        if word_match:
            word_set = cls.word_match(raw)
            all_set.extend(word_set)

        if regex_match:
            # 当输入的搜索关键词长度小于符合正则匹配规则的时候启用正则匹配
            if len(raw) <= 2:
                pattern = r'\w'.join(raw)
                regex_set = cls.regex_match(pattern)
                all_set.extend(regex_set)

        # 去除重复结果
        all_set.remove_duplicates()

        return all_set

    @classmethod
    def full_match(cls, raw: str) -> SearchResultSet:
        """
        全匹配搜索，将原始搜索词与索引数据进行匹配查找
        :param raw: 输入的原始搜索词
        :return: SearchResultSet
        """
        data = character_filter(raw)
        data = character_cn_filter(data)
        # 搜索结果集
        search_set = SearchResultSet()
        for index in IndexManager.get_instance().indexes:
            search_obj = SearchResultObject(index, raw, 1, SearchResultObjectType.FullMatch)
            # 全匹配的匹配度为1
            search_obj.matching_score = 1
            for field_name, clean_data in index.clean_data.items():
                if data in clean_data:
                    search_set.add(search_obj)
                    # 我发现匹配的时候输出这个调试信息很浪费性能！
                    # logger.debug('full_match: {}'.format(search_obj.__repr__()))
                    break
        return search_set

    @classmethod
    def word_match(cls, raw: str) -> SearchResultSet:
        """
        词匹配搜索，将搜索词进行分词处理之后与索引数据（已经进行分词处理）进行匹配查找
        :param raw: 输入的原始搜索词
        :return: SearchResultSet
        """
        # 先对输入的搜索语分词处理
        keywords = word_segment(raw)
        # 搜索结果集
        search_set = SearchResultSet()
        for index in IndexManager.get_instance().indexes:
            search_obj = SearchResultObject(index, raw, len(keywords), SearchResultObjectType.WordMatch)
            for word in keywords:
                # 统计匹配词数量，输入的关键词有多少个出现在索引数据里面
                for field_name, words_list in index.keywords.items():
                    if word in words_list:
                        # 检测到这个关键词的出现，记录下，跳出循环，测试下个关键词
                        search_obj.matching_count += 1
                        break
                # 计算匹配度：匹配词数量 / 总输入关键词数
                search_obj.matching_score = search_obj.matching_count / search_obj.keyword_count
            if search_obj.matching_score > 0:
                # 匹配度大于0才添加到结果集中
                search_set.add(search_obj)

        return search_set

    @classmethod
    def regex_match(cls, pattern: str) -> SearchResultSet:
        """
        正则匹配，在索引的clean_data里做正则匹配
        :param pattern: 正则表达式
        :return: SearchResultSet
        """
        search_set = SearchResultSet()
        for index in IndexManager.get_instance().indexes:
            for field_name, clean_data in index.clean_data.items():
                match_result = re.search(pattern, clean_data)
                if match_result is not None:
                    search_obj = SearchResultObject(index, pattern, 1, SearchResultObjectType.RegexMatch)
                    search_obj.matching_score = 0  # 正则匹配的匹配度接近于0，所以这里取0
                    search_set.add(search_obj)
                    logger.debug('regex_match: {}'.format(search_obj.__dict__))
                    break
        return search_set
