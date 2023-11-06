from rest_framework import serializers

class SearchSerializer(serializers.Serializer):
    search_query = serializers.CharField()
    