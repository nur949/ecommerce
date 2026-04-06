from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=180)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    specifications = models.TextField(blank=True)
    return_policy = models.TextField(blank=True, default='7 days replacement available for damaged or defective items.')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.PositiveIntegerField(default=0)
    featured_image = models.ImageField(upload_to='products/', blank=True, null=True)
    brand = models.CharField(max_length=80, default='Zynvo')
    badge_text = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new = models.BooleanField(default=False)
    is_daily_deal = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    collection_label = models.CharField(max_length=80, blank=True)
    trending_group = models.CharField(max_length=80, blank=True, default='General')
    deal_ends_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', args=[self.slug])

    @property
    def demo_image_url(self):
        product_name = (self.name or '').lower()
        product_brand = (self.brand or '').lower()
        text = f'{product_name} {product_brand}'
        image_map = [
            (('laptop', 'notebook', 'macbook'), 'https://images.pexels.com/photos/18105/pexels-photo.jpg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('desktop', 'pc', 'tower', 'computer'), 'https://images.pexels.com/photos/704730/pexels-photo-704730.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('monitor', 'display'), 'https://images.pexels.com/photos/777001/pexels-photo-777001.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('phone', 'smartphone', 'iphone', 'android'), 'https://images.pexels.com/photos/607812/pexels-photo-607812.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('tablet', 'ipad'), 'https://images.pexels.com/photos/1334597/pexels-photo-1334597.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('camera',), 'https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('headphone', 'earbud', 'earphone', 'speaker', 'audio'), 'https://images.pexels.com/photos/3394665/pexels-photo-3394665.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('keyboard', 'mouse'), 'https://images.pexels.com/photos/2115256/pexels-photo-2115256.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('gaming chair', 'chair'), 'https://images.pexels.com/photos/7862493/pexels-photo-7862493.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('router', 'network', 'wifi'), 'https://images.pexels.com/photos/2881229/pexels-photo-2881229.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('printer',), 'https://images.pexels.com/photos/159751/book-address-book-learning-learn-159751.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('projector',), 'https://images.pexels.com/photos/2873486/pexels-photo-2873486.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('washing machine',), 'https://images.pexels.com/photos/5591536/pexels-photo-5591536.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('air conditioner', 'ac', 'inverter'), 'https://images.pexels.com/photos/5824519/pexels-photo-5824519.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('blender', 'mixer', 'kitchen', 'appliance'), 'https://images.pexels.com/photos/4112598/pexels-photo-4112598.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('drone',), 'https://images.pexels.com/photos/724921/pexels-photo-724921.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('ups', 'power station', 'battery', 'power'), 'https://images.pexels.com/photos/4526414/pexels-photo-4526414.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('sewing machine',), 'https://images.pexels.com/photos/4610359/pexels-photo-4610359.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('console', 'playstation', 'ps5', 'xbox'), 'https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
            (('tv', 'television'), 'https://images.pexels.com/photos/1201996/pexels-photo-1201996.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'),
        ]
        for keywords, image_url in image_map:
            if any(keyword in text for keyword in keywords):
                return image_url
        return 'https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=900&h=900&fit=crop'

    @property
    def primary_image_url(self):
        if self.featured_image:
            return self.featured_image.url
        return self.demo_image_url

    @property
    def discount_amount(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return self.compare_at_price - self.price
        return 0

    @property
    def discount_percentage(self):
        if self.compare_at_price and self.compare_at_price > self.price:
            return round(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def is_deal_active(self):
        return self.is_daily_deal and (self.deal_ends_at is None or self.deal_ends_at > timezone.now())


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='products/gallery/', blank=True, null=True)
    alt_text = models.CharField(max_length=140, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    attribute_name = models.CharField(max_length=50, default='Color')
    value = models.CharField(max_length=80)
    color_hex = models.CharField(max_length=7, blank=True)
    sku = models.CharField(max_length=60, blank=True)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'attribute_name', 'value')

    def __str__(self):
        return f'{self.product.name} - {self.attribute_name}: {self.value}'
