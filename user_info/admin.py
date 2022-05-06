from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user_info.models import UserInfo
# Register your models here.

class AccountAdmin(UserAdmin):
  list_display = ('email', 'username', 'date_joined', 'last_login', 'is_admin', 'is_staff')
  search_fields = ('email', 'username')
  readonly_fields = ('id', 'date_joined', 'last_login')

  filter_horizontal = ()
  list_filter = ('is_admin',)
  fieldsets = ()

admin.site.register(UserInfo, AccountAdmin)
