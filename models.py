from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from ckeditor_uploader.fields import RichTextUploadingField
from django.utils import timezone
from decimal import Decimal


try:
    from discounts.models import Discount 
except ImportError:
    Discount = None


SUPPLIER_CHOICES = (
    ('Anabel Arto', 'Anabel Arto'),
    ('Jasmine', 'Jasmine'),
    ('Lana', 'Lana'),
    ('Luna', 'Luna'),
    ('LanaS', 'LanaS'),
    ('Acousma', 'Acousma'),
    ('Anfen', 'Anfen'),
    ('Donafen', 'Donafen'),
    ('Diorella', 'Diorella'),
    ('Balaloum', 'Balaloum'),
    ('Vienetta', 'Vienetta'),
    ("Victoria's Secret", "Victoria's Secret"),
    ('Nicoletta', 'Nicoletta'),
    ('Others', 'Others'),
)
class Category(models.Model):
    name = models.CharField(max_length=100, db_index=True, verbose_name="Назва")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адреса")
    description = models.TextField(blank=True, verbose_name="Опис")
    image = models.ImageField(upload_to="categories/", blank=True, verbose_name="Зображення")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        ordering = ('name',)
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Повертає URL для фільтрації товарів за цією категорією."""
        return reverse('main:product_list_by_category', args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,  
        blank=True,
        verbose_name="Категорія"
    )
    supplier = models.CharField(
        max_length=200,
        choices=SUPPLIER_CHOICES,
        default='Others',
        verbose_name='Постачальник/Виробник'
    )
    name = models.CharField(max_length=200, db_index=True, verbose_name="Назва")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-адреса")
    description = models.TextField(blank=True, verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    is_available = models.BooleanField(default=True, db_index=True, verbose_name="В наявності")

    image = models.ImageField(upload_to="products/%Y/%m/%d", blank=True, verbose_name="Зображення")
    views = models.IntegerField(default=0, verbose_name="Перегляди")
    featured = models.BooleanField(default=False, verbose_name="Рекомендований")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Оновлено")
    detailed_description = RichTextUploadingField(
        blank=True, 
        null=True, 
        verbose_name="Детальний опис")
    
    discount_percent = models.IntegerField(
        default=0, 
        verbose_name="Постійна знижка (%)"
    ) 

    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_label = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        indexes = [
            models.Index(fields=['id', 'slug']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('main:product-detail', kwargs={
            'id': self.id, 
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def get_current_price(self):
        base_price = self.price

        if not isinstance(base_price, Decimal):
            base_price = Decimal(str(base_price))

        active_discount = None
        if Discount:
            active_discount = Discount.objects.filter(
                product=self, 
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            ).first()
            
        if active_discount:
            discount_value = Decimal(str(active_discount.value))
            
            if active_discount.discount_type == 'percentage':
                discount_amount = base_price * (discount_value / Decimal('100'))
                return base_price - discount_amount
            
            elif active_discount.discount_type == 'fixed':
                return max(Decimal('0'), base_price - discount_value)

        elif self.discount_percent and self.discount_percent > 0:
            discount_percentage = Decimal(str(self.discount_percent))
            discount_amount = base_price * (discount_percentage / Decimal('100'))
            return base_price - discount_amount

        return base_price
    

    def get_discounted_price(self):
        return self.get_current_price()


    def get_average_rating(self):
        """Розраховує середній рейтинг активних відгуків."""
        average = self.reviews.filter(is_active=True).aggregate(Avg('rating'))
        return round(average['rating__avg'], 1) if average['rating__avg'] else 0.0

    def get_reviews_count(self):
        """Повертає кількість активних відгуків."""
        return self.reviews.filter(is_active=True).count()
        
    def get_rating_distribution(self):
        """Повертає розподіл оцінок (1-5 зірок)."""
        distribution = {}
        total_reviews = self.get_reviews_count()
        
        counts = self.reviews.filter(is_active=True).values('rating').annotate(count=Count('rating'))
        
        for i in range(1, 6):
            count_obj = next((item for item in counts if item['rating'] == i), None)
            count = count_obj['count'] if count_obj else 0
            percent = (count / total_reviews * 100) if total_reviews else 0
            
            distribution[i] = {
                'count': count,
                'percent': round(percent),
                'stars': '★' * i + '☆' * (5 - i)
            }
            

        return dict(sorted(distribution.items(), reverse=True))