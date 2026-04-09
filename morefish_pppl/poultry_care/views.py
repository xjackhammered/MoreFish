"""
poultry_care/views.py
API views for the Poultry Care section.
Mirrors the structure of device/views.py from the fish farm.
"""
import sys
import traceback

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .helper import get_daily_data, get_weekly_data, get_monthly_data, get_yearly_data
from .models import Device, PoultryFarm, SensorConfig, PoultryNotification
from .serializers import (
    ChartQuerySerializer,
    DeviceLatestReadingSerializer,
    FarmDashboardSerializer,
    FarmIdParamSerializer,
    PoultryFarmListSerializer,
    PoultryNotificationSerializer,
    SensorConfigSerializer,
)
from .service import PoultryService


# ─── FARM LIST ────────────────────────────────────────────────────────────────
class PoultryFarmListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company_id = request.GET.get('company_id', None)
        farms = PoultryService.get_farm_list(user=request.user, company_id=company_id)
        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Farm list',
            'data': list(farms),
        })


# ─── FARM DASHBOARD ───────────────────────────────────────────────────────────
class PoultryFarmDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        param_serializer = FarmIdParamSerializer(data=request.query_params)
        param_serializer.is_valid(raise_exception=True)
        farm_id = param_serializer.validated_data['farm_id']

        try:
            dashboard_data = PoultryService.get_farm_dashboard(farm_id=farm_id, user=request.user)
        except PoultryFarm.DoesNotExist:
            return Response({
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': f'No farm found with id={farm_id}',
                'data': {},
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': str(e),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = FarmDashboardSerializer(data=dashboard_data)
        serializer.is_valid(raise_exception=True)

        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Farm dashboard data',
            'data': serializer.data,
        })


# ─── SENSOR LIST ──────────────────────────────────────────────────────────────
class PoultrySensorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        device_id = request.GET.get('device_id')
        if not device_id:
            return Response({'success': False, 'message': 'device_id is required'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            configs = SensorConfig.objects.filter(device_id=device_id).select_related('sensor')
            serializer = SensorConfigSerializer(configs, many=True)
            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Sensor list',
                'data': serializer.data,
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── CHART DATA ───────────────────────────────────────────────────────────────
class PoultryDataGraphView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = ChartQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        farm_id    = query.validated_data['farm_id']
        sensor_key = query.validated_data['sensor_key']
        range_type = query.validated_data['type']

        try:
            if range_type == 'daily':
                result = get_daily_data(farm_id=farm_id, sensor_name=sensor_key)
            elif range_type == 'weekly':
                result = get_weekly_data(farm_id=farm_id, sensor_name=sensor_key, range_type='weekly')
            elif range_type == 'monthly':
                result = get_monthly_data(farm_id=farm_id, sensor_name=sensor_key, date_range=30)
            elif range_type == 'half-yearly':
                result = get_monthly_data(farm_id=farm_id, sensor_name=sensor_key, date_range=180)
            elif range_type == 'yearly':
                result = get_yearly_data(farm_id=farm_id, sensor_name=sensor_key, range_type='yearly')
            else:
                result = get_daily_data(farm_id=farm_id, sensor_name=sensor_key)

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'Sensor chart data',
                'data': result,
            })
        except Exception as e:
            traceback.print_exc()
            return Response(
                {'error': f'line {sys.exc_info()[-1].tb_lineno}: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ─── LATEST READINGS (quick snapshot) ────────────────────────────────────────
class PoultryLatestReadingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(user=request.user).select_related('farm')
        serializer = DeviceLatestReadingSerializer(devices, many=True)
        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Device latest readings',
            'data': serializer.data,
        })


# ─── NOTIFICATIONS ────────────────────────────────────────────────────────────
class PoultryNotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = PoultryNotification.objects.filter(
            user=request.user
        ).select_related('device', 'sensor')[:50]

        serializer = PoultryNotificationSerializer(notifications, many=True)
        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': 'Notifications',
            'data': serializer.data,
        })


class PoultryNotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ids = request.data.get('ids', None)
        qs  = PoultryNotification.objects.filter(user=request.user)
        if ids:
            qs = qs.filter(id__in=ids)
        updated = qs.update(is_read=True)
        return Response({
            'success': True,
            'status_code': status.HTTP_200_OK,
            'message': f'{updated} notification(s) marked as read.',
        })