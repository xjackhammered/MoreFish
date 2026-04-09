from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from django.contrib import admin

# Register your models here.
# from import_export.admin import ImportExportModelAdmin

from users.forms import UserChangeForm, UserCreationForm
from users.models import *


class AddressAdmin(admin.StackedInline):
    model = Address


class CitizenshipAdmin(admin.StackedInline):
    model = Citizenship


class OccupationAdmin(admin.StackedInline):
    model = Occupation


class PhoneAdmin(admin.StackedInline):
    model = Phone


class LocationAdmin(admin.StackedInline):
    model = Location


class FCMAdmin(admin.StackedInline):
    model = FCM


class EducationAdmin(admin.StackedInline):
    model = Education


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_deleted")


@admin.register(CompanyInformation)
class CompanyInformationAdmin(admin.ModelAdmin):
    list_display = (
        "company_contact_person",
        "company_contact_number",
        "company_address",
        "company",
    )

#
# class UsersAdmin(UserAdmin):
#     form = UserChangeForm
#     add_form = UserCreationForm
#     fieldsets = (
#         (None, {"fields": ("username", "password", "usr_email", "company")}),
#         (
#             _("Profile info"),
#             {
#                 "fields": (
#                     "first_name",
#                     "last_name",
#                     "gender",
#                     "usr_profile_pic",
#                     "user_type",
#                 )
#             },
#         ),
#         (
#             _("Permissions"),
#             {
#                 "fields": (
#                     "groups",
#                     "is_verify",
#                     "is_notification",
#                     "is_message",
#                     "is_active",
#                     "is_staff",
#                     "is_superuser",
#                 )
#             },
#         ),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {"classes": ("wide",), "fields": ("username", "password1", "password2")},
#         ),
#     )
#
#     inlines = [
#         AddressAdmin,
#         PhoneAdmin,
#         OccupationAdmin,
#         EducationAdmin,
#         CitizenshipAdmin,
#         LocationAdmin,
#         FCMAdmin,
#     ]
#
#     def user_type(self, obj):
#         """
#         get group, separate by comma, and display empty string if user has no group
#         """
#         return (
#             ",".join([g.name for g in obj.groups.all()]) if obj.groups.count() else ""
#         )
#
#     list_display = ("username", "usr_email", "first_name", "is_staff")
#     list_display_links = ("username",)
#     list_filter = [
#         "groups",
#     ]
#     search_fields = ("usr_email", "first_name", "last_name", "username")
#     ordering = ("usr_email",)
#     readonly_fields = ("date_joined", "last_login")

class UsersAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {"fields": ("username", "password", "usr_email", "company")}),
        (
            _("Profile info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "gender",
                    "usr_profile_pic",
                    "user_type",
                    # seller-specific fields
                    "user_details",
                    "usr_address",
                    "interested_product_details",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "groups",
                    "is_verify",
                    "is_notification",
                    "is_message",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "usr_email",
                    "password1",
                    "password2",
                    "user_type",
                    "company",
                ),
            },
        ),
    )

    inlines = [
        AddressAdmin,
        PhoneAdmin,
        OccupationAdmin,
        EducationAdmin,
        CitizenshipAdmin,
        LocationAdmin,
        FCMAdmin,
    ]

    def user_type(self, obj):
        """
        get group, separate by comma, and display empty string if user has no group
        """
        return (
            ",".join([g.name for g in obj.groups.all()]) if obj.groups.count() else ""
        )

    list_display = (
        "username",
        "usr_email",
        "first_name",
        "user_type",
        "company",
        "is_staff",
    )
    list_display_links = ("username",)
    list_filter = [
        "groups",
        "user_type",
        "company",
    ]
    search_fields = ("usr_email", "first_name", "last_name", "username")
    ordering = ("usr_email",)
    readonly_fields = ("date_joined", "last_login")


class MqttTopicAdmin(admin.ModelAdmin):
    list_display = ("topic_name", "topic")


class APIkeyAdmin(admin.ModelAdmin):
    list_display = ("key_value", "key_type")


admin.site.register(User, UsersAdmin)
admin.site.register(MqttTopci, MqttTopicAdmin)
admin.site.register(APIKey, APIkeyAdmin)
