from rest_framework import serializers

class CorePaginationSerializer(serializers.Serializer):
    page_number = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    total_items = serializers.IntegerField()
    has_next = serializers.BooleanField()
    has_prev = serializers.BooleanField()
    page_size = serializers.IntegerField()
    
class CoreSerializer(serializers.Serializer):
    guid = serializers.CharField()