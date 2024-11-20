from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import BicycleSerializer, OrdersSerializer
from rental.models import Bicycle, Orders
from django.utils import timezone

User = get_user_model()

class BicycleViewSet(viewsets.ModelViewSet):
    serializer_class = BicycleSerializer

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'update', 'partial_update'):
            permission_classes = (IsAdminUser,)
        elif self.action in ('list', 'rented_bicycles', 'free_bicycles', 'retrieve'):
            permission_classes = (AllowAny,)
        else:
            permission_classes = (IsAuthenticated,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'free_bicycles':
            return Bicycle.objects.filter(status='free')
        elif self.action == 'rented_bicycles':
            return Bicycle.objects.filter(status='rented')
        else:
            return Bicycle.objects.all()

    @action(methods=['get'], detail=False)
    def free(self, request):
        queryset = self.get_queryset()
        return Response({'free_bicycles': self.get_serializer(queryset, many=True).data}) if queryset \
            else Response({'empty': 'Нет свободных велосипедов'})

    @action(methods=['get'], detail=False)
    def rented(self, request):
        queryset = self.get_queryset()
        return Response({'free_bicycles': self.get_serializer(queryset, many=True).data}) if queryset \
            else Response({'empty': 'Нет арендованных велосипедов'})

    @action(methods=['patch'], detail=True)
    def start_rent(self, request, pk=None):
        try:
            bicycle = self.get_queryset().get(pk=pk)
        except Bicycle.DoesNotExist:
            return Response({'error': 'Такого велосипеда нет'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if bicycle.status == 'rented':
                return Response({'error': 'Этот велосипед арендован'},
                                status=status.HTTP_400_BAD_REQUEST)
            elif Orders.objects.filter(rent_finish=None, user=request.user):
                return Response({'error': 'Нельзя арендовать больше одного велосипеда'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                bicycle.status = 'rented'
                bicycle.save()
                Orders.objects.create(user=request.user, bicycle=bicycle)
                return Response({'Велосипед арендован': self.get_serializer(bicycle).data})

    @action(methods=['patch'], detail=True)
    def finish_rent(self, request, pk=None):
        try:
            bicycle = self.get_queryset().get(pk=pk)
        except Bicycle.DoesNotExist:
            return Response({'error': 'Такого велосипеда нет'}, status=status.HTTP_404_NOT_FOUND)
        else:
            orders = Orders.objects.filter(bicycle_id=pk)
            if bicycle.status == 'free':
                return Response({'error': 'Этот велосипед свободен'},
                                status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.get(id=orders.latest('id').user_id).username == str(request.user):
                bicycle.status = 'free'
                bicycle.save()
                current_order = orders.latest('id')
                current_order.rent_finish = timezone.now()
                current_order.save()
                return Response({'Велосипед возвращён': self.get_serializer(bicycle).data})
            else:
                return Response({'error': 'Велосипед арендован другим пользователем'}, status=status.HTTP_400_BAD_REQUEST)


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Orders.objects.all()
    serializer_class = OrdersSerializer

    def get_permissions(self):
        if self.action == 'history':
            permission_classes = (IsAuthenticated,)
        else:
            permission_classes = (IsAdminUser,)
        return [permission() for permission in permission_classes]

    @action(methods=['get'], detail=False)
    def history(self, request):
        queryset = self.get_queryset().filter(user=request.user).exclude(rent_finish=None)
        return Response({'История аренды': self.get_serializer(queryset, many=True).data}) if queryset \
            else Response({'empty': 'История аренды пуста'})

