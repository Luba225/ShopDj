from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from main.models import Category
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from orders.models import Order
from orders.models import OrderItem

def get_categories():
    return Category.objects.filter(is_active=True).order_by('name')


def login_view(request):
    categories = get_categories()
    
    if request.user.is_authenticated:
        return redirect('main:product-list')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            next_url = request.POST.get('next') or reverse('main:product-list')
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    context = {'form': form, 'categories': categories}
    return render(request, 'accounts/login.html', context)


def logout_view(request):
    logout(request)
    return redirect('main:product-list')


def register_view(request):
    categories = get_categories()
    
    if request.user.is_authenticated:
        return redirect('main:product-list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:product-list')
    else:
        form = UserCreationForm()
        
    context = {'form': form, 'categories': categories}
    return render(request, 'accounts/register.html', context)

@login_required
def profile_view(request):
    """
    Відображає основну сторінку профілю користувача.
    """
    context = {
        'active_tab': 'profile',
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def order_history_view(request):
    """
    Відображає список усіх замовлень, зроблених поточним авторизованим користувачем.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created')
    context = {
        'orders': orders,
        'active_tab': 'orders',
    }
    
    return render(request, 'accounts/order_history.html', context)

class AdminAccessRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            user = request.user
            
            if not user.is_authenticated or not user.is_staff:
                if request.path != reverse('admin:login'):
                    return redirect('main:product-list')
                    
        return self.get_response(request)