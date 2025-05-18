from rest_framework import serializers
from .models import Category, Product, Order
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_name', 'stock', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'product_name', 'product_price', 'quantity', 'status', 'total_price', 'shipping_address', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'user']

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['product', 'quantity', 'shipping_address']
        
    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('product')
        quantity = validated_data.get('quantity', 1)
        
        # Calculate total price
        total_price = product.price * quantity
        
        # Create order
        order = Order.objects.create(
            user=user,
            product=product,
            quantity=quantity,
            shipping_address=validated_data.get('shipping_address'),
            total_price=total_price,
            status='pending'
        )
        
        return order 