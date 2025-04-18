from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Kişisel Bilgiler'), {'fields': ('first_name', 'last_name', 'email', 'user_type', 'bio', 'profile_image', 'date_of_birth', 'phone_number')}),
        (_('İzinler'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Önemli Tarihler'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'first_name', 'last_name'),
        }),
    )
    list_display = ('username', 'email', 'get_full_name_display', 'user_type_badge', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('last_login', 'date_joined')
    list_per_page = 25
    date_hierarchy = 'date_joined'
    show_full_result_count = True
    
    def get_full_name_display(self, obj):
        return obj.get_full_name() or "-"
    get_full_name_display.short_description = _('Ad Soyad')
    
    def user_type_badge(self, obj):
        badges = {
            'student': ('badge badge-info', '#17a2b8', _('Öğrenci')),
            'instructor': ('badge badge-success', '#28a745', _('Eğitmen')),
            'admin': ('badge badge-danger', '#dc3545', _('Admin')),
        }
        
        badge_class, bg_color, label = badges.get(obj.user_type, ('badge badge-secondary', '#6c757d', obj.get_user_type_display()))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px;">{}</span>',
            bg_color,
            label
        )
    user_type_badge.short_description = _('Kullanıcı Tipi')
    user_type_badge.admin_order_field = 'user_type'

admin.site.register(CustomUser, CustomUserAdmin)
