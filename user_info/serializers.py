from attr import field
from rest_framework import serializers
from traitlets import default
from user_info.models import FavoriteStocks, UserInfo
from stock_name.models import StockName
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator

# serializer 內會自動生成驗證器去驗證你傳進來的資料


class UserRegisterSerilizer(serializers.ModelSerializer):
    favoriteStocks = serializers.SlugRelatedField(
        queryset=StockName.objects.all(), many=True, slug_field='stock')

    class Meta:
        model = UserInfo
        fields = ["id", "email", "username", "gender",
                  "password", "last_login", "date_joined", "favoriteStocks"]
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'email': {'validators': [UniqueValidator(queryset=UserInfo.objects.all(), message='此Email已經有人使用！')]},
            'username': {'validators': [UniqueValidator(queryset=UserInfo.objects.all(), message='此使用者名稱已經有人使用！')]},
            "last_login": {'read_only': True}, "date_joined": {'read_only': True},
            "favoriteStocks": {'read_only': True}
        }

    # def validate(self, attrs):
    #   if attrs.get('password') != attrs.get('password_confirm'):
    #     raise serializers.ValidationError({"password_confirm":'驗證密碼錯誤！'})
    #   attrs.pop('password_confirm')
    #   return attrs

    def create(self, validated_data):
        user = UserInfo.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class FavoriteStockSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        queryset=UserInfo.objects.all(), many=False, slug_field='username')
    stock = serializers.SlugRelatedField(
        queryset=StockName.objects.all(), many=False, slug_field='stock')

    class Meta:
        model = FavoriteStocks
        fields = "__all__"
