from django.contrib import admin
from .models import Category, Product, Review, Order, OrderItem, WishlistItem, ContactMessage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'is_featured']
    list_filter = ['category', 'is_featured']
    search_fields = ['name', 'description']
    list_editable = ['price', 'stock', 'is_featured']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['author', 'product', 'rating', 'created_at']
    list_filter = ['rating']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total_price', 'status', 'created_at']
    list_filter = ['status']
    list_editable = ['status']
    inlines = [OrderItemInline]

from .models import SliderImage
admin.site.register(SliderImage)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at']
    readonly_fields = ['name', 'email', 'subject', 'message', 'created_at']


admin.site.register(WishlistItem)
