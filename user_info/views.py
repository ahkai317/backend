
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from user_info.models import UserInfo, Favorite

from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from user_info.serializers import UserRegisterSerilizer, FavoriteSerializer, FavoriteListSerializer
from user_info.permission import IsSelfOrReadOnly



# ============================================================

from rest_framework.decorators import action

class UserModelViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserRegisterSerilizer
    # lookup_field = 'username'

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
            content = {'detail': '此用戶沒有權限'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)

class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()
    def get_serializer_class(self):
        if self.action == 'list':
            return FavoriteListSerializer
        else:
            return FavoriteSerializer

    @action(detail=False, methods=['get'])
    def getfavoritelist(self, request):
        if (request.user and request.user.is_authenticated):
            queryset = Favorite.objects.filter(user=request.user)
            serializer = self.get_serializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            content = {'detail': 'Authenticated not provided'}
            return Response(content, status=status.HTTP_403_FORBIDDEN)

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