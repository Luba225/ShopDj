from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профіль'
    
    # Виводимо аватар
    fields = ('avatar', 'avatar_preview')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return mark_safe(f'<img src="{obj.avatar.url}" style="max-height: 100px; border-radius: 5px;" />')
        return "Немає зображення"
    avatar_preview.short_description = "Мініатюра"


class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'profile_avatar_thumbnail'
    )
    
    def profile_avatar_thumbnail(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return mark_safe(f'<img src="{obj.profile.avatar.url}" width="30" height="30" style="border-radius: 50%; object-fit: cover;" />')
        return "-"
    
    profile_avatar_thumbnail.short_description = "Аватар"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)