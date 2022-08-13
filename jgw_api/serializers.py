from rest_framework import serializers

from .models import Category

class CategoryGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryEditSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(CategoryEditSerializer, self).__init__(many=many, *args, **kwargs)

    class Meta:
        model = Category
        fields = ('category_name',)