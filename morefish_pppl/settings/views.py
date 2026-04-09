from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import AppVersion
from .serializers import AppVersionSerializer


class AppVersionList(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = AppVersion.objects.all()
    serializer_class = AppVersionSerializer
