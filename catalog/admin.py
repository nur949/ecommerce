from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductVariant

admin.site.site_header = 'Zynvo Administration'
admin.site.site_title = 'Zynvo Admin'
admin.site.index_title = 'Store operations'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('preview', 'image', 'alt_text', 'order')
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:72px;height:72px;object-fit:cover;border-radius:12px;"/>', obj.image.url)
        return '—'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0
    fields = ('attribute_name', 'value', 'color_hex', 'sku', 'price_override', 'stock', 'image', 'is_default')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'name', 'category', 'price', 'stock', 'is_active', 'is_daily_deal', 'is_new', 'is_trending')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'is_active', 'is_daily_deal', 'is_new', 'is_trending', 'is_featured')
    search_fields = ('name', 'sku', 'brand', 'collection_label')
    list_editable = ('price', 'stock', 'is_active')
    autocomplete_fields = ('category',)
    inlines = [ProductImageInline, ProductVariantInline]
    fieldsets = (
        ('Core', {'fields': ('category', 'name', 'slug', 'brand', 'sku', 'short_description', 'description', 'featured_image')}),
        ('Pricing & Inventory', {'fields': ('price', 'compare_at_price', 'stock', 'badge_text')}),
        ('Merchandising', {'fields': ('is_active', 'is_featured', 'is_new', 'is_daily_deal', 'is_trending', 'collection_label', 'trending_group', 'deal_ends_at')}),
        ('Content', {'fields': ('specifications', 'return_policy')}),
        ('SEO', {'classes': ('collapse',), 'fields': ('meta_title', 'meta_description')}),
    )

    def thumb(self, obj):
        if obj.featured_image:
            return format_html('<img src="{}" style="width:48px;height:48px;object-fit:cover;border-radius:10px;"/>', obj.featured_image.url)
        return '—'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_featured', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured', 'order')
    search_fields = ('name',)
