from django.contrib import admin
from cart.models import Cart,payment,Order_details
admin.site.register(Cart)
admin.site.register(payment)
admin.site.register(Order_details)
