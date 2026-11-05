
from django.db import models, transaction
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from accounts.permissions import IsAdminOrReadOnly

from .models import Category, Product, StockTransaction
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    StockTransactionSerializer,
    StockMovementSerializer,
)


# จัดการหมวดหมู่สินค้า
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]


# จัดการสินค้า
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()

        low_stock = self.request.query_params.get('low_stock')

        if low_stock == 'true':
            queryset = queryset.filter(
                stock__lte=models.F('min_stock')
            )

        return queryset

    # จัดการกรณีลบสินค้าที่มีประวัติธุรกรรม
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "ไม่สามารถลบสินค้านี้ได้ "
                        "เนื่องจากมีประวัติการรับเข้า-เบิกออกสินค้าอยู่"
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    # รับสินค้าเข้าและเบิกสินค้าออก
    def stock_movement(self, request, pk, movement_type):
        movement_serializer = StockMovementSerializer(
            data=request.data
        )
        movement_serializer.is_valid(raise_exception=True)

        quantity = movement_serializer.validated_data['quantity']
        note = movement_serializer.validated_data.get('note', '')

        with transaction.atomic():
            product = get_object_or_404(
                Product.objects.select_for_update(),
                pk=pk
            )

            if not product.is_active:
                return Response(
                    {'message': 'สินค้านี้ถูกปิดใช้งาน'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if movement_type == 'OUT' and product.stock < quantity:
                return Response(
                    {
                        'message': 'สินค้าในคลังมีไม่เพียงพอ',
                        'available_stock': product.stock,
                        'requested_quantity': quantity,
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if movement_type == 'IN':
                product.stock += quantity
            else:
                product.stock -= quantity

            product.save(update_fields=['stock', 'updated_at'])

            stock_transaction = StockTransaction.objects.create(
                product=product,
                user=request.user,
                transaction_type=movement_type,
                quantity=quantity,
                note=note
            )

        return Response(
            {
                'message': (
                    'รับสินค้าเข้าสำเร็จ'
                    if movement_type == 'IN'
                    else 'เบิกสินค้าออกสำเร็จ'
                ),
                'product': product.name,
                'transaction_id': stock_transaction.id,
                'transaction_type': movement_type,
                'quantity': quantity,
                'remaining_stock': product.stock,
            },
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='stock-in')
    def stock_in(self, request, pk=None):
        return self.stock_movement(request, pk, 'IN')

    @action(detail=True, methods=['post'], url_path='stock-out')
    def stock_out(self, request, pk=None):
        return self.stock_movement(request, pk, 'OUT')

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='low_stock',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='กรองสินค้าที่มีจำนวนคงเหลือต่ำกว่าหรือเท่ากับ Min Stock',
                required=False,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# ดูประวัติการรับเข้าและเบิกออก
class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StockTransaction.objects.select_related(
        'product',
        'user'
    ).all()

    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
