from django.urls import path
from . import views

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),

    # Product manage (individual)
    path('product/<int:id>/edit/', views.edit_product, name='edit_product'),
    path('product/<int:id>/delete/', views.delete_product, name='delete_product'),
    
    # Cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:id>/', views.order_confirmation, name='order_confirmation'),
    
    # Product Management (read-only)
    path('add/', views.add_product, name='add_product'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # User Dashboard
    path('my-orders/', views.user_orders, name='user_orders'),
]
