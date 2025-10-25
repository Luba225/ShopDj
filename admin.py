from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product

def image_tag_html(obj):
    if obj.image:
        return format_html(
            '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />'.format(obj.image.url)
        )
    return "Немає зображення"
image_tag_html.short_description = 'Мініатюра'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug", "is_active", image_tag_html)
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name", )}
    list_editable = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "category", "price", "is_available", 
        "featured", "views", "created_at", image_tag_html
    )
    list_filter = ("category", "is_available", "featured", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "is_available", "featured")
    ordering = ("-created_at",)