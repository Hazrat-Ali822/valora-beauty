from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Pages
    path('', views.home, name='home'),
    
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('collections/', views.collections, name='collections'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile, name='profile'),
]
