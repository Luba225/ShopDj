from django.db import models
from main.models import Product
from django.contrib.auth.models import User

class Order(models.Model):

    user = models.ForeignKey(
        User, 
        related_name='orders', 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        verbose_name="Користувач"
    )

    first_name = models.CharField(max_length=50, verbose_name="Ім'я")
    last_name = models.CharField(max_length=50, verbose_name="Прізвище")
    email = models.EmailField(verbose_name="Електронна пошта")
    phone = models.CharField(max_length=20, verbose_name="Телефон", blank=True)
    address = models.CharField(max_length=250, verbose_name="Адреса доставки")
    city = models.CharField(max_length=100, verbose_name="Місто")
    

    paid = models.BooleanField(default=False, verbose_name="Оплачено") 
    created = models.DateTimeField(auto_now_add=True, verbose_name="Створено")
    updated = models.DateTimeField(auto_now=True, verbose_name="Оновлено")

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
        ]
        verbose_name = "Замовлення"
        verbose_name_plural = "Замовлення"

    def __str__(self):
        return f'Замовлення {self.id}'

    def get_total_cost(self):
        """Розраховує загальну вартість замовлення."""
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    """
    Кожен окремий товар у складі замовлення
    """
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE,
        verbose_name="Замовлення"
    )
    product = models.ForeignKey(
        Product,
        related_name='order_items',
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за одиницю")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Кількість")

    class Meta:
        verbose_name = "Позиція замовлення"
        verbose_name_plural = "Позиції замовлення"
        
    def __str__(self):
        return str(self.id)

    def get_cost(self):
        """Розраховує вартість позиції (ціна * кількість)."""
        if self.price is None:
            return 0
        return self.price * self.quantity