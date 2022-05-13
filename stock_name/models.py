from cgi import print_exception
from django.db import models
from django.utils import timezone
from numpy import require

# Create your models here.


class StockName(models.Model):
    stock = models.CharField(max_length=32, unique=True)
    stockName = models.CharField(max_length=64, default="")
    industry = models.CharField(max_length=64, default="")
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.stock)


class StockDetail(models.Model):
    stock = models.ForeignKey(
        'StockName', on_delete=models.PROTECT, related_name='stockDetail')
    price = models.CharField(max_length=16, verbose_name='股價', default="")
    ud = models.CharField(max_length=16, verbose_name='漲跌', default="")
    udpercent = models.CharField(max_length=16, verbose_name='漲跌幅', default="")
    open = models.CharField(max_length=16, verbose_name='開盤價', default="")
    yesterday = models.CharField(max_length=16, verbose_name='昨收價', default="")
    high = models.CharField(max_length=16, verbose_name='最高價', default="")
    low = models.CharField(max_length=16, verbose_name='最低價', default="")
    volumn = models.CharField(max_length=16, verbose_name='交易量', default="")
    updated = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.stock.stock)
