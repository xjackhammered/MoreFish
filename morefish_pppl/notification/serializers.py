from rest_framework_jwt.settings import api_settings

from users.serializers import UserDetailSerializer

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
import json
from rest_framework import serializers
from assets.serializers import AssetsSerializer
from notification.models import Notifications
from users.serializers import UserDetailSerializer


class NotificationSerializer(serializers.ModelSerializer):
    not_user = UserDetailSerializer()

    # not_created_at = serializers.DateTimeField(format="%Y-%m-%d %I:%M:%S %p")

    class Meta:
        model = Notifications
        fields = (
            'id',
            'not_user',
            'not_time',
            'not_urgency',
            'not_pond',
            'not_message_body',
            'not_warning_msg',
            'not_warning',
            'not_value',
            'not_final',
            'not_color',
        )
