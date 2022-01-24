from django.contrib import admin
# from .models import related models
from .models import CarModel, CarMake


class CarModelInline(admin.StackedInline):
    model = CarModel
    extra = 5

# Register your models here.
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'dealerId', 'carType', 'year']
    list_filter = ['year']
    search_fields = ['name', 'carType']

class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ['name', 'description']
    search_fields = ['name']

admin.site.register(CarMake, CarMakeAdmin)
admin.site.register(CarModel, CarModelAdmin)
