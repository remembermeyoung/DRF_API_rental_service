from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser import serializers as dj_ser
from django.conf import settings
from rest_framework import serializers
from rental.models import Bicycle, Orders
from django.core import exceptions as django_exceptions
from rest_framework.settings import api_settings

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'id')
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'required': True}}


    def validate(self, attrs):
        password = attrs.get('password')
        email = attrs.get('email')

        if email in User.objects.all().values_list('email', flat=True):
            raise serializers.ValidationError(detail='Пользователь с таким email уже существует')

        try:
            validate_password(password)
        except django_exceptions.ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error[api_settings.NON_FIELD_ERRORS_KEY]}
            )

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class BicycleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bicycle
        fields = '__all__'
        extra_kwargs = {'status': {'read_only': True}}


class OrdersSerializer(serializers.ModelSerializer):

    bicycle_model = serializers.CharField(source='bicycle.model', read_only=True)

    class Meta:
        model = Orders
        fields = ['rent_start', 'rent_finish', 'total_price', 'user', 'bicycle', 'bicycle_model']
        extra_kwargs = {'user': {'write_only': True},
                        'bicycle': {'write_only': True}}
