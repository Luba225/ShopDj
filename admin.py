from django.contrib import admin
from .models import Discount, PromoCode, PromoCodeUsage

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('product', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'min_quantity')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('product__name',)
    ordering = ('-created_at',)

class PromoCodeUsageInline(admin.TabularInline):
    model = PromoCodeUsage
    extra = 0
    readonly_fields = ('user', 'order_amount', 'discount_amount', 'used_at')
    can_delete = False

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'start_date', 'end_date', 'is_active', 'usage_limit', 'used_count')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('code',)
    readonly_fields = ('used_count', 'created_at', 'created_by')
    inlines = [PromoCodeUsageInline]


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promo_code', 'user', 'order_amount', 'discount_amount', 'used_at')
    list_filter = ('used_at', 'promo_code')
    search_fields = ('promo_code__code', 'user__username')
    ordering = ('-used_at',)
