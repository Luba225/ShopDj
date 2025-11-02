from django.db import models
from django.conf import settings
from main.models import Product

RATING_CHOICES = (
    (1, '★'),
    (2, '★★'),
    (3, '★★★'),
    (4, '★★★★'),
    (5, '★★★★★'),
)

class Review(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Користувач"
    )
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        verbose_name="Товар"
    )
    
    rating = models.IntegerField(
        choices=RATING_CHOICES, 
        default=5, 
        verbose_name="Рейтинг"
    )
    
    content = models.TextField(
        verbose_name="Текст відгуку"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Дата створення"
    )
    
    class Meta:
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"
        ordering = ['-created_at']
        unique_together = ('user', 'product') 

    def __str__(self):
        return f'{self.user.username} - {self.product.name} ({self.rating} зірок)'