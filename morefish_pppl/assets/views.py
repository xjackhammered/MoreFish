import sys

import requests
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from users.models import FCM, Phone, User
from assets.serializers import AssetsManualSerializer, AssetsSerializer, AssetsListSerializer, UserWiseAssetsListSerializer
from assets.models import AssetsProperties
from pyfcm import FCMNotification
from notification.models import Notifications
push_service = FCMNotification(api_key="AAAAreYfHOo:APA91bHArYaU6wXsdjoPupAcsthPUKmCHV6E1dMvYdc5a-4hYPU0s9cKmCMH6QkthisgJpfOH8bWcxYeW2eVQsdOSjqUuRYmP_78VZ8FDmTv-ZERfclaJ9-xkoBSA7YhfluRZvzXqDjd")


class AssetsList(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        try:
            assets_info = AssetsProperties.objects.filter(ast_user__id=None)
            assets_list = AssetsListSerializer(assets_info, many=True).data
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Assets list',
                'data': assets_list
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)


class AssetsUserWiseList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            user_info = User.objects.filter(is_superuser=0)
            assets_list = UserWiseAssetsListSerializer(user_info, many=True).data
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'User Wise Assets list',
                'data': assets_list
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)


class AssetsAssignToUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            asset_ids = request.data.get('asset_ids')
            user_id = request.data.get('user_id')
            if asset_ids:
                assets_ids = asset_ids.split(',')
                for asset_id in assets_ids:
                    asset_info = AssetsProperties.objects.filter(id=asset_id).first()
                    if asset_info:
                        AssetsProperties.ast_user.through.objects.create(assetsproperties_id=asset_id, user_id=user_id)
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Assets Assigned'
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)



class AssetUnassetsAssignToUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            asset_id = request.data.get('asset_id')
            user_id = request.data.get('user_id')
            if asset_id:
                asset_info = AssetsProperties.objects.filter(id=asset_id).first()
                if asset_info:
                    AssetsProperties.ast_user.through.objects.filter(assetsproperties_id=asset_id, user_id=user_id).delete()
            response = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'Assets Unassigned'
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)




class SendMessageToOwner(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            message = request.data.get('message')
            ast_id = int(request.data.get('asset_id'))
            assets_info = AssetsProperties.objects.filter(id=ast_id).first()

            user_info = AssetsProperties.ast_user.through.objects.filter(assetsproperties_id=assets_info.id)
            for user_data in user_info:
                fcm_info = FCM.objects.filter(user_id=user_data.user_id).first()
                if fcm_info:
                    registration_id = fcm_info.token
                else:
                    registration_id = ''
                AssetsProperties.objects.filter(id=ast_id).update(ast_comments=message)
                message_title = "Message from "+user_data.user.first_name+" "+user_data.user.last_name

                message_body = message

                result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title,
                                                           message_body=message_body)
                if user_data.user.is_notification == 1:
                    Notifications.objects.create(not_message_title=message_title, not_message_body=message_body, not_assets_id=ast_id, not_status=0)
                # OTP send
                is_phone = Phone.objects.filter(user_id=user_data.user_id).first()
                if is_phone:
                    phone = is_phone.phn_cell
                    if len(phone) > 11:
                        phone_number = phone[-11:]
                    else:
                        phone_number = phone
                    url = "http://dma.com.bd:8888/send/sms"
                    message = {'number': phone_number, 'message': message_body}
                    if user_data.user.is_message == 1:
                        r = requests.post(url, message)
                response = {
                    'success': 'True',
                    'status code': status.HTTP_200_OK,
                    'message': result
                }
                return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)

class AssetsUnderUser(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = request.GET.get('user_id')
        company_id = request.GET.get('company_id')

        if company_id:
            queryset = AssetsProperties.objects.filter(company=company_id)
        else:
            queryset = AssetsProperties.objects.filter(ast_user=user_id)

        assets_list = AssetsManualSerializer(queryset, many=True).data
        initial_asset = {
            'id': 0,
            'ast_name': '--Select a pond--'
        }
        assets_list.insert(0, initial_asset)

        response = {
            'success': 'True',
            'status_code': status.HTTP_200_OK,
            'message': 'Assets assigned',
            'data': assets_list
        }

        return Response(response, status=status.HTTP_200_OK)


class AssetsUnderUserForReport(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user_id = request.GET.get('user_id')
        company_id = request.GET.get('company_id')

        if company_id:
            queryset = AssetsProperties.objects.filter(company=company_id)
        else:
            queryset = AssetsProperties.objects.filter(ast_user=user_id)

        assets_list = AssetsManualSerializer(queryset, many=True).data

        initial_asset = {
            'id': 0,
            'ast_name': '--Select a pond--'
        }
        assets_list.insert(0, initial_asset)

        response = {
            'success': 'True',
            'status_code': status.HTTP_200_OK,
            'message': 'Assets assigned',
            'data': assets_list
        }

        all_devices_response = {
            'company_id': None,
            'ast_name': 'All Ponds',
        }
        assets_list.append(all_devices_response)

        return Response(response, status=status.HTTP_200_OK)