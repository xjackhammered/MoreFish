import json
import random
import sys
import time
import traceback
from django.http import HttpRequest

import requests
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password
# email
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from morefish_pppl.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.authtoken.models import Token

# Create your views here.
from rest_framework import status, generics
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.auth import EmailOrUsernameModelBackend
from users.models import Company, User, Phone, FCM, OTP
from users.serializers import CompanyListSerializer, LoginResponseSerializer, LoginSerializer, JWT_PAYLOAD_HANDLER, JWT_ENCODE_HANDLER, RegisterSerializer, \
    PhoneCreateSerializer, RegistrationSerializer, UserDetailSerializer, UpdateUserDetailSerializer, ChangePasswordSerializer
from drf_spectacular.utils import extend_schema
from core.schema import generate_response_schema
from django.contrib.auth import authenticate

class RefreshToken(APIView):
    permission_classes = [AllowAny]
    def get(self,request:HttpRequest):
        user = request.GET.get('id')
        jwt_token ,created= Token.objects.get_or_create(user_id=user)
        
        return Response({
            'success':'True',
            'status_code':status.HTTP_200_OK,
            'token':jwt_token.key
        })
# user register
class Register(APIView):
    serializer_class = RegistrationSerializer
    phone_serializer = PhoneCreateSerializer
    
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: generate_response_schema(
                success='True',
                status_code=201,
                message='Registration has been Successful.',
                serializer_instance=RegisterSerializer()  # Instantiate the serializer
            ),
            status.HTTP_403_FORBIDDEN: generate_response_schema(
                success=True,
                status_code=403,
                message="Email Already Exists"
            )
        }
    )

    def post(self, request):
        try:
            reg_serializer = self.serializer_class(data=request.data)
            reg_serializer.is_valid(raise_exception=True)
            if not User.objects.filter(usr_email=request.data['usr_email']):
                serializer = RegisterSerializer(data=reg_serializer.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

                user_id = UserDetailSerializer(User.objects.get(usr_email=request.data['usr_email'])).data['id']
                user = User.objects.get(usr_email=request.data['usr_email'])
                user.is_active=False
                user.save()
                # phone save
                new_phone = self.phone_serializer(
                    data={'user': user_id,
                          'phn_cell': request.data['phone']})
                new_phone.is_valid(raise_exception=True)
                new_phone.save()
                response = {
                    'success': 'True',
                    'status_code': status.HTTP_201_CREATED,
                    'message': 'Registration has been Successful.',
                    'data': serializer.data
                }

                return Response(response)
            else:
                response = {
                    'success': 'True',
                    'status_code': status.HTTP_403_FORBIDDEN,
                    'message': 'Email Already Exist'
                }
                return Response(response)
        except Exception as e:
           
            traceback.print_exc()
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    
class CompanyList(APIView):
    permission_classes = (AllowAny,)
    @extend_schema(
        responses={
            status.HTTP_200_OK: generate_response_schema(
                success='True',
                status_code=200,
                message='Company List',
                serializer_instance=CompanyListSerializer()  # Instantiate the serializer
            ),
        }
    )
    def get(self,request):
        company_list = list(Company.objects.all().values("id","name"))
        company_list.insert(0,{'id':0,'name':'--Please Select--'})
        
        company_list_serialized = CompanyListSerializer(data=company_list,many=True)
        company_list_serialized.is_valid(raise_exception=True)
        return Response({
            "data":company_list_serialized.data,
            "success":"True",
            "status_code":status.HTTP_200_OK,
            "message":"Company List"
        })

class Login(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer()

    @extend_schema(
        responses={
            status.HTTP_200_OK: generate_response_schema(
                success=True,
                status_code=status.HTTP_200_OK,
                message='User logged in successfully',
                serializer_instance=LoginResponseSerializer()
            ),
            status.HTTP_404_NOT_FOUND: generate_response_schema(
                success=False,
                status_code=status.HTTP_404_NOT_FOUND,
                message="Invalid Credentials"
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR: generate_response_schema(
                success=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message='Internal Server Error'
            ),
            status.HTTP_403_FORBIDDEN: generate_response_schema(
                success=False,
                status_code=status.HTTP_403_FORBIDDEN,
                message='User is not approved yet. Please wait for admin approval.'
            )
        }
    )
    def post(self, request):
        valid_login = LoginSerializer(data=request.data)
        valid_login.is_valid(raise_exception=True)
        email = request.data.get('usr_email')
        password = request.data.get('password')

        invalid_cred_response = {
                'success': False,
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Invalid Credentials'
            }
        
        try:
            user = User.objects.get(usr_email=email)
        except User.DoesNotExist:
            return Response(invalid_cred_response, status=status.HTTP_404_NOT_FOUND)
        auth_user = authenticate(username=user.username,password=password)
        if auth_user is None:
            return Response(invalid_cred_response, status=status.HTTP_404_NOT_FOUND)

        if auth_user.is_active == 0:
            return Response({
                'success': False,
                'status_code': status.HTTP_403_FORBIDDEN,
                'message': 'Your account has been registered but not been approved yet. Please wait for admin approval.'
            }, status=status.HTTP_403_FORBIDDEN)
        try:
            jwt_token, created = Token.objects.get_or_create(user=auth_user)
            update_last_login(None, auth_user)
            
            
            user_detail_data = UserDetailSerializer(instance=auth_user)
            login_response_data = {
                "user_id": auth_user.id,
                "token": jwt_token.key,
                "user_data": user_detail_data.data
            }

            # Create the LoginResponseSerializer instance with raw data
            user_data = LoginResponseSerializer(data=login_response_data)
            user_data.is_valid(raise_exception=True)

            return Response({
                'success': True,
                'status_code': status.HTTP_200_OK,
                'message': 'User logged in successfully',
                'data': user_data.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            traceback.print_exc()
            return Response({
                'success': False,
                'status_code': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'message': 'Internal Server Error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class UserDetails(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        try:
            user_info = User.objects.get(id=pk)
            serializer = UserDetailSerializer(user_info)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'User Details',
                'data': serializer.data
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)

    def post(self, request, pk):
        try:
            print(request.data)
            serializer = UpdateUserDetailSerializer(request.user, data=request.data)

            if serializer.is_valid():
                serializer.save()

                if Phone.objects.filter(user=pk).exists():

                    Phone.objects.filter(user=pk).update(
                        phn_business={True: request.data.get('phn_business'), False: ''}[
                            request.data.get('phn_business') is not None],
                        phn_cell={True: request.data.get('phn_cell'), False: ''}[
                            request.data.get('phn_cell') is not None],
                        phn_home={True: request.data.get('phn_home'), False: ''}[
                            request.data.get('phn_home') is not None])

                else:
                    phn_data = {
                        'user': pk,
                        'phn_cell': request.data.get('phn_cell'),
                        'phn_business': {True: request.data.get('phn_business'), False: ''}[
                            request.data.get('phn_business') is not None],
                        'phn_home': {True: request.data.get('phn_home'), False: ''}[
                            request.data.get('phn_home') is not None]
                    }
                    print(phn_data)
                    new_phone = PhoneCreateSerializer(data=phn_data)
                    new_phone.is_valid(raise_exception=True)
                    new_phone.save()
            else:
                print(serializer.errors)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'User Update Successful',
                'data': UserDetailSerializer(User.objects.get(pk=pk)).data
            }
            return Response(response, status=status.HTTP_201_CREATED)

        except Exception as e:
            traceback.print_exc()
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)


class UserList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            farmers = UserDetailSerializer(User.objects.filter(is_superuser=0), many=True).data
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'User list',
                'data': farmers
            }
            return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), str(e)
            return Response(response, status=status.HTTP_201_CREATED)


# user logout
class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        # using Django logout
        logout(request)
        content = {
            'success': True,
            'status_code': status.HTTP_201_CREATED,
            'message': 'logout Successfully',
        }
        return Response(content)


class ChangePassword(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer
    model = User

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                response = {
                'status': 'success',
                'code': status.HTTP_400_BAD_REQUEST,
                'message': 'Wrong password.'
                }
                return Response(response)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully'
            }
            return Response(response)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FcmTokenUpdate(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.data.get('user_id')
        token = request.data.get('token')
        exist_info = FCM.objects.filter(user_id=user).first()
        if exist_info:
            FCM.objects.filter(user_id=user).update(token=token)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'FCM Update Success'
            }
        else:
            FCM.objects.create(user_id=user, token=token)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'FCM Create Success'
            }

        return Response(response, status=status.HTTP_201_CREATED)

class UserActiveInactive(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.data.get('user_id')
        exist_info = User.objects.filter(id=user).first()
        if exist_info:
            if exist_info.is_active == 1:
                User.objects.filter(id=user).update(is_active=0)
                response = {
                    'success': 'True',
                    'status_code': status.HTTP_200_OK,
                    'message': 'User Inactive Success'
                }
            else:
                User.objects.filter(id=user).update(is_active=1)
                response = {
                    'success': 'True',
                    'status_code': status.HTTP_200_OK,
                    'message': 'User Active Success'
                }
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'User Not Found'
            }

        return Response(response, status=status.HTTP_201_CREATED)


class ForgotPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        random_string = str(random.randint(100000, 999999))
        phn_cell = request.data.get('phone')
        email = request.data.get('email')
        is_phone = Phone.objects.filter(phn_cell=phn_cell).first()
        is_email = User.objects.filter(usr_email=email).first()
        if is_phone:
            if len(is_phone.phn_cell) > 11:
                phone_number = is_phone.phn_cell[-11:]
            else:
                phone_number = is_phone.phn_cell
            # url = "http://dma.com.bd:8888/send/sms"
            # message = {'number': phone_number, 'message': 'Your Reset code is: '+random_string}
            # r = requests.post(url, message)
            message = 'Your Reset code is: ' + random_string
            token = "17751359451705046385d681c28af1f6d6ba4dc9289ca664edf6"
            url = "http://api.greenweb.com.bd/api.php"
            data = {
                'token':token,
                'to':phone_number,
                'message':message
            }
            responses = requests.post(url = url, data = data) 
            if (responses.status_code == 200):
                otp_info = OTP.objects.filter(user_id=is_phone.user_id)
                if otp_info:
                    OTP.objects.filter(user_id=is_phone.user_id).update(otp=random_string)
                else:
                    OTP.objects.create(user_id=is_phone.user_id, otp=random_string)
                print("Successfully sent to user!!")
            

            if is_email:
                user_name = is_email.first_name+' '+is_email.last_name
                subject = 'Fish Farm : Password Reset Code!'
                html_message = render_to_string('mail_template/password_reset.html', {'user_name': user_name, 'code': random_string})
                plain_message = strip_tags(html_message)
                email_from = EMAIL_HOST_USER
                recipient_list = [is_email.usr_email, ]
                try:
                    send_mail(subject, plain_message, email_from, recipient_list, html_message=html_message)
                except Exception as e:
                    error = 'on line {}'.format(sys.exc_info()[-1].tb_lineno), e
                    print(f"Error:{error}")
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'Success'
            }
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'User Phone Not Found'
            }
        return Response(response)

