from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from rental.models import Bicycle


class Command(BaseCommand):
    def handle(self, *args, **options):
        models = ['Аист', 'Десна', 'BMX', 'Forward', 'GT']
        prices = [100, 200, 50, 75, 80]

        try:
            Bicycle.objects.get(id=1)
        except Exception:
            for i in range(len(models)):
                Bicycle.objects.create(model=models[i], price=prices[i])

            get_user_model().objects.create_user(username='test_user', password='test_password', email='test@test.com')
            get_user_model().objects.create_user(username='test_user2', password='test_password2', email='test2@test.com')
            print('Скрипт был запущен')
