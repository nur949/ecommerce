from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class SiteSettings(SingletonModel):
    site_name = models.CharField(max_length=100, default='Zynvo')
    tagline = models.CharField(max_length=150, default='Smart living, curated beautifully.')
    support_phone = models.CharField(max_length=30, default='+880 1700-000000')
    support_email = models.EmailField(default='support@zynvo.com')
    address = models.CharField(max_length=255, default='Dhaka, Bangladesh')
    copyright_text = models.CharField(max_length=255, default='© 2026 Zynvo Ltd. All Rights Reserved')
    hero_title = models.CharField(max_length=140, default='Elevate your everyday with Zynvo')
    hero_subtitle = models.CharField(
        max_length=255,
        default='Discover hand-picked lifestyle, fashion, and gadget essentials with fast delivery.',
    )
    announcement_text = models.CharField(max_length=255, default='Free shipping on orders over ৳3000')
    corporate_cta_title = models.CharField(max_length=140, default='Become Our Corporate Partner')
    corporate_cta_url = models.CharField(max_length=255, default='/corporate/')
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    def __str__(self):
        return 'Site settings'


class NavItem(models.Model):
    class Location(models.TextChoices):
        PRIMARY = 'primary', 'Primary'
        CATEGORY = 'category', 'Category'

    title = models.CharField(max_length=80)
    url = models.CharField(max_length=255, default='#')
    location = models.CharField(max_length=20, choices=Location.choices, default=Location.PRIMARY)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return f'{self.title} ({self.location})'


class FooterLink(models.Model):
    class Group(models.TextChoices):
        COMPANY = 'company', 'Company'
        CUSTOMER = 'customer', 'Customer'
        HELP = 'help', 'Help'

    title = models.CharField(max_length=100)
    url = models.CharField(max_length=255, default='#')
    group = models.CharField(max_length=20, choices=Group.choices)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['group', 'order', 'title']

    def __str__(self):
        return self.title


class HomeSection(models.Model):
    key = models.SlugField(unique=True)
    title = models.CharField(max_length=120)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class HeroSlide(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=255, blank=True)
    cta_text = models.CharField(max_length=40, default='Shop Now')
    cta_url = models.CharField(max_length=255, default='/shop/')
    accent_label = models.CharField(max_length=40, blank=True, help_text='Example: Up to 38% Off')
    image = models.ImageField(upload_to='hero/', blank=True, null=True)
    bg_color = models.CharField(max_length=20, default='#eef6ff')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class PromoBanner(models.Model):
    title = models.CharField(max_length=120)
    subtitle = models.CharField(max_length=120, blank=True)
    url = models.CharField(max_length=255, default='/shop/')
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    color = models.CharField(max_length=20, default='#f0f7ff')
    group = models.CharField(max_length=30, default='hero_right', help_text='hero_right, gadget, unlimited')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['group', 'order', 'id']

    def __str__(self):
        return f'{self.group}: {self.title}'


class StaticPage(models.Model):
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:page', args=[self.slug])


class BlogCategory(models.Model):
    name = models.CharField(max_length=80)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('core:blog_detail', args=[self.slug])

    @property
    def demo_image_url(self):
        text = f'{(self.title or "").lower()} {(self.excerpt or "").lower()}'
        image_map = [
            (('skincare', 'skin', 'beauty', 'glow', 'serum'), 'https://images.pexels.com/photos/6621434/pexels-photo-6621434.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'),
            (('gadget', 'smart', 'tech', 'phone', 'laptop'), 'https://images.pexels.com/photos/356056/pexels-photo-356056.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'),
            (('home', 'kitchen', 'appliance', 'living'), 'https://images.pexels.com/photos/5824519/pexels-photo-5824519.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'),
            (('fashion', 'style', 'outfit'), 'https://images.pexels.com/photos/994523/pexels-photo-994523.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'),
            (('delivery', 'shipping', 'order'), 'https://images.pexels.com/photos/6169034/pexels-photo-6169034.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'),
        ]
        for keywords, image_url in image_map:
            if any(keyword in text for keyword in keywords):
                return image_url
        return 'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&fit=crop'

    @property
    def primary_image_url(self):
        if self.featured_image:
            return self.featured_image.url
        return self.demo_image_url
