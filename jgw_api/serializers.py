from rest_framework import serializers

from .models import Category

class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_name',)