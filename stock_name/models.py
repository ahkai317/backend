from django.db import models

# Create your models here.


class StockName(models.Model):
    stock = models.CharField(max_length=10)
    stockName = models.CharField(max_length=20)
    updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.stock
