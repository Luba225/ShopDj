from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from ckeditor_uploader.fields import RichTextUploadingField

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