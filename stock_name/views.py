from multiprocessing.dummy import Array
import re
import random
from typing import List
import requests
import pandas as pd
from django.db.models import F
from bs4 import BeautifulSoup
from rest_framework import filters
from urllib.request import Request
from django.http import JsonResponse
from stock_name.filter import StockFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from stock_name.models import StockName, StockDetail
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied
from stock_name.serializers import StockIndustrySerializer, StandardResultsSetPagination, StockDetailSerializer, StockVolumnSerializer
# Create your views here.


def news(request: Request) -> JsonResponse:
    # Yahoo --> /...?keyword=台股&page=page
    keyword = request.GET.get('keyword', default='台股')
    # request.GET.get('keyword')
    page = request.GET.get('page', default='0')
    # request.GET.get('page')
    # user_agent = UserAgent()
    user_agents = [
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    res = requests.get(f'https://tw.news.search.yahoo.com/search?p={keyword}&b={page}1',
                       headers={
                           "Content-Type": "application/json",
                           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                           "Accept-Encoding": "gzip, deflate, br",
                           "Accept-Language": "zh-TW,zh;q=0.9",
                           "Host": "tw.news.search.yahoo.com",  # 目標網站
                           "Sec-Fetch-Dest": "document",
                           "Sec-Fetch-Mode": "navigate",
                           "Sec-Fetch-Site": "none",
                           "Upgrade-Insecure-Requests": "1",
                           # user_agent.random #使用者代理
                           "User-Agent": random.choice(user_agents),
                       })
    soup = BeautifulSoup(res.text, 'html.parser')
    url_list = []
    title_list = []
    source_list = []
    publish_list = []
    content_list = []
    img_list = []

    for i in range(len(list(soup.select('ol.mb-15.reg.searchCenterMiddle  li  ul.compArticleList')))):
        url_list.append(soup.select('ul.compArticleList')[i].select(
            'h4.s-title.fz-16.lh-20')[0].select('a')[0]['href'])
        title_list.append(soup.select('ul.compArticleList')[
                          i].select('h4.s-title.fz-16.lh-20')[0].text)
        source_list.append(soup.select('ul.compArticleList')[
                           i].select('span.s-source.mr-5.cite-co')[0].string)
        publish_list.append(soup.select('ul.compArticleList')[
                            i].select('span.fc-2nd.s-time.mr-8')[0].text)
        content_list.append(soup.select('ul.compArticleList')[
                            i].select('p')[0].text)
        try:
            if i <= 3:
                img_list.append((re.findall(
                    r'/https.*', soup.select('ul.compArticleList')[i].select('img')[0]['src'])[0][1:]))
            else:
                img_list.append((re.findall(r'/https.*', soup.select('ul.compArticleList')[
                                i].select('img')[0]['data-src'])[0][1:]))   #: --> 0517 .isdigit() 只是字串不為空

        except (IndexError, ValueError):
            img_list.append(
                f'https://ww2.money-link.com.tw/images/news/4/{i}.jpg')

    news_dict = pd.DataFrame(
        zip(title_list, url_list, source_list, publish_list, content_list, img_list))
    news_dict.columns = ['title', 'url', 'source', 'publish', 'content', 'img']
    news_dict = news_dict.to_dict('records')
    return JsonResponse(news_dict, safe=False)


class StockViewSet(ReadOnlyModelViewSet):
    queryset = StockDetail.objects.all()
    serializer_class = StockDetailSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_class = StockFilter
    search_fields = ['^stock__stock', '^stock__stockName']
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def search(self, request: Request) -> Response:
        queryset = super().filter_queryset(self.queryset)[:6]
        serializer = StockDetailSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def orderData(self, request: Request) -> Response:
        # get variable from GET Request
        orderColumn = request.GET.get('col')
        reversOrder = request.GET.get('reverse', default='')
        # set the queryset
        self.queryset = self.queryset.extra(
            {'inter': "CAST(%s as DECIMAL(10,2))" % (orderColumn or 'stock')}).order_by('%sinter' % reversOrder)
        queryset = super().filter_queryset(self.queryset)
        # serializer for stock, stockName, industry...
        serializer = StockDetailSerializer(queryset, many=True)
        # get the pagination info and create page
        page = self.paginate_queryset(serializer.data)
        # *****************************************************************
        # original, no data Serializer, only paginationSerializer (另一種寫法)
        # page = self.paginate_queryset(queryset.values("stock__stock", "stock__stockName"))
        # *****************************************************************
        # get the response
        responseData = self.get_paginated_response(page)
        # return a Response, so just return this
        # return responseData
        return responseData

    @action(detail=False, methods=['get'], url_path='getmfs')
    def getFavStockDetail(self, request: Request) -> Response:
        user = request.user
        if user and user.is_authenticated:
            self.queryset = self.queryset.filter(
                stock__favoriteStock__user=user)
            queryset = super().filter_queryset(self.queryset)
            serializer = StockDetailSerializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise PermissionDenied

    @action(detail=False, methods=['get'])
    def industry(self, request: Request) -> Response:
        stockId = request.GET.get('stockId', default='')
        queryset = StockName.objects.filter(stock__icontains=stockId).values(
            'industry').distinct().order_by('industry')
        serializer = StockIndustrySerializer(queryset, many=True)
        outPut = pd.DataFrame(serializer.data)
        outPut = outPut.to_dict('list')
        return Response(outPut)

    @action(detail=False, methods=['get'])
    def volumn(self, request: Request) -> Response:
        queryset = StockDetail.objects.annotate(
            stockId=F('stock__stock')).values('stockId', 'volumn')

        def sort(arr: List) -> List:
            left = []
            right = []
            mid = []

            if len(arr) > 1:
                pivot = int(arr[0]['volumn'])
                for x in arr:
                    if int(x['volumn']) > pivot:
                        left.append(x)
                    if int(x['volumn']) < pivot:
                        right.append(x)
                    if int(x['volumn']) == pivot:
                        mid.append(x)
                return sort(left) + mid + sort(right)
            else:
                return arr
        page = self.paginate_queryset(sort(queryset))
        responseData = self.get_paginated_response(page)
        # serializer = StockVolumnSerializer(queryset, many=True)
        return responseData

    # ==============================================================================================
    # from django.core.paginator import Paginator
    # from collections import OrderedDict
    # 記錄一下另一個寫法（原始自幹）
    # @action(detail=False, methods=['get'])
    # def orderData(self, request: Request) -> JsonResponse:
    #     # get variable from GET Request
    #     orderColumn = request.GET.get('col')
    #     page = request.GET.get('page', default=1)
    #     limit = request.GET.get('page', default=30)
    #     industry = request.GET.get('industry', default='')
    #     reversOrder = request.GET.get('reverse', default='')
    #     # set the queryset
    #     queryset = StockDetail.objects.filter(stock__industry=industry).extra(
    #         {'inter': "CAST(%s as DECIMAL(10,2))" % (orderColumn or 'stock_id')}).order_by('%sinter' % reversOrder)
    #     # serializer for stock, stockName, industry...
    #     serializer = StockDetailSerializer(queryset, many=True)

    #     # setting paginator
    #     paginator = Paginator(serializer.data, limit)
    #     page = paginator.page(page)
    #     # set the url
    #     previous_url = None
    #     next_url = None
    #     # get the url info from request for creating next or previous url
    #     _url_scheme = request.scheme
    #     _host = request.get_host()
    #     _path_info = request.path_info
    #     # creating url
    #     if page.has_previous():
    #         previous_url = '{}://{}{}?industry={}&limit={}&page={}'.format(
    #             _url_scheme, _host, _path_info, industry, limit, page.previous_page_number())
    #     if page.has_next():
    #         next_url = '{}://{}{}?industry={}&limit={}&page={}'.format(
    #             _url_scheme, _host, _path_info, industry, limit, page.next_page_number())
    #     # create a ordered dict for these data
    #     response_dict = OrderedDict([
    #         ('count', len(serializer.data)),
    #         ('next', next_url),
    #         ('previous', previous_url),
    #         ('results', page.object_list)
    #     ])
    #     # return JsonResponse
    #     return JsonResponse(response_dict, status=200, safe=False)
