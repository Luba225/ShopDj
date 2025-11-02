from decimal import Decimal
from django.conf import settings
from main.models import Product

class Cart:
    def __init__(self, request):
        """
        Ініціалізація кошика.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        """
        Додати товар до кошика або оновити його кількість.
        Ключ: ID товару. Значення: { 'quantity': X, 'price': Y }
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': str(product.price)}

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        """
        Видалити товар із кошика.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            
    def __iter__(self):
        """
        Перебір елементів у кошику та отримання товарів з бази даних.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Підрахувати загальну кількість товарів у кошику.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Підрахувати загальну вартість товарів у кошику.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()