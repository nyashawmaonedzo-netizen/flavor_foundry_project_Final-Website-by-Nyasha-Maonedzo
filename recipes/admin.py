from django.contrib import admin
from django.db.models import Avg, Count
from .models import Product, Order, OrderItem, Category, Review, Wishlist


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count')
    search_fields = ('name',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'is_in_stock', 'available', 'average_rating', 'review_count', 'created_at')
    list_filter = ('category', 'available', 'created_at', 'price')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'review_count')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'category', 'price')
        }),
        ('Images', {
            'fields': ('image_url', 'image')
        }),
        ('Inventory', {
            'fields': ('available', 'stock')
        }),
        ('Reviews & Ratings', {
            'fields': ('average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def average_rating(self, obj):
        return f"★ {obj.get_average_rating():.1f}" if obj.reviews.exists() else "No ratings"
    average_rating.short_description = 'Average Rating'
    
    def review_count(self, obj):
        return obj.reviews.count()
    review_count.short_description = 'Review Count'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'email', 'total_amount', 'item_count', 'created_at')
    list_filter = ('created_at', 'user', 'city')
    search_fields = ('full_name', 'email', 'shipping_address', 'city', 'postal_code', 'user__username')
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'total_amount')
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'id', 'created_at', 'total_amount')
        }),
        ('Customer Information', {
            'fields': ('full_name', 'email')
        }),
        ('Shipping Address', {
            'fields': ('shipping_address', 'city', 'postal_code')
        }),
    )
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'display_rating_stars', 'created_at')
    list_filter = ('rating', 'created_at', 'product', 'user')
    search_fields = ('user__username', 'product__name', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'comment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def display_rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    display_rating_stars.short_description = 'Rating'


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Items in Wishlist'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
