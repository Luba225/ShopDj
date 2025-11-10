from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Product
from .cart import Cart
from .forms import CartAddProductForm
from decimal import Decimal



@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        quantity = cleaned_data['quantity']
        override_quantity = cleaned_data['override']
        final_price = product.price 
        final_price = product.get_current_price()

        cart.add(
            product=product, 
            quantity=quantity, 
            override_quantity=override_quantity, 
            price=final_price
        )
        
    return redirect('cart:cart_detail')

@require_POST
def cart_remove(request, product_id):
    """
    Видаляє товар із кошика. Вимагає POST-запиту.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    """
    Відображає вміст кошика.
    """
    cart = Cart(request)
  
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(
                                        initial={'quantity': item['quantity'], 
                                                 'override': True})
        
    return render(request, 'cart/detail.html', {'cart': cart})