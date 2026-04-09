from rest_framework_jwt.settings import api_settings

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER
import json
from .models import Company, User, Phone, Education, Address, Occupation, Location, Citizenship, FCM, OTP
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, update_last_login
from rest_framework import serializers





class UserPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['phn_business', 'phn_cell', 'phn_home']


class UserAddressSerializer(serializers.ModelSerializer):
    # add_city = CitySerializer()

    class Meta:
        model = Address
        fields = ['add_village', 'add_police_station', 'add_zip', 'add_road', 'add_house', 'add_union', 'add_city']


class CreateUserAddressSerializer(serializers.ModelSerializer):
    # add_city = CitySerializer()
    add_village = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    add_police_station = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    add_zip = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    add_road = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    add_house = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    add_union = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    class Meta:
        model = Address
        fields = ['user', 'add_village', 'add_police_station', 'add_zip', 'add_road', 'add_house', 'add_union',
                  'add_city']


class CitizenshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizenship
        fields = ['cit_dob', 'cit_nid', 'cit_passport', 'cit_citizenship', ]


class CreateCitizenshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizenship
        fields = ['user', 'cit_dob', 'cit_nid', 'cit_passport', 'cit_citizenship', ]


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'edu_degree', 'edu_organization', 'edu_board', 'edu_admission_date', 'edu_passing_year',
                  'edu_result',
                  'edu_out_of', 'edu_description']


class CreateEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['user', 'edu_degree', 'edu_organization', 'edu_board', 'edu_admission_date', 'edu_passing_year',
                  'edu_result', 'edu_out_of', 'edu_description']


class OccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ['occ_title', 'occ_organization', 'occ_organization_address', ]


class CreateOccupationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occupation
        fields = ['user', 'occ_title', 'occ_organization', 'occ_organization_address', ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['loc_lat', 'loc_long', ]


class CreateLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['user', 'loc_lat', 'loc_long', ]


class FCMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCM
        fields = ['token', ]


class CreateFCMSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCM
        fields = ['user', 'token', ]


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['otp', ]


class CreateOTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ['user', 'otp', ]


class UpdateUserDetailSerializer(serializers.ModelSerializer):
    user_address = UserAddressSerializer(required=False, allow_null=True)
    user_citizenship = CitizenshipSerializer(required=False, allow_null=True)
    user_education = EducationSerializer(required=False, allow_null=True, many=True, )
    user_occupation = OccupationSerializer(required=False, allow_null=True)

    # user_location = LocationSerializer(many=True,required=False,allow_null=True)
    # user_fcm = FCMSerializer(read_only=True)
    # user_otp = OTPSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'user_type','user_address',
                  'user_citizenship', 'user_education', 'user_occupation']

    def update(self, instance, validated_data):

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        # instance.usr_email = validated_data.get('usr_email', instance.usr_email)

        # updating address
        if validated_data.get('user_address') is not None:
            if Address.objects.filter(user=instance.id).exists():
                res_address_obj = validated_data.pop('user_address')
                Address.objects.filter(user=instance.id).update(add_village=res_address_obj.get('add_village'),
                                                                add_police_station=res_address_obj.get(
                                                                    'add_police_station'),
                                                                add_zip=res_address_obj.get('add_zip'),
                                                                add_road=res_address_obj.get('add_road'),
                                                                add_house=res_address_obj.get('add_house'),
                                                                add_union=res_address_obj.get('add_union'),
                                                                add_city_id=res_address_obj.get('add_city_id'))
            else:
                res_address_obj = validated_data.get('user_address')
                res_address_obj['user'] = instance.id
                print(res_address_obj)
                new_address = CreateUserAddressSerializer(data=res_address_obj)
                new_address.is_valid()
                new_address.save()

        if validated_data.get('user_citizenship') is not None:
            if Citizenship.objects.filter(user=instance.id).exists():
                res_citizenship_obj = validated_data.get('user_citizenship')
                Citizenship.objects.filter(user=instance.id).update(cit_dob=res_citizenship_obj.get('cit_dob'),
                                                                    cit_nid=res_citizenship_obj.get(
                                                                        'cit_nid'),
                                                                    cit_passport=res_citizenship_obj.get(
                                                                        'cit_passport'),
                                                                    cit_citizenship=res_citizenship_obj.get(
                                                                        'cit_citizenship'))

            else:
                res_citizenship_obj = validated_data.get('user_citizenship')
                res_citizenship_obj['user'] = instance.id
                new_citizenship = CreateCitizenshipSerializer(data=res_citizenship_obj)
                new_citizenship.is_valid()
                new_citizenship.save()
        # occupation
        if validated_data.get('user_occupation') is not None:
            if Occupation.objects.filter(user=instance.id).exists():
                res_occupation_obj = validated_data.get('user_occupation')
                Occupation.objects.filter(user=instance.id).update(occ_title=res_occupation_obj.get('occ_title'),
                                                                   occ_organization=res_occupation_obj.get(
                                                                       'occ_organization'),
                                                                   occ_organization_address=res_occupation_obj.get(
                                                                       'occ_organization_address'),
                                                                   )

            else:
                res_occupation_obj = validated_data.get('user_occupation')
                res_occupation_obj['user'] = instance.id
                new_occupation = CreateOccupationSerializer(data=res_occupation_obj)
                new_occupation.is_valid()
                new_occupation.save()

        # education
        if validated_data.get('user_education') is not None:
            Education.objects.filter(user=instance.id).delete()
            education_list = list(validated_data.pop('user_education'))
            for education in education_list:
                education['user'] = instance.id
                new_education = CreateEducationSerializer(data=education)
                new_education.is_valid()
                new_education.save()

        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    user_phone = UserPhoneSerializer(allow_null=True)
    user_address = UserAddressSerializer(allow_null=True)
    user_citizenship = CitizenshipSerializer(allow_null=True)
    user_education = EducationSerializer(many=True,allow_null=True)
    user_occupation = OccupationSerializer(allow_null=True)
    user_location = LocationSerializer(many=True,allow_null=True)
    user_fcm = FCMSerializer(read_only=True,allow_null=True)
    user_otp = OTPSerializer(read_only=True,allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'usr_email', 'first_name', 'last_name', 'is_active', 'user_type', 'user_phone', 'user_address',
                  'user_citizenship', 'user_education', 'user_occupation', 'user_location', 'user_fcm', 'user_otp','company_id']


