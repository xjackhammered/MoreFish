from django.contrib import admin
from assets.models import AssetsType, AssetsProperties, AssetsFiles, District
# from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter
# Register your models here.


class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ('ast_title', 'ast_created_at',)

    search_fields = ('ast_title', )
admin.site.register(AssetsType, AssetTypeAdmin)

class AssetsFilesAdmin(admin.StackedInline):
    model = AssetsFiles

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['district']

class AssetsPropertiesAdmin(admin.ModelAdmin):
    exclude = ['ast_created_by', 'ast_updated_by']
    inlines = [AssetsFilesAdmin]
    list_display = ('ast_name', 'ast_type', 'users','company','district')

    search_fields = ('ast_title', )

    def users(self, obj):
        return ", ".join([p.first_name +' '+p.last_name for p in obj.ast_user.all()])

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.ast_created_by = request.user
            obj.ast_updated_by = request.user
        if change and obj.id:
            obj.ast_updated_by = request.user
        obj.save()
admin.site.register(AssetsProperties, AssetsPropertiesAdmin)
