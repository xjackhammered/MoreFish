from django.contrib import admin
from notification.models import NotificationThreshold, Notifications, Configuration


# from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
# Register your models here.

class NotificationsAdmin(admin.ModelAdmin):
    list_display = (
        'not_user',
        'not_time',
        'not_date',
        'not_urgency',
        'not_pond',
        'not_message_body',
        'not_warning_msg',
        'not_warning',
        'not_value',
        'not_final',
        'not_color',
        'dev',
        'conf'
    )

    search_fields = ('not_user',)

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.not_updated_by = request.user
        if change and obj.id:
            obj.not_updated_by = request.user
        obj.save()


admin.site.register(Notifications, NotificationsAdmin)


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = (
        'con_code',
        'con_urgency',
        'con_message_body',
        'con_todo',
        'con_warning_msg',
        'con_warning',
        'con_created_at',
    )

    search_fields = ('con_code',)


class NotificationThresholdadmin(admin.ModelAdmin):
    list_display = ('thresh_device',)
    fieldsets = (
        ('Device', {
            'fields': ('thresh_device',),
        }),
        ('pH', {
            'fields': ('max_ph_threshold', 'min_ph_threshold', 'max_good_ph_threshold', 'good_ph_threshold',
                       'min_good_ph_threshold'),
        }),

        ('TDS', {
            'fields': ('max_tds_threshold', 'min_tds_threshold', 'max_good_tds_threshold', 'good_tds_threshold',
                       'min_good_tds_threshold'),
        }),
        ('Temperature', {
            'fields': ('max_temperature_threshold', 'min_temperature_threshold', 'max_good_temperature_threshold',
                       'good_temperature_threshold', 'min_good_temperature_threshold'),
        }),
        ('Ammonia', {
            'fields': ('max_ammonia_threshold', 'min_ammonia_threshold', 'max_good_ammonia_threshold',
                       'good_ammonia_threshold', 'min_good_ammonia_threshold'),
        }),
        ('DO', {
            'fields': ('max_do_threshold', 'min_do_threshold', 'max_good_do_threshold', 'good_do_threshold',
                       'min_good_do_threshold'),
        }),
        ('Alkinity', {
            'fields': ('max_alkinity_threshold', 'min_alkinity_threshold', 'max_good_alkinity_threshold',
                       'good_alkinity_threshold', 'min_good_alkinity_threshold'),
        }),
        ('Hardness', {
            'fields': ('max_hardness_threshold', 'min_hardness_threshold', 'max_good_hardness_threshold',
                       'good_hardness_threshold', 'min_good_hardness_threshold'),
        }),
    )


admin.site.register(Configuration, ConfigurationAdmin)
admin.site.register(NotificationThreshold, NotificationThresholdadmin)
