from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Review
from .forms import ReviewForm
from main.models import Product

class ReviewView(LoginRequiredMixin, View):
    login_url = 'accounts:login'
    redirect_field_name = 'next'

    def get(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        form = ReviewForm()
        return render(request, 'reviews/add_review.html', {'product': product, 'form': form})

    def post(self, request, product_pk):
        product = get_object_or_404(Product, pk=product_pk)
        if Review.objects.filter(product=product, author=request.user).exists():
            messages.error(request, "Ви вже залишали відгук для цього товару 💗")
            return redirect('main:product-detail', id=product.id, slug=product.slug)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            review.product = product
            review.save()
            messages.success(request, '✅ Ваш відгук успішно додано та очікує на модерацію.')
            return redirect('main:product-detail', id=product.id, slug=product.slug)
        return render(request, 'reviews/add_review.html', {'product': product, 'form': form})
