from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('payment-start/<int:order_id>/', views.payment_start, name='payment_start'),
    path('payment-complete/', views.payment_complete, name='payment_complete'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
]