from django.contrib.auth.models import User
from rest_framework import serializers
from rental.models import Bicycle, Orders


class CreateUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate(self, data):
        if data['username'] in User.objects.all().values_list('username', flat=True):
            raise serializers.ValidationError('Такое имя пользователя уже занято')
        elif data['email'] in User.objects.all().values_list('email', flat=True):
            raise serializers.ValidationError('На этот e-mail уже зарегистрирован аккаунт')
        return data


class BicycleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bicycle
        exclude = ('id',)
        read_only_fields = ['model']


class OrdersSerializer(serializers.ModelSerializer):

    bicycle_model = serializers.CharField(source='bicycle.model', read_only=True)

    class Meta:
        model = Orders
        fields = ['rent_start', 'rent_finish', 'total_price', 'user', 'bicycle', 'bicycle_model']
        extra_kwargs = {'user': {'write_only': True},
                        'bicycle': {'write_only': True}}
