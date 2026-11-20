from rest_framework import serializers
from .models import Category, Service, Realization, Product, Order, OrderItem, ContactMessage, Application


class CategorySerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'type', 'type_display', 'description', 'icon']


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    features_list = serializers.ListField(source='get_features_list', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 'icon',
            'short_description', 'full_description', 'features', 'features_list',
            'image_url', 'is_featured', 'is_active', 'order', 'created_at'
        ]


class RealizationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    tech_tags = serializers.ListField(source='get_tech_tags', read_only=True)

    class Meta:
        model = Realization
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 'client_name',
            'short_description', 'full_description', 'tech_stack', 'tech_tags',
            'image_url', 'completion_date', 'project_url', 'is_featured', 'is_active', 'created_at'
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    tech_tags = serializers.ListField(source='get_tech_tags', read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 'platform',
            'platform_display', 'version', 'icon', 'short_description',
            'full_description', 'tech_stack', 'tech_tags', 'image_url',
            'demo_url', 'download_url', 'badge', 'is_featured', 'is_active',
            'order', 'created_at'
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    category_slug = serializers.CharField(source='category.slug', read_only=True, default='')
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    specs_dict = serializers.ListField(source='get_specs_dict', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'category_name', 'category_slug',
            'price', 'discount_price', 'current_price', 'short_description', 'full_description',
            'stock', 'badge', 'rating', 'reviews_count',
            'image_url', 'specs', 'specs_dict', 'is_featured', 'is_active', 'created_at'
        ]



class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'price', 'quantity',
            'subtotal', 'product_image_url', 'product_category'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_email',
            'customer_phone', 'delivery_address', 'city', 'total_amount',
            'status', 'status_display', 'notes', 'created_at', 'items'
        ]


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'service_interest', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'name', 'email', 'phone', 'subject', 'service_interest', 'message', 'created_at']
