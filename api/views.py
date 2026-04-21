from django.contrib.auth import authenticate
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import WishlistItem
from catalog.models import Category, Product, ProductReview
from orders.cart_utils import get_cart_items, make_item_key, remove_from_cart, update_cart_quantity

from .serializers import (
    CartItemAddSerializer,
    CartItemUpdateSerializer,
    CartSummarySerializer,
    CategorySerializer,
    ProductReviewSerializer,
    ProductSerializer,
    RegisterSerializer,
    WishlistItemSerializer,
)

User = get_user_model()


def _token_pair_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


class RegisterApiView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'user': {'id': user.id, 'email': user.email, 'name': user.first_name}, 'token': _token_pair_for_user(user)}, status=status.HTTP_201_CREATED)


class LoginApiView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        password = request.data.get('password') or ''
        user = authenticate(request, username=email, password=password)
        if user is None:
            found = User.objects.filter(email__iexact=email).only('username').first()
            user = authenticate(request, username=found.username if found else email, password=password)
        if user is None:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'user': {'id': user.id, 'email': user.email, 'name': user.first_name}, 'token': _token_pair_for_user(user)})


class CategoryListApiView(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.filter(parent__isnull=True).prefetch_related('children')


class ProductListApiView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = (
            Product.objects.filter(is_active=True)
            .select_related('category')
            .prefetch_related('variants')
            .annotate(average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)), review_count=Count('reviews', filter=Q(reviews__is_approved=True)))
        )
        q = (self.request.GET.get('q') or '').strip()
        category = (self.request.GET.get('category') or '').strip()
        brand = (self.request.GET.get('brand') or '').strip()
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(brand__icontains=q) | Q(description__icontains=q) | Q(sku__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if brand:
            qs = qs.filter(brand__iexact=brand)
        sort_map = {'price': 'price', '-price': '-price', 'popular': '-review_count', 'latest': '-created_at'}
        return qs.order_by(sort_map.get(self.request.GET.get('sort') or 'latest', '-created_at'))


class ProductDetailApiView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'slug'
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('variants', 'gallery')


class ProductReviewListCreateApiView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        return ProductReview.objects.filter(product__slug=self.kwargs['slug'], is_approved=True)

    def perform_create(self, serializer):
        product = get_object_or_404(Product, slug=self.kwargs['slug'], is_active=True)
        serializer.save(
            product=product,
            user=self.request.user if self.request.user.is_authenticated else None,
            reviewer_name=(self.request.data.get('reviewer_name') or self.request.user.get_full_name() or 'Guest').strip(),
            reviewer_email=(self.request.data.get('reviewer_email') or getattr(self.request.user, 'email', '')).strip(),
            is_verified_purchase=self.request.user.is_authenticated and self.request.user.order_set.filter(items__product=product).exists(),
        )


class WishlistApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = request.user.wishlist_items.select_related('product', 'product__category').all()
        return Response({'results': WishlistItemSerializer(queryset, many=True).data})

    def post(self, request):
        product = get_object_or_404(Product, id=request.data.get('product_id'), is_active=True)
        item, _ = WishlistItem.objects.get_or_create(user=request.user, product=product)
        return Response({'id': item.id}, status=status.HTTP_201_CREATED)


class WishlistDetailApiView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, product_id):
        WishlistItem.objects.filter(user=request.user, product_id=product_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartApiView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(CartSummarySerializer.from_request(request))

    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CartSummarySerializer.from_request(request), status=status.HTTP_201_CREATED)


class CartItemApiView(views.APIView):
    permission_classes = [permissions.AllowAny]

    def patch(self, request, item_key):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        update_cart_quantity(request, item_key, serializer.validated_data['quantity'])
        return Response(CartSummarySerializer.from_request(request))

    def delete(self, request, item_key):
        remove_from_cart(request, item_key)
        return Response(status=status.HTTP_204_NO_CONTENT)
