from django.contrib import admin

from .models import Product, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'created_at', 'total_amount')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'email', 'shipping_address', 'city', 'postal_code')
    inlines = [OrderItemInline]


admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
