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
from .models import Product, Category, SUPPLIER_CHOICES
from django.db.models import Count
from discounts.models import Discount
from django.views.generic import DetailView
from django.utils import timezone
from decimal import Decimal

SUPPLIERS = [choice[0] for choice in SUPPLIER_CHOICES]
SUPPLIERS = [
    'Anabel Arto', 'Jasmine', 'Lana', 'Luna', 'LanaS', 'Acousma', 
    'Anfen', 'Donafen', 'Diorella', 'Balaloum', 'Vienetta', 
    "Victoria's Secret", 'Nicoletta', 'Others'
]

class ProductDetailView(DetailView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()

        active_discount = None
        try:
            active_discount = Discount.objects.filter(
                product=product, 
                is_active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now(),
            ).first() 
        except NameError:
             pass

        context['active_discount'] = active_discount
        
        final_price = product.price
        is_on_sale = False

        if active_discount:
            is_on_sale = True
            
            if active_discount.discount_type == 'percentage':
                discount_amount = product.price * (active_discount.value / 100)
                final_price = product.price - discount_amount
                
            elif active_discount.discount_type == 'fixed':
                final_price = product.price - active_discount.value
                final_price = max(0, final_price) 
        
        elif product.discount_percent and product.discount_percent > 0:
            is_on_sale = True
            final_price = product.get_discounted_price() 


        context['final_price'] = final_price
        context['base_price'] = product.price
        context['is_on_sale'] = is_on_sale
        
        return context
    
def product_list_view(request):
    categories = Category.objects.all().order_by('name')
    
    selected_category = request.GET.get('category')
    selected_supplier = request.GET.get('supplier')
    
    products = Product.objects.all()
    
    if selected_category:
        products = products.filter(category__name=selected_category)
    
    if selected_supplier:
        products = products.filter(supplier=selected_supplier)

    
    context = {
        'products': products,
        'categories': categories,
        'suppliers': SUPPLIERS,
        'selected_category': selected_category,
        'selected_supplier': selected_supplier,
    }
    
    return render(request, 'main/product_list.html', context)

def about_view(request):
    """Сторінка 'Про нас'."""
    return render(request, 'main/about.html')

def contact_view(request):
    """Сторінка 'Контакти'."""
    return render(request, 'main/contact.html')

def get_categories():
    return Category.objects.filter(is_active=True).order_by('name')


def product_list(request, category_slug=None):
    categories = Category.objects.filter(is_active=True).order_by('name')
    products = Product.objects.filter(is_available=True)
    category = None

    selected_category = request.GET.get('category')
    selected_supplier = request.GET.get('supplier')

    if selected_category:
        products = products.filter(category__name=selected_category)

    if selected_supplier:
        products = products.filter(supplier=selected_supplier)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        ).distinct()

    sort_by = request.GET.get('sort', 'new')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'views':
        products = products.order_by('-views')
    elif sort_by == 'old':
        products = products.order_by('created_at')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    products_on_page = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'products': products_on_page,
        'page_obj': products_on_page,
        'paginator': paginator,
        'suppliers': [s[0] for s in SUPPLIER_CHOICES],
        'selected_category': selected_category,
        'selected_supplier': selected_supplier,
    }

    return render(request, 'main/product-list.html', context)

def product_detail(request, id, slug):
    """
    Відображає деталі товару, збільшує лічильник переглядів, показує схожі товари
    та враховує знижки (акційні або стандартні).
    """
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    reviews = product.reviews.select_related('author').all()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    active_discount = Discount.objects.filter(
        product=product,
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    ).first()

    base_price = Decimal(str(product.price))
    final_price = base_price
    is_on_sale = False


    if active_discount:
        is_on_sale = True
        discount_value = Decimal(str(active_discount.value))

        if active_discount.discount_type == 'percentage':
            discount_amount = base_price * (discount_value / Decimal('100'))
            final_price = base_price - discount_amount

        elif active_discount.discount_type == 'fixed':
            final_price = base_price - discount_value
            final_price = max(Decimal('0'), final_price)


    elif getattr(product, 'discount_percent', 0) > 0:
        is_on_sale = True
        final_price = Decimal(str(product.get_discounted_price()))

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.product = product
            new_review.author = request.user
            try:
                new_review.save()
                messages.success(request, "Ваш відгук успішно додано!")
            except Exception:
                messages.error(request, "Ви вже залишили відгук на цей товар. Ви можете залишити лише один.")
            return redirect('main:product-detail', id=product.id, slug=slug)
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
        'active_discount': active_discount,
        'base_price': base_price,
        'final_price': final_price,
        'is_on_sale': is_on_sale,
    }

    return render(request, 'main/product-detail.html', context)