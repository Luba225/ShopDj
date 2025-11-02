from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import Order, OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.http import HttpResponse
from .liqpay import liqpay_client
import base64
import json

def order_create(request):
    """
    Обробляє оформлення замовлення: 
    1. Перевіряє форму клієнта.
    2. Якщо форма валідна, переносить товари з сесії Cart у базу даних OrderItem.
    3. Відправляє email-підтвердження.
    4. Очищає кошик.
    """
    cart = Cart(request)
    
    if not cart:
        return redirect('main:product-list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user

            order.save()
            
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )

            subject = f'Ваше замовлення №{order.id} на MyShop'
            message = (
                f"Шановний(а) {order.first_name},\n\n"
                f"Дякуємо за Ваше замовлення! Його номер: {order.id}.\n"
                f"Загальна сума: {order.get_total_cost()} грн.\n"
                f"Ми зв'яжемося з Вами найближчим часом для уточнення деталей доставки за адресою: {order.city}, {order.address}.\n\n"
                "З повагою,\nКоманда MyShop"
            )
            recipient_list = [order.email]
            
            try:
                send_mail(
                    subject, 
                    message, 
                    'support@myshop.com', 
                    recipient_list
                )
            except Exception as e:
                print(f"Помилка відправки листа: {e}")
            
            cart.clear()
            return render(request, 'orders/order/created.html', {'order': order})
        
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email
            }
        
        form = OrderCreateForm(initial=initial_data) 
        
    return render(request, 
                  'orders/order/create.html', 
                  {'cart': cart, 'form': form})

@login_required
def payment_start(request, order_id):
    
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.paid:
        return redirect(reverse('accounts:order_history')) 

    params = {
        'order_id': order.id,
        'amount': str(order.get_total_cost()),
        'description': f'Оплата замовлення №{order.id} у MyShop',
        'result_url': request.build_absolute_uri(reverse('orders:payment_complete')),
        # 'server_url': request.build_absolute_uri(reverse('orders:payment_callback')),
    }
    
    liqpay_data = liqpay_client.cpay_params(params)
    
    return render(request, 'orders/payment_start.html', {
        'order': order, 
        'liqpay_data': liqpay_data
    })

@csrf_exempt 
def payment_callback(request):
    """
    Обробляє POST-запит від LiqPay (Server URL).
    Перевіряє підпис (signature) та оновлює статус замовлення.
    """
    if request.method == 'POST':
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        generated_signature = liqpay_client._generate_signature(data)

        if generated_signature == signature:
            try:
                decoded_data = base64.b64decode(data).decode('utf-8')
                params = json.loads(decoded_data)
            except (base64.Error, json.JSONDecodeError):
                return HttpResponse(status=400, content="Invalid data encoding")

            order_id = params.get('order_id')
            status = params.get('status')

            if status == 'success' or status == 'sandbox':
                try:
                    order = Order.objects.get(id=order_id)
                    order.paid = True
                    order.liqpay_status = status
                    order.save()
                    
                    print(f"Оплата замовлення №{order_id} успішна. Статус: {status}")
                    
                except Order.DoesNotExist:
                    print(f"Помилка: Замовлення №{order_id} не знайдено.")
                    return HttpResponse(status=404)
            
            return HttpResponse(status=200)
        else:
            print("Помилка безпеки: Невірний підпис LiqPay.")
            return HttpResponse(status=403)
    
    return HttpResponse(status=400)

@login_required
def payment_complete(request):
    """
    Обробляє повернення користувача (Result URL).
    Тут ми показуємо повідомлення про успішну/невдалу оплату, 
    залежно від параметрів у сесії або URL.
    """
    # просто відобразимо сторінку "Дякуємо"
    
    # Пізніше тут буде логіка перевірки:
    # order_id = request.GET.get('order_id')
    # status = request.GET.get('status')
    
    return render(request, 'orders/payment_complete.html', {})