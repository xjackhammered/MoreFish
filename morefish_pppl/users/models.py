from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
# Create your models here.
from users.managers import UserManager

# from application.models import Application

is_gender = (
    ('M', 'Male'),
    ('F', 'Female'),
)


class Company(models.Model):
    name = models.CharField(max_length=150, null=True, blank=True)
    icon = models.ImageField(upload_to="uploads/company/images/", null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class CompanyInformation(models.Model):
    company_contact_person = models.CharField(max_length=150, blank=True, null=True)
    company_contact_number = models.CharField(max_length=150, null=True, blank=True)
    company_address = models.TextField(null=True, blank=True)
    company = models.ForeignKey("users.Company", null=True, blank=True, on_delete=models.CASCADE)


class User(AbstractBaseUser, PermissionsMixin):
    class UserType(models.IntegerChoices):
        SUPER_USER = '0', _('SUPER_USER')
        ORGANIZATION_USER = '1', _('ORGANIZATION_USER')
        ZONAL_ADMIN = '2', _('ZONAL_ADMIN')
        CONSUMER = '3', _('CONSUMER')
        OPERATOR = '4', _('OPERATOR')
        SELLER = '5', _('SELLER')

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        error_messages={
            'unique': _("A user with that username already exists."),
        }, blank=True, null=True
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    gender = models.CharField(max_length=1, choices=is_gender, null=True, blank=True)
    usr_email = models.EmailField(_('email address'), null=True, blank=True, unique=True)
    usr_profile_pic = models.ImageField(upload_to='uploads/users/images/', blank=True, null=True)
    user_type = models.IntegerField(_('user type'), choices=UserType.choices, default=UserType.CONSUMER)
    # for seller
    user_details = models.TextField(max_length=255, null=True, blank=True)
    usr_address = models.TextField(max_length=255, null=True, blank=True)
    interested_product_details = models.TextField(max_length=255, null=True, blank=True)

    # application = models.ManyToManyField(Application, blank=True, null=True)
    is_deleted = models.BooleanField(_('deleted'), default=False,
                                     help_text=_('Designates whether this user is deleted'))
    is_verify = models.BooleanField(_('verify'), default=True, help_text=_('Designates whether this user is verified'))
    is_notification = models.BooleanField(_('notification'), default=False,
                                          help_text=_('User get Notification using Apps'))
    is_message = models.BooleanField(_('message'), default=False, help_text=_('User get mobile SMS'))
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now=True)
    company = models.ForeignKey("users.Company", null=True, blank=True, on_delete=models.CASCADE)
    # company = models.ForeignKey(null=True,blank=True,on_delete=models.CASCADE, default=None)
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class Address(models.Model):
    user = models.OneToOneField('users.User', related_name='user_address', on_delete=models.CASCADE, primary_key=True)
    add_village = models.CharField(max_length=200, blank=True, null=True)
    add_police_station = models.CharField(max_length=200, blank=True, null=True)
    add_zip = models.CharField(max_length=20, blank=True, null=True)
    add_road = models.CharField(max_length=20, blank=True, null=True)
    add_house = models.CharField(max_length=100, blank=True, null=True)
    add_union = models.CharField(max_length=100, blank=True, null=True)
    add_city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return "%s" % self.add_city


class Phone(models.Model):
    user = models.OneToOneField('users.User', related_name='user_phone', on_delete=models.CASCADE, primary_key=True)
    phn_business = models.CharField(max_length=50, blank=True, null=True)
    phn_cell = models.CharField(max_length=50, blank=True, null=True)
    phn_home = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "%s" % self.phn_cell


class Citizenship(models.Model):
    user = models.OneToOneField('users.User', related_name='user_citizenship', on_delete=models.CASCADE,
                                primary_key=True)
    cit_dob = models.CharField(max_length=200, blank=True, null=True)
    cit_nid = models.CharField(max_length=200, blank=True, null=True)
    cit_passport = models.CharField(max_length=200, blank=True, null=True)
    cit_citizenship = models.CharField(max_length=200, blank=True, null=True)


class Education(models.Model):
    user = models.ForeignKey('users.User', related_name='user_education', on_delete=models.CASCADE, null=True,
                             blank=True)
    edu_degree = models.CharField(max_length=200, blank=True, null=True)
    edu_organization = models.CharField(max_length=300, blank=True, null=True)
    edu_board = models.CharField(max_length=300, blank=True, null=True)
    edu_admission_date = models.DateField(blank=True, null=True)
    edu_passing_year = models.DateField(max_length=200, blank=True, null=True)
    edu_result = models.CharField(max_length=200, blank=True, null=True)
    edu_out_of = models.CharField(max_length=200, blank=True, null=True)
    edu_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.edu_degree


class Occupation(models.Model):
    user = models.OneToOneField('users.User', related_name='user_occupation', on_delete=models.CASCADE,
                                primary_key=True)
    occ_title = models.CharField(max_length=200, blank=True, null=True)
    occ_organization = models.CharField(max_length=255, blank=True, null=True)
    occ_organization_address = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.occ_title


class Location(models.Model):
    user = models.ForeignKey('users.User', related_name='user_location', on_delete=models.CASCADE, blank=True,
                             null=True)
    loc_lat = models.CharField(max_length=200, blank=True, null=True)
    loc_long = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return "%s" % self.loc_lat + "%s" % self.loc_long


class FCM(models.Model):
    user = models.OneToOneField('users.User', related_name='user_fcm', on_delete=models.CASCADE, primary_key=True)
    token = models.TextField(blank=True, null=True)

    def __str__(self):
        return "%s" % self.token


class OTP(models.Model):
    user = models.ForeignKey('users.User', related_name='user_otp', on_delete=models.CASCADE, blank=True, null=True)
    otp = models.CharField(max_length=50, blank=True, null=True)


class MqttTopci(models.Model):
    class TopicType(models.IntegerChoices):
        RAW_DATA = 1, "raw_data_toipic"
        MQTT_DATA = 2, "mqtt_device_data"
        FILE_WRITING = 3, "file_writing_topic"
        HATCHERY = 4, "hatchery_topic"

    topic_name = models.CharField(null=True, blank=True, max_length=50)
    topic = models.CharField(null=True, blank=True, max_length=100)
    topic_type = models.IntegerField(choices=TopicType.choices, null=True, blank=True)


class APIKey(models.Model):
    class KeyType(models.IntegerChoices):
        OPEN_WEATHER_API = 1, "Open weather Api key"
        GOOGLE_GEOCODE_API = 2, "Google Geocode Api key"
        FCM_API_KEY = 3, "FCM API KEY"

    key_value = models.TextField(null=True, blank=True)
    key_type = models.IntegerField(choices=KeyType.choices)
