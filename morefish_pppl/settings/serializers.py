# androidapp/serializers.py

from rest_framework import serializers
from .models import AppVersion


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = ['version_number', 'release_date']
