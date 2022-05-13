import requests
import pandas as pd
import random
from bs4 import BeautifulSoup
from rest_framework.response import Response
from django.http import JsonResponse
from stock_name.models import StockName
from stock_name.serializers import StockSerializer, StockIndustrySerializer, StandardResultsSetPagination
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from stock_name.filter import StockFilter
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
# Create your views here.


def news(request):
    # Yahoo --> /...?keyword=台股&page=page
    keyword = '台股'
    # request.GET.get('keyword')
    page = '0'
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
    re = requests.get(f'https://tw.news.search.yahoo.com/search?p={keyword}&b={page}1',
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
    soup = BeautifulSoup(re.text, 'html.parser')
    url_list = []
    title_list = []
    source_list = []
    publish_list = []

    img_list = []
    for i in range(len(soup.select('ol.mb-15.reg.searchCenterMiddle  li  ul.compArticleList'))):
        url_list.append(soup.select('ul.compArticleList')[i].select(
            'h4.s-title.fz-16.lh-20')[0].select('a')[0]['href'])
        title_list.append(soup.select('ul.compArticleList')[
            i].select('h4.s-title.fz-16.lh-20')[0].text)
        source_list.append(soup.select('ul.compArticleList')[
            i].select('span.s-source.mr-5.cite-co')[0].string)
        publish_list.append(soup.select('ul.compArticleList')[
                            i].select('span.fc-2nd.s-time.mr-8')[0].text)
        img_list.append(soup.select('ul.compArticleList')
                        [0].select('img')[0]['src'])
    news_dict = pd.DataFrame(
        zip(title_list, url_list, source_list, publish_list))
    news_dict.columns = ['title', 'url', 'source', 'publish']
    news_dict = news_dict.to_dict('records')
    return JsonResponse(news_dict, safe=False)


class StockViewSet(ReadOnlyModelViewSet):
    queryset = StockName.objects.all()
    serializer_class = StockSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filter_class = StockFilter
    search_fields = ['^stock', '^stockName']
    permission_classes = [AllowAny]

    @action(detail=False, methods=['get'])
    def search(self, request):
        queryset = super().filter_queryset(self.queryset)[:10]
        serializer = StockSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def industry(self, request):
        queryset = StockName.objects.values(
            'industry').distinct().order_by('industry')
        serializer = StockIndustrySerializer(queryset, many=True)
        return Response(serializer.data)
