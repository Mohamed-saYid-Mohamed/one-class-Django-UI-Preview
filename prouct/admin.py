from django.contrib import admin
from .models import Product, Order, OrderItem, Cart, CartItem

class DisplayProduct(admin.ModelAdmin):
    list_display = ("product_id", "name", "price", "stock")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name", "phone", "city", "total_price", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone", "city", "user__username")
    inlines = [OrderItemInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_items", "total_price", "created_at")
    inlines = [CartItemInline]


admin.site.register(Product, DisplayProduct)
admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)

