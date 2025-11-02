from django.contrib import admin
from django.http import HttpResponse
from .models import Order, OrderItem
import csv
import datetime

def export_to_csv(modeladmin, request, queryset):
    """Експортує вибрані замовлення у формат CSV."""
    opts = modeladmin.model._meta
    
    field_names = [field.name for field in opts.fields]
    if 'user' in field_names: field_names.remove('user') 
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=orders_{datetime.date.today()}.csv'
    
    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response

export_to_csv.short_description = 'Експортувати вибрані замовлення у CSV'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product', 'price', 'quantity', 'get_cost'] 
    readonly_fields = ['price', 'get_cost']
    extra = 0

    def get_cost(self, obj):
        return f'{obj.get_cost()} грн'
    get_cost.short_description = 'Вартість'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'first_name', 
        'last_name', 
        'email', 
        'city', 
        'paid', 
        'created', 
        'get_total_cost_display'
    ]
    list_filter = ['paid', 'created', 'updated']
    list_editable = ['paid'] 
    
    fieldsets = [
        ('Інформація про клієнта', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Адреса доставки', {
            'fields': ('city', 'address')
        }),
        ('Статус', {
            'fields': ('paid',)
        }),
    ]
    
    actions = [export_to_csv]
    inlines = [OrderItemInline]
    
    def get_total_cost_display(self, obj):
        return f'{obj.get_total_cost()} грн'
    
    get_total_cost_display.short_description = 'Загальна вартість'