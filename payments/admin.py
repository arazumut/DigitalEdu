from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from .models import Cart, CartItem, Payment, Order, OrderItem

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    raw_id_fields = ('course',)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    raw_id_fields = ('course',)
    readonly_fields = ('price',)

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_item_count', 'get_total_price')
    inlines = [CartItemInline]
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = _('Ürün Sayısı')
    
    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            if hasattr(item.course, 'effective_price'):
                total += item.course.effective_price()
            else:
                total += item.course.price or 0
        return format_html('<span style="font-weight: bold;">{} TL</span>', total)
    get_total_price.short_description = _('Toplam Tutar')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'status_badge', 'total_amount_display', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    readonly_fields = ('total_amount',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    list_select_related = ('user',)
    fieldsets = (
        (None, {
            'fields': ('user', 'status', 'notes')
        }),
        (_('Ödeme Bilgileri'), {
            'fields': ('total_amount',)
        }),
    )
    
    def total_amount_display(self, obj):
        return format_html('<span style="font-weight: bold; color: #28a745;">{} TL</span>', obj.total_amount)
    total_amount_display.short_description = _('Toplam Tutar')
    total_amount_display.admin_order_field = 'total_amount'
    
    def user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = _('Kullanıcı')
    user_link.admin_order_field = 'user__username'
    
    def status_badge(self, obj):
        badges = {
            'pending': ('badge badge-warning', '#ffc107', _('Beklemede')),
            'processing': ('badge badge-info', '#17a2b8', _('İşleniyor')),
            'completed': ('badge badge-success', '#28a745', _('Tamamlandı')),
            'cancelled': ('badge badge-danger', '#dc3545', _('İptal Edildi')),
            'refunded': ('badge badge-secondary', '#6c757d', _('İade Edildi')),
        }
        
        badge_class, bg_color, label = badges.get(obj.status, ('badge badge-secondary', '#6c757d', obj.get_status_display()))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px;">{}</span>',
            bg_color,
            label
        )
    status_badge.short_description = _('Durum')
    status_badge.admin_order_field = 'status'

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user_link', 'order_link', 'amount_display', 'payment_method', 'status_badge', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'transaction_id')
    readonly_fields = ('transaction_id', 'created_at')
    date_hierarchy = 'created_at'
    list_select_related = ('user', 'order')
    fieldsets = (
        (None, {
            'fields': ('user', 'order', 'amount', 'payment_method', 'status')
        }),
        (_('İşlem Bilgileri'), {
            'fields': ('transaction_id', 'created_at')
        }),
    )
    
    def amount_display(self, obj):
        return format_html('<span style="font-weight: bold; color: #28a745;">{} TL</span>', obj.amount)
    amount_display.short_description = _('Tutar')
    amount_display.admin_order_field = 'amount'
    
    def user_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = _('Kullanıcı')
    user_link.admin_order_field = 'user__username'
    
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:payments_order_change', args=[obj.order.id])
            return format_html('<a href="{}">#Order-{}</a>', url, obj.order.id)
        return '-'
    order_link.short_description = _('Sipariş')
    order_link.admin_order_field = 'order'
    
    def status_badge(self, obj):
        badges = {
            'pending': ('badge badge-warning', '#ffc107', _('Beklemede')),
            'processing': ('badge badge-info', '#17a2b8', _('İşleniyor')),
            'completed': ('badge badge-success', '#28a745', _('Tamamlandı')),
            'failed': ('badge badge-danger', '#dc3545', _('Başarısız')),
            'refunded': ('badge badge-secondary', '#6c757d', _('İade Edildi')),
        }
        
        badge_class, bg_color, label = badges.get(obj.status, ('badge badge-secondary', '#6c757d', obj.get_status_display()))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px;">{}</span>',
            bg_color,
            label
        )
    status_badge.short_description = _('Durum')
    status_badge.admin_order_field = 'status'

admin.site.register(Cart, CartAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
