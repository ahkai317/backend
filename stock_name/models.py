from django.db import models
from django.utils import timezone

# Create your models here.


class StockName(models.Model):
    stock = models.CharField(max_length=32, primary_key=True)
    stockName = models.CharField(max_length=64, default="")
    market = models.CharField(max_length=64, default="")
    securities = models.CharField(max_length=64, default="")
    industry = models.CharField(max_length=64, default="")
    list_date = models.CharField(max_length=64, default="")
    updated = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.stock
