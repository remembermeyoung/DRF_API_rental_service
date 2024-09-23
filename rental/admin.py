from django.contrib import admin
from .models import Bicycle, Orders


@admin.register(Bicycle)
class BicycleAdmin(admin.ModelAdmin):
    list_display = ['model', 'price', 'status']
    list_filter = ['model', 'price', 'status']
    ordering = ['status', '-price']


admin.site.register(Orders)
