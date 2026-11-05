from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    StockTransactionViewSet,
)

router = DefaultRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='category'
)

router.register(
    'products',
    ProductViewSet,
    basename='product'
)

router.register(
    'transactions',
    StockTransactionViewSet,
    basename='transaction'
)

urlpatterns = [
    path('', include(router.urls)),
]