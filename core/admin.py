from django.contrib import admin
from django.utils.html import format_html

from .models import (
    BlogCategory,
    BlogPost,
    FooterLink,
    HeroSlide,
    HomeSection,
    NavItem,
    PromoBanner,
    SiteSettings,
    StaticPage,
    NewsletterSubscriber,
)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Brand', {'fields': ('site_name', 'tagline', 'announcement_text')}),
        ('Contact', {'fields': ('support_phone', 'support_email', 'address', 'copyright_text')}),
        ('Hero & Corporate', {'fields': ('hero_title', 'hero_subtitle', 'corporate_cta_title', 'corporate_cta_url')}),
        ('Social', {'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'linkedin_url')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(HomeSection)
class HomeSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'key', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title', 'key')


@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('location', 'is_active')
    search_fields = ('title', 'url')


@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('group', 'is_active')


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'cta_text', 'order', 'is_active')
    list_editable = ('order', 'is_active')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:84px;height:48px;object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return '-'


@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'group', 'order', 'is_active')
    list_filter = ('group', 'is_active')
    list_editable = ('order', 'is_active')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:84px;height:48px;object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return '-'


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'body')


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'excerpt', 'content')
    list_select_related = ('category',)
    date_hierarchy = 'created_at'


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'created_at')
    list_editable = ('is_active',)
    search_fields = ('email',)
