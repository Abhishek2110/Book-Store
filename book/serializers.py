from rest_framework import serializers
from .models import Books
from rest_framework.exceptions import PermissionDenied

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'title', 'author', 'price', 'quantity', 'user')
        
    def validate(self, attrs):
        if not attrs.get('user').is_superuser:
            raise PermissionDenied("Access denied")
        return super().validate(attrs)