class PhoneCreateSerializer(serializers.ModelSerializer):
    phn_cell = serializers.CharField(required=False,allow_blank=True)
    phn_home = serializers.CharField(required=False,allow_blank=True)
    phn_buisness = serializers.CharField(required=False,allow_blank=True)

    class Meta:
        model = Phone
        fields = ('user', 'phn_cell', 'phn_home', 'phn_buisness')

class RegistrationSerializer(serializers.Serializer):
    usr_email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    user_type = serializers.IntegerField(required=True)
    company = serializers.IntegerField(required=True,allow_null=True)
    # seller-specific fields
    user_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    usr_address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    interested_product_details = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def validate(self, data):
        user_type = data.get('user_type')
        company = data.get('company')

        # Check if user_type is 3 and company is null
        if user_type == 3 and company is not None:
            raise serializers.ValidationError("Company must be null for user_type 3.")

        # Check if user_type is 1 and company exists
        if user_type == 1 and company is None:
            raise serializers.ValidationError("Company is required for user_type 1.")

        return data
    
class RegisterSerializer(serializers.ModelSerializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(),required=False,allow_null=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'password', 'usr_email', 'company','user_type', 'user_details', 'usr_address', 'interested_product_details')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # print('reg serializer',validated_data)
        user = User.objects.create_user(**validated_data)
        print(validated_data)
        user.username = validated_data['usr_email']
        if user.company_id:
            user.company_id = validated_data['company']
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    usr_email = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(max_length=128, write_only=True)

        

class LoginResponseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=True)
    token = serializers.CharField(required=True)
    user_data = serializers.DictField()
    
    
    
class ChangePasswordSerializer(serializers.Serializer):
    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class CompanyListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=True,allow_blank=True)
    
    class Meta:
        model=Company
        fields = ("id","name")