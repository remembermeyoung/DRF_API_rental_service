from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .tasks import set_total_price

from rental.models import Bicycle, Orders
from django.utils import timezone
from rental.permissions import BicycleDetailPermission, NotAuthorisedPermission
from .serializers import BicycleSerializer, CreateUserSerializer, OrdersSerializer


class RegistrationAPIView(APIView):
    permission_classes = (NotAuthorisedPermission, )

    def post(self, request):

        serializer = CreateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        token = RefreshToken.for_user(user)
        token.payload.update({'user_id': user.id, 'username': user.username})

        return Response({'access': str(token.access_token),
                         'refresh': str(token)},
                        status=status.HTTP_201_CREATED)


class LogInAPIView(APIView):
    permission_classes = (NotAuthorisedPermission, )

    def post(self, request):

        data = request.data

        username = data.get('username', None)
        password = data.get('password', None)

        if username is None or password is None:
            return Response({'error': 'Для авторизации необходимо ввести логин и пароль'},
                            status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Неверные данные'}, status=status.HTTP_401_UNAUTHORIZED)

        token = RefreshToken.for_user(user)
        token.payload.update({'user_id': user.id, 'username': user.username})

        return Response({'access': str(token.access_token), 'refresh': str(token)},
                        status=status.HTTP_200_OK)


class LogOutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({'error': 'Необходим refresh_token'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({'error': 'ОШИБКА'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': 'Выход'}, status=status.HTTP_200_OK)


class BicycleStatusListAPIView(ListAPIView):
    def get(self, request, *args, **kwargs):
        queryset = Bicycle.objects.all() if kwargs['status'] == 'all' else Bicycle.objects.filter(status=kwargs['status'])
        serializer = BicycleSerializer

        if not queryset:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({f'{kwargs['status']}': serializer(queryset, many=True).data})


class BicycleDetailAPIView(RetrieveUpdateAPIView):
    queryset = Bicycle.objects.all()
    serializer_class = BicycleSerializer
    permission_classes = (BicycleDetailPermission, )

    def patch(self, request, **kwargs):

        bicycle = Bicycle.objects.get(id=kwargs['pk'])
        user = User.objects.get(username=str(request.user))

        if bicycle.status == 'free':
            if Orders.objects.filter(rent_finish=None, user=user):
                return Response({'Ошибка': 'Нельзя арендовать больше одного велосипеда'},
                                status=status.HTTP_403_FORBIDDEN)
            else:
                bicycle_ser = BicycleSerializer(instance=bicycle, data={'status': 'rented'}, partial=True)
                bicycle_ser.is_valid(raise_exception=True)
                bicycle_ser.save()

                order_ser = OrdersSerializer(data={'user': user.id, 'bicycle': bicycle.id})
                order_ser.is_valid(raise_exception=True)
                order_ser.save()
                return Response({'Велосипед арендован': BicycleSerializer(bicycle).data,
                                 'Время начала аренды': OrdersSerializer(Orders.objects.latest('id')).data['rent_start']})

        if bicycle.status == 'rented':

            orders = Orders.objects.filter(bicycle_id=kwargs['pk'])
            if User.objects.get(id=orders.latest('id').user_id).username == str(request.user):

                bicycle_ser = BicycleSerializer(instance=bicycle, data={'status': 'free'}, partial=True)
                bicycle_ser.is_valid(raise_exception=True)
                bicycle_ser.save()

                current_order = orders.latest('id')
                order_ser = OrdersSerializer(instance=current_order, data={'rent_finish': timezone.now()}, partial=True)
                order_ser.is_valid(raise_exception=True)
                order_ser.save()

                set_total_price.delay(current_order)

                return Response({'Велосипед возвращен': BicycleSerializer(bicycle).data,
                                'Время окончания аренды': OrdersSerializer(current_order).data['rent_finish']})

            else:
                return Response({'Ошибка': 'Этот велосипед арендован другим пользователем'},
                                status=status.HTTP_403_FORBIDDEN)

    def put(self, request, **kwargs):
        return Response({'Ошибка': 'метод /PUT/ недоступен'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrdersHistoryAPIView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = User.objects.get(username=str(request.user))
        queryset = Orders.objects.filter(user=user)
        if queryset:
            return Response({'История аренды': OrdersSerializer(queryset, many=True).data})
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
