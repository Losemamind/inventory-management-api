
from django.contrib import admin
from .models import Category, Product, StockTransaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'sku',
        'category',
        'price',
        'stock',
        'min_stock',
        'is_active',
    )

    list_filter = ('category', 'is_active')
    search_fields = ('name', 'sku')
    list_editable = ('is_active',)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'product',
        'user',
        'transaction_type',
        'quantity',
        'created_at',
    )

    list_filter = ('transaction_type', 'created_at')
    search_fields = ('product__name', 'user__username')
