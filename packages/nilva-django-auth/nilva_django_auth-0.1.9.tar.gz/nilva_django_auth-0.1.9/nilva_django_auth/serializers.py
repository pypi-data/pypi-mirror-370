from rest_framework import serializers

from nilva_django_auth.models import UserSession


class SessionSerializer(serializers.ModelSerializer):
    """
    Serializer for user sessions.
    """
    os = serializers.CharField(read_only=True)
    device_brand = serializers.CharField(read_only=True)
    device_model = serializers.CharField(read_only=True)
    device_family = serializers.CharField(read_only=True)
    is_mobile = serializers.BooleanField(read_only=True)
    browser = serializers.CharField(read_only=True)
    last_online = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = UserSession
        fields = [
            'user_agent',
            'ip_address',
            'created_at',
            'os',
            'device_brand',
            'device_model',
            'device_family',
            'is_mobile',
            'browser',
            'last_online',
            'is_current',
        ]
        read_only_fields = fields

    def get_last_online(self, obj):
        return obj.last_activity.isoformat()

    def get_is_current(self, obj: UserSession):
        current_jti = self.context.get('current_jti')
        jti = str(obj.jti)

        return jti == current_jti
