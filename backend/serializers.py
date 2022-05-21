from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError


class LogOutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': '此為無效的Token'
    }

    def validate(self, attrs):
        self.refreshToken = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.refreshToken).blacklist()
        except TokenError:
            self.fail('bad_token')
