from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from cloversearch.encoder import SearchQueryObjectEncoder
from cloversearch.query import SearchQuery
from .response import Response
import time


def index(request):
    return render(request, 'search/index.html')


def page_search(request):
    r = {}
    if 'w' not in request.GET:
        return HttpResponseRedirect('/search/page')
    start_time = time.time()
    r['keyword'] = request.GET['w']
    result = SearchQuery.query(request.GET['w'])
    end_time = time.time()
    took_time = end_time - start_time
    r['took_time'] = took_time
    r['result_count'] = len(result.all)
    r['result'] = result.all[0:10]

    return render(request, 'search/result.html', context=r)


def search(request):
    r = Response()
    r.encoder = SearchQueryObjectEncoder
    if 'w' not in request.GET:
        return r.error('NoKeyWord', '未提供搜索关键词')
    start_time = time.time()

    result = SearchQuery.query(request.GET['w'])
    each_page = int(request.GET.get('each_page', '10'))
    page = int(request.GET.get('page', '1'))

    end_time = time.time()
    took_time = end_time - start_time

    if len(result.all) > 0:
        paginator = Paginator(result.all, each_page)
        current_page = paginator.page(page)
        r['result'] = current_page.object_list
    else:
        r['result'] = []

    r['took_time'] = took_time
    r['result_count'] = len(result.all)

    return r.ok('Search Request, Keyword:{}'.format(request.GET['w']))
