from operator import mod
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from stock_name.models import StockName

# create user


class MyAccountUser(UserManager):
    def create_user(self, email, username, password, gender):
        if not email:
            raise ValueError(_("email is required"))
        if not username:
            raise ValueError(_("username can't be blank"))
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            gender=gender
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            gender='不分性別'
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
# Create your models here.


def gender_validate(value: str) -> ValidationError:
    if not value in ['男生', '女生', '不分性別']:
        raise ValidationError('請輸入正確的性別')


class UserInfo(AbstractBaseUser):
    email = models.EmailField(verbose_name='電子信箱Email',
                              max_length=64, unique=True)
    username = models.CharField(
        verbose_name='使用者名稱', max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='註冊時間', auto_now_add=True)
    last_login = models.DateTimeField(
        verbose_name='最後登入時間', default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=True)
    favoriteStocks = models.ManyToManyField(
        StockName, through='FavoriteStocks')

    gender = models.CharField(
        verbose_name='性別', max_length=10, validators=[gender_validate])

    objects = MyAccountUser()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    # phone = models.CharField(verbose_name='手機', max_length=64)
    # birthday = models.DateField(verbose_name='生日', max_length=64)
    # address = models.CharField(verbose_name='姓名', max_length=200)

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin
    # 如果在views裡面沒有設置permission_classes的話就要家這一行，要不然請求頭Authorization有內的狀況下他就會報錯，因為預設setting裡面的permission檢查會檢查這一行
    # def has_perms(self, perms, obj=None):
    #     return self.is_active

    def has_module_perms(self, add_label):
        return True


class FavoriteStocks(models.Model):
    user = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, related_name='favoriteStock')
    stock = models.ForeignKey(
        StockName, on_delete=models.CASCADE, related_name='favoriteStock')
    updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.user} ---------> {self.stock} ---------> {self.updated}'
