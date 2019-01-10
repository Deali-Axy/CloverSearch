from django.core.paginator import Paginator

from .query import SearchResultObject
from json import JSONEncoder
from datetime import datetime, date


class SearchQueryObjectEncoder(JSONEncoder):
    """
    对SearchQueryObject对象json序列化的处理。
    还包括日期格式的处理
    """

    def default(self, o):
        if isinstance(o, SearchResultObject):
            return o.__dict__
        elif isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        elif isinstance(o, Paginator):
            return None
        return super(SearchQueryObjectEncoder, self).default(o)
