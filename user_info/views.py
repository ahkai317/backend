from rest_framework import status
from rest_framework.response import Response
from stock_name.models import StockName
from user_info.models import FavoriteStocks, UserInfo
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from user_info.serializers import UserRegisterSerilizer, FavoriteStockSerializer
from user_info.permission import IsSelfOrReadOnly


# ============================================================

from rest_framework.decorators import action


class UserModelViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserRegisterSerilizer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsSelfOrReadOnly]

        return super().get_permissions()

    def get_queryset(self):
        return UserInfo.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def adminInfo(self, request):
        if (request.user and request.user.is_superuser):
            queryset = UserInfo.objects.all()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            raise PermissionDenied

    @action(detail=False, methods=['post'], url_path='mfs')
    def modifyFavStock(self, request):
        user = request.user
        stock = request.POST.get('remove') or request.POST.get('add')
        if user and user.is_authenticated:
            try:
                if request.POST.get('remove'):
                    stock = StockName.objects.get(
                        stock=stock)
                    user.favoriteStocks.remove(stock)
                    result = {'detail': '移除成功'}
                else:
                    stock = StockName.objects.get(
                        stock=stock)
                    user.favoriteStocks.add(stock)
                    queryset = FavoriteStocks.objects.filter(
                        user=user, stock=stock)
                    serializer = FavoriteStockSerializer(queryset, many=True)
                    result = serializer.data
                return Response(result, status=status.HTTP_201_CREATED)
            except ObjectDoesNotExist:
                raise ValidationError(
                    '股票代號 \'%s\' 不存在' % stock)
        raise PermissionDenied

    # @action(detail=False, methods=['get'], url_path='getmfs')
    # def getFavStock(self, request):
    #     user = request.user
    #     if user and user.is_authenticated:
    #         queryset = FavoriteStocks.objects.filter(user=user)
    #         serializer = FavoriteStockSerializer(queryset)
    #         return Response(serializer.data)
    #     raise PermissionDenied


# ======================== 自己玩玩 ===========================
# from django.contrib import auth
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import get_user_model

# @csrf_exempt
# def UserLoginViewSet(request):
#     if request.method not in ['POST']:
#         return JsonResponse({'detail':"此請求方法不被允許%s" % request.method}, status=405)
#     else:
#         username_field = get_user_model().USERNAME_FIELD
#         username = request.POST.get('email', None)
#         password = request.POST.get('password', None)
#         error = {}
#         if not username:
#             error[username_field] = ['此欄位為必填']
#         if not password:
#             error['password'] = ['此欄位為必填']

#         if error.values():
#             return JsonResponse(error, status=401)

#         authenticate_kwargs = {
#             username_field: username,
#             'password': password,
#         }
#         user = auth.authenticate(**authenticate_kwargs)
#         if user is not None and user.is_active:
#             request.session['user_info'] = authenticate_kwargs
#             request.session.set_expiry(2592000) # 2592000設定一個月
#             return JsonResponse({'detail': '登入成功'}, status=200)
#         else:
#             return JsonResponse({'detail': '帳號密碼有誤'}, status=401)
