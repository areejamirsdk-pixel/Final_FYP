from django.contrib import admin
from .models import *
# Register your models here.

# admin.site.register(Product)
admin.site.register(Review)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)


admin.display(ordering='countInStock')


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'countInStock']
    list_editable = ['countInStock']


@admin.display(ordering='countInStock')
def invertory_status(self, product):
    if product.inventory < 10:
        return ('LOW')
    return ('OK')


admin.site.register(Product, ProductAdmin)
