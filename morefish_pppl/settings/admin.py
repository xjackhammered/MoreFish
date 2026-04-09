# Register your models here.
from django.contrib import admin
from .models import AppVersion


@admin.register(AppVersion)
class AppVersionAdmin(admin.ModelAdmin):
    list_display = ('version_number', 'release_date')
    search_fields = ('version_number',)
    ordering = ('-release_date',)

    def has_add_permission(self, request):
        return True
