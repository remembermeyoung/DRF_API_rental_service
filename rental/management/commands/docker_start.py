from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from rental.models import Bicycle


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = ['Аист', 'Десна', 'BMX', 'Forward', 'GT']
        prices = [100, 200, 50, 75, 80]

        try:
            Bicycle.objects.get(id=1)
        except Bicycle.DoesNotExist:
            bicycles = [Bicycle(model=models[i], price=prices[i]) for i in range(0,5)]
            Bicycle.objects.bulk_create(bicycles)

            get_user_model().objects.create_user(username='test_user', password='test_password', email='test@test.com')
            get_user_model().objects.create_user(username='test_user2', password='test_password2', email='test2@test.com')
            print('Стартовый скрипт запущен\n'
                  'Создано 5 моделей велосипедов и 2 тестовых пользователя:\n'
                  '1. username=test_user, password=test_password, email=test@test.com\n'
                  '2. username=test_user2, password=test_password2, email=test2@test.com\n')
        else:
            print('Стартовый скрипт запущен\n'
                  'Тестовые данные уже в БД')
