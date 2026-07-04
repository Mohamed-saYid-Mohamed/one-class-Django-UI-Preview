from django.urls import path
from .views import (
    index, order_success, product_detail,
    register_view, login_view, logout_view,
    cart_detail, add_to_cart, update_cart, remove_from_cart,
    checkout, my_orders, view_order_detail, cancel_order, reorder
)

urlpatterns = [
    path('', index, name='index'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('order-success/<int:order_id>/', order_success, name='order_success'),
    
    # Auth
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # Cart
    path('cart/', cart_detail, name='cart_detail'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/update/', update_cart, name='update_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    
    # Checkout & Orders
    path('checkout/', checkout, name='checkout'),
    path('orders/', my_orders, name='my_orders'),
    path('orders/<int:order_id>/', view_order_detail, name='view_order_detail'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
    path('orders/<int:order_id>/reorder/', reorder, name='reorder'),
]


