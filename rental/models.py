from django.contrib.auth.models import User
from django.db import models


class Bicycle(models.Model):

    STATUS_OPTION = (('rented', 'Арендован'), ('free', 'Свободен'))

    model = models.CharField(max_length=25, verbose_name='Модель велосипеда')
    price = models.PositiveSmallIntegerField(verbose_name='Цена за час')
    status = models.CharField(max_length=9, choices=STATUS_OPTION, default='free', verbose_name='Статус')

    objects = models.Manager()

    class Meta:
        ordering = ['status', '-price']
        indexes = [models.Index(fields=['-model'])]
        verbose_name = 'Велосипед'
        verbose_name_plural = 'Велосипеды'

    def __str__(self):
        return self.model


class Orders(models.Model):

    rent_start = models.DateTimeField(auto_now_add=True, verbose_name='Начало аренды')
    rent_finish = models.DateTimeField(blank=True, null=True, verbose_name='Конец аренды')
    total_price = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Сумма аренды')

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='user', verbose_name='Арендатор')
    bicycle = models.ForeignKey(Bicycle, on_delete=models.DO_NOTHING, related_name='bicycle', verbose_name='Велосипед')

    objects = models.Manager()

    class Meta:
        ordering = ['rent_start']
        indexes = [models.Index(fields=['-user'])]
        verbose_name = 'История заказов'
        verbose_name_plural = 'История заказов'

    def __str__(self):
        return f'{self.user.username}, {self.bicycle.model}'