class OtpVerify(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        code = request.data.get('code')
        otp_info = OTP.objects.filter(otp=code).first()
        if otp_info:
            user_info = User.objects.filter(id=otp_info.user_id).first()
            if user_info:
                if user_info.is_verify == 0:
                    User.objects.filter(id=otp_info.user_id).update(is_verify=1)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'user id': otp_info.user_id,
                'message': 'Code is Matched'
            }
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Enter Valid Code'
            }
        return Response(response)

class ExistingUserCheck(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        email = request.data.get('email')
        email_info = User.objects.filter(usr_email=email).first()
        if email_info:
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'Email Already Exist'
            }
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'Not Found'
            }
        return Response(response)

class ResendOtp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        random_string = str(random.randint(100000, 999999))
        user = request.data.get('user_id')
        otp_info = OTP.objects.filter(user_id=user).first()
        if otp_info:
            is_phone = Phone.objects.filter(user_id=user).first()
            if is_phone:
                if len(is_phone.phn_cell) > 11:
                    phone_number = is_phone.phn_cell[-11:]
                else:
                    phone_number = is_phone.phn_cell
                message = 'Your Reset code is: ' + random_string
                token = "17751359451705046385d681c28af1f6d6ba4dc9289ca664edf6"
                url = "http://api.greenweb.com.bd/api.php"
                data = {
                    'token':token,
                    'to':phone_number,
                    'message':message
                }
                responses = requests.post(url = url, data = data) 
                if (responses.status_code == 200):
                    otp_info = OTP.objects.filter(user_id=is_phone.user_id)
                    if otp_info:
                        OTP.objects.filter(user_id=is_phone.user_id).update(otp=random_string)
                    else:
                        OTP.objects.create(user_id=is_phone.user_id, otp=random_string)
                    print("Successfully sent to user!!")
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'user id': otp_info.user_id,
                'message': 'Code is Sent'
            }
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'User Not Found'
            }
        return Response(response)

