# Generated by Django 5.0.6 on 2024-07-04 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rental', '0002_alter_bicycle_options_alter_orders_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='rent_finish',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Конец аренды'),
        ),
    ]