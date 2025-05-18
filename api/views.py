from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Category, Product, Order
from .serializers import (
    CategorySerializer, 
    ProductSerializer, 
    OrderSerializer, 
    OrderCreateSerializer
)
from .utils import ratelimit

# Create your views here.

# Category ViewSet
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @ratelimit(num_requests=10, timeframe=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @ratelimit(num_requests=5, timeframe=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

# Product ViewSet
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'price', 'created_at']
    
    @ratelimit(num_requests=20, timeframe=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @ratelimit(num_requests=5, timeframe=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @ratelimit(num_requests=15, timeframe=60)
    @action(detail=True, methods=['get'])
    def category_products(self, request, pk=None):
        category = get_object_or_404(Category, pk=pk)
        products = Product.objects.filter(category=category)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

# Order ViewSet
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['status', 'product__name', 'user__username']
    ordering_fields = ['created_at', 'status', 'total_price']
    
    def get_queryset(self):
        # Regular users can only see their own orders
        # Admins can see all orders
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    @ratelimit(num_requests=10, timeframe=60)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @ratelimit(num_requests=3, timeframe=60)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
        
    def perform_create(self, serializer):
        serializer.save()
        
    # Custom action to update order status
    @ratelimit(num_requests=5, timeframe=60)
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        status_value = request.data.get('status', None)
        if not status_value or status_value not in dict(Order.STATUS_CHOICES).keys():
            return Response({"error": "Invalid status value"}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = status_value
        order.save()
        serializer = self.get_serializer(order)
        return Response(serializer.data)