class DeleteUser(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data.get('user_id')
        User.objects.filter(id=user).delete()
        response = {
            'success': 'True',
            'status_code': status.HTTP_404_NOT_FOUND,
            'message': 'Delete User Success'
        }
        return Response(response)

class OtpSend(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        # OTP send
        phone = request.data['phone_number']
        if len(phone) > 11:
            phone_number = phone[-11:]
        else:
            phone_number = phone
        random_string = str(random.randint(100000, 999999))
        token = "17751359451705046385d681c28af1f6d6ba4dc9289ca664edf6"
        message = 'Your OTP is: ' + random_string
        data = {
            'token':token,
            'to':phone_number,
            'message':message
        }
        url = "http://api.greenweb.com.bd/api.php"
        r = requests.post(url=url,data=data)
        print(r)
        if (r.status_code == 200):
            OTP.objects.create(otp=random_string)
            response = {
                'success': 'True',
                'status_code': status.HTTP_200_OK,
                'message': 'OTP has been sent.'
            }
            return Response(response)
        else:
            response = {
                'success': 'True',
                'status_code': status.HTTP_404_NOT_FOUND,
                'message': 'OTP sent has been failed.'
            }
            return Response(response)

class ResetPassword(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        password = request.data.get('password')
        user_id = request.data.get('user_id')
        hashed_password =  make_password(password)
        User.objects.filter(id=user_id).update(password=hashed_password)
        response = {
            'success': 'True',
            'status_code': status.HTTP_200_OK,
            'message': 'Success'
        }
        return Response(response)

class CompanySelector(APIView):
    permission_classes=(IsAuthenticated,)

    def post(self,request:HttpRequest):
        company_id = request.data.get("company_id")
        try:
            user = User.objects.get(id=request.user.id)
            user.company_id = company_id
            user.save()
            return Response({
                "success":"True",
                "status_code":status.HTTP_202_ACCEPTED,
                "message":"company set successfully"
            })
        except:
            traceback.print_exc()
            return Response({
                "success":"False",
                'status_code':status.HTTP_400_BAD_REQUEST,
                'message':'Success'
                })