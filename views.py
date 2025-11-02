from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import F, Case, When, IntegerField
from .models import Product, Category
from django.db.models import Q, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg
from reviews.forms import ReviewForm
from cart.forms import CartAddProductForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render


def about_view(request):
    """Сторінка 'Про нас'."""
    return render(request, 'main/about.html')

def contact_view(request):
    """Сторінка 'Контакти'."""
    return render(request, 'main/contact.html')

def get_categories():
    return Category.objects.filter(is_active=True).order_by('name')


def product_list(request, category_slug=None):
    """
    Відображає список товарів з фільтрацією, пошуком, сортуванням та пагінацією.
    """
    categories = get_categories()
    products = Product.objects.filter(is_available=True)
    category = None
    cart_product_form = CartAddProductForm()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).distinct()

    sort_by = request.GET.get('sort', 'new')
    
    if sort_by == 'new':
        products = products.order_by('-created_at')
    elif sort_by == 'old':
        products = products.order_by('created_at')
    elif sort_by == 'popular':
        products = products.order_by('-views')
    elif sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'name':
        products = products.order_by('name')


    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    
    try:
        products_on_page = paginator.page(page_number)
    except PageNotAnInteger:
        products_on_page = paginator.page(1)
    except EmptyPage:
        products_on_page = paginator.page(paginator.num_pages)

    context = {
        'products': products_on_page, 
        'page_obj': products_on_page, 
        'paginator': paginator,
        'categories': categories,
        'category': category,
        'current_sort': sort_by,
        'search_query': search_query,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'main/product-list.html', context)


def product_detail(request, id, slug):
    """
    Відображає деталі товару, збільшує лічильник переглядів та показує схожі товари.
    """
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    reviews = product.reviews.select_related('user').all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.product = product
            new_review.user = request.user
            
            try:
                new_review.save()
                messages.success(request, "Ваш відгук успішно додано!")
            except Exception:
                messages.error(request, "Ви вже залишили відгук на цей товар. Ви можете залишити лише один.")
                
            return redirect ('main:product-detail', id=product.id, slug=slug)
    else:
        form = ReviewForm()

    cart_product_form = CartAddProductForm()
    product.views = F('views') + 1
    product.save(update_fields=['views'])
    product.refresh_from_db()
    
    related_products = Product.objects.filter(
        category=product.category, 
        is_available=True
    ).exclude(id=product.id).order_by('?')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'categories': get_categories(),
        'reviews': reviews,
        'average_rating': average_rating, 
        'form': form,
        'cart_product_form': cart_product_form,
    }
    return render(request, 'main/product-detail.html', context)