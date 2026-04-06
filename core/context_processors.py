from catalog.models import Category, Product
from .models import FooterLink, NavItem, SiteSettings


def site_context(request):
    mega_categories = []
    top_categories = Category.objects.filter(parent__isnull=True).prefetch_related('children')[:6]
    for category in top_categories:
        children = list(category.children.all()[:8])
        featured_products = list(Product.objects.filter(category=category, is_active=True)[:4])
        if not featured_products and children:
            featured_products = list(Product.objects.filter(category__in=children, is_active=True)[:4])
        mega_categories.append({
            'category': category,
            'children': children,
            'featured_products': featured_products,
        })
    return {
        'site_settings': SiteSettings.load(),
        'primary_nav_items': NavItem.objects.filter(location=NavItem.Location.PRIMARY, is_active=True).order_by('order'),
        'footer_company_links': FooterLink.objects.filter(group=FooterLink.Group.COMPANY, is_active=True).order_by('order'),
        'footer_customer_links': FooterLink.objects.filter(group=FooterLink.Group.CUSTOMER, is_active=True).order_by('order'),
        'footer_help_links': FooterLink.objects.filter(group=FooterLink.Group.HELP, is_active=True).order_by('order'),
        'mega_categories': mega_categories,
    }
