import re
from unittest import result
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator(object):
    def validate(self, password, user=None):
        r = r'(?=.*[a-z])(?=.*[A-Z])(?=.*\d)'
        result = re.match(r, password)
        if not result:
            raise ValidationError(_('密碼需包含大小寫英文及數字'))


class LengthValidator(object):
    def validate(self, password, user=None):
        r = r'^(?=.{6,20}$)'
        result = re.match(r, password)
        if not result:
            raise ValidationError(_('密碼長度需為6-20個字'))


class IllegalCharacterValidator(object):
    def validate(self, password, user=None):
        r = r'(?=.*[\u4e00-\u9fff])'
        result = re.match(r, password)
        if result:
            raise ValidationError(_('密碼中不可包含中文'))
