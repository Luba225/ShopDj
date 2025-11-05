from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from main.models import Product


RATING_CHOICES = (
    (1, '★☆☆☆☆ (1)'),
    (2, '★★☆☆☆ (2)'),
    (3, '★★★☆☆ (3)'),
    (4, '★★★★☆ (4)'),
    (5, '★★★★★ (5)'),
)

class Review(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews', 
        verbose_name="Товар"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Автор"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES, 
        default=5, 
        verbose_name="Оцінка"
    )
    title = models.CharField(
        max_length=100, 
        verbose_name="Заголовок"
    )
    content = models.TextField(
        max_length=1000, 
        verbose_name="Текст відгуку"
    )
    advantages = models.TextField(
        blank=True, 
        verbose_name="Переваги"
    )
    disadvantages = models.TextField(
        blank=True, 
        verbose_name="Недоліки"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Створено"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Оновлено"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Активний (Модерація)"
    )
    helpful_count = models.IntegerField(
        default=0, 
        verbose_name="Корисно (Лічильник)"
    )

    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        unique_together = ['product', 'author']
        ordering = ['-created_at']

    def __str__(self):
        return f"Відгук {self.rating}★ на {self.product.name} від {self.author.username}"

    def get_rating_display_stars(self):
        """Повертає рядок зірок для відображення оцінки."""
        full_stars = '★' * self.rating
        empty_stars = '☆' * (5 - self.rating)
        return full_stars + empty_stars