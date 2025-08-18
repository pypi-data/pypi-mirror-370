from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from django_jqgrid.models import GridFilter

User = get_user_model()


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class GridFilterSerializer(serializers.ModelSerializer):
    """
    Serializer for GridFilter model - includes nested serializers 
    for associated content type and user
    """
    table_details = ContentTypeSerializer(source='table', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)

    class Meta:
        model = GridFilter
        fields = [
            'id', 'name', 'key', 'value', 'table', 'table_details',
            'created_by', 'created_by_details', 'is_global',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        request = self.context.get('request', None)
        if request and not validated_data.get('created_by'):
            validated_data['created_by'] = request.user
        return super().create(validated_data)
