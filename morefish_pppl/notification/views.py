import sys
from datetime import datetime, timedelta

from django.shortcuts import render

# Create your views here.
from pytz import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Avg
from device.models import Device

from helper import unique
from notification.serializers import NotificationSerializer
from users.models import Phone
from notification.models import Notifications
from dateutil import parser
from django.db.models import Q


# class FAQList(APIView):
#     permission_classes = (AllowAny,)
#
#     def get(self, request):
#         faq_info = FAQ.objects.all().values().order_by('id')
#         response = {
#             'success': 'True',
#             'status code': status.HTTP_200_OK,
#             'message': 'FAQ list',
#             'data': faq_info
#         }
#         print("line 26", faq_info)
#         return Response(response, status=status.HTTP_201_CREATED)

# notification block Today list
class UserWiseTodayNotificationList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        notification_list = []
        today = datetime.today().date()
        print("line 44", today)
        today_notification_info = Notifications.objects.filter(not_user_id=user_id, not_date=today).order_by(
            '-id').values()[:12]

        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': "Today",
            'data': today_notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)


# notification block Yesterday list
class UserWiseYesterdayNotificationList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        print("line 44", today)
        print("line 45", yesterday)
        yesterday_notification_info = Notifications.objects.filter(not_user_id=user_id, not_date=yesterday).order_by(
            '-id').values()[:12]
        print("line 68", yesterday_notification_info)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': "Yesterday",
            'data': yesterday_notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)

    # notification block date wise list


class UserWiseDateWiseNotificationList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        now = datetime.now()
        today = datetime.today().date()
        yesterday = today - timedelta(days=1)
        random_date_notification_info = Notifications.objects.filter(
            not_user_id=user_id
        ).exclude(
            Q(not_date=today) |
            Q(not_date=yesterday)
        ).order_by(
            '-id'
        ).values()[:10]
        last_notification_date = random_date_notification_info.first()['not_time']
        # print("line 96", today)
        print("line 97", last_notification_date)
        days_ago = now - parser.parse(last_notification_date)
        print('line 100', days_ago.days)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': str(days_ago.days) + " days ago",
            'data': random_date_notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)


class UserWiseNotificationList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        notification_list = []
        one_week_ago = datetime.today() - timedelta(hours=8)
        # print("line 27", one_week_ago)
        notification_info = Notifications.objects.filter(not_user_id=user_id).order_by(
            '-id').values()[:12]

        # serializer = NotificationSerializer(notification_info, many=True)
        # print("line 27", notification_info)
        # i = 0
        # for idx in range(len(notification_info) - 1):
        #     # print("line 34", notification_info[i+1]['not_color'])
        #     # (notification_info[i]['not_color'] == notification_info[i + 1]['not_color']) and
        #     if notification_info[i]['not_warning_msg'] == notification_info[i + 1]['not_warning_msg']:
        #         continue
        #     else:
        #         notification_list.append(notification_info[i])
        #     i = i + 1
        #
        # print("final list", notification_list)

        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Notification list',
            'data': notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)


class UserWiseNotificationHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.data.get("user_id")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        # notification_info = {}
        tomorrow = (datetime.strptime(end_date, '%Y-%m-%d').date()) + timedelta(days=1)
        # print("line 81", tomorrow)
        notification_info = Notifications.objects.filter(not_user=user_id,
                                                         not_time__range=[start_date, tomorrow]).values()
        # notification_info = Notifications.objects.all().order_by('-id').values()[:9]
        # serializer = NotificationSerializer(notification_info, many=True)
        # print("line 83", notification_info)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'message': 'Notification History',
            'data': notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)

class UserWiseDeviceWiseNotificationList(APIView):
    permission_classes = (IsAuthenticated,)


    def get(self, request):
        requesting_user = request.user.id
        asset_id = request.query_params.get('asset_id')
        print("asset id ->", asset_id)
        # Retrieve device_id based on asset_id
        device = Device.objects.filter(dev_asset=asset_id).first()
        if device:
            device_id = device.id
            print("Device ID ->", device_id)
            notification_info = Notifications.objects.filter(not_user_id=requesting_user, dev=device_id).order_by(
                '-id').values()[:24]

            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'Notification list',
                'data': notification_info
            }
            return Response(response)
        else:
            response = {
                'success': 'False',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Device not found for the provided asset ID',
                'data': []
            }
            return Response(response)

class UserWiseDeviceWiseNotificationHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.user.id
        asset_id = request.data.get("asset_id")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")

        # Retrieve the device_id from the asset_id
        device = Device.objects.filter(dev_asset=asset_id).first()
        if device is None:
            response = {
                'success': 'False',
                'status_code': status.HTTP_400_BAD_REQUEST,
                'message': 'Device not found for the given asset_id.',
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        device_id = device.id

        tomorrow = (datetime.strptime(end_date, '%Y-%m-%d').date()) + timedelta(days=1)
        notification_info = Notifications.objects.filter(not_user_id=user_id,
                                                         dev=device_id,
                                                         not_time__range=[start_date, tomorrow]).values()

        response = {
            'success': 'True',
            'status_code': status.HTTP_200_OK,
            'message': 'Notification History',
            'data': notification_info
        }
        return Response(response, status=status.HTTP_201_CREATED)