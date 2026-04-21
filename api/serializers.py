from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.models import UserProfile, WishlistItem
from catalog.models import Category, Product, ProductReview, ProductVariant
from orders.cart_utils import add_to_cart, build_cart_totals, get_cart_items, update_cart_quantity
from orders.models import Address

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'children']

    def get_children(self, obj):
        return [{'id': child.id, 'name': child.name, 'slug': child.slug} for child in obj.children.all()]


class ProductVariantSerializer(serializers.ModelSerializer):
    effective_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = ['id', 'attribute_name', 'value', 'color_hex', 'sku', 'stock', 'is_default', 'effective_price']

    def get_effective_price(self, obj):
        return str(obj.price_override or obj.product.price)


class ProductSerializer(serializers.ModelSerializer):
    image = serializers.CharField(source='primary_image_url', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    in_stock = serializers.BooleanField(read_only=True)
    is_orderable = serializers.BooleanField(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'slug',
            'brand',
            'category_name',
            'price',
            'compare_at_price',
            'discount_percentage',
            'stock',
            'in_stock',
            'is_orderable',
            'image',
            'url',
            'short_description',
            'variants',
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductReview
        fields = ['id', 'reviewer_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'name', 'phone']

    def create(self, validated_data):
        email = validated_data['email'].strip().lower()
        name = validated_data.pop('name', '').strip()
        phone = validated_data.pop('phone', '').strip()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=validated_data['password'],
            first_name=name,
        )
        if name or phone:
            UserProfile.objects.update_or_create(user=user, defaults={'phone': phone})
        return user


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id',
            'full_name',
            'phone',
            'country',
            'city',
            'area',
            'postcode',
            'address_line',
            'delivery_type',
            'is_default',
        ]


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'created_at']


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0, max_value=99)


class CartItemAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1, max_value=99, default=1)

    def save(self, **kwargs):
        request = self.context['request']
        product = Product.objects.get(id=self.validated_data['product_id'], is_active=True)
        variant = None
        if self.validated_data.get('variant_id'):
            variant = product.variants.filter(id=self.validated_data['variant_id']).first()
        add_to_cart(request, product, quantity=self.validated_data['quantity'], variant=variant)
        return product


class CartSummarySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    subtotal = serializers.CharField()
    total = serializers.CharField()
    discount_total = serializers.CharField()
    items = serializers.ListField()

    @staticmethod
    def from_request(request):
        items, subtotal = get_cart_items(request)
        totals = build_cart_totals(subtotal)
        return {
            'count': sum(item['quantity'] for item in items),
            'subtotal': str(totals['subtotal']),
            'total': str(totals['total']),
            'discount_total': str(totals['discount_total']),
            'items': [
                {
                    'key': item['key'],
                    'product_id': item['product'].id,
                    'name': item['product'].name,
                    'quantity': item['quantity'],
                    'unit_price': str(item['unit_price']),
                    'line_total': str(item['total']),
                    'image': item['product'].primary_image_url,
                }
                for item in items
            ],
        }
