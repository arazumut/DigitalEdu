from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from courses.models import Course

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_('Kullanıcı')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    
    class Meta:
        verbose_name = _('Sepet')
        verbose_name_plural = _('Sepetler')
        
    def __str__(self):
        return f"{self.user.username}'in Sepeti"
    
    def get_total_price(self):
        return sum(item.course.effective_price() for item in self.items.all())
    
    def get_item_count(self):
        return self.items.count()

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Sepet')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Kurs')
    )
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Eklenme Tarihi'))
    
    class Meta:
        verbose_name = _('Sepet Öğesi')
        verbose_name_plural = _('Sepet Öğeleri')
        unique_together = ['cart', 'course']
        
    def __str__(self):
        return f"{self.course.title}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Beklemede')),
        ('completed', _('Tamamlandı')),
        ('failed', _('Başarısız')),
        ('refunded', _('İade Edildi')),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', _('Kredi Kartı')),
        ('bank_transfer', _('Banka Transferi')),
        ('other', _('Diğer')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('Kullanıcı')
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Tutar')
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='credit_card',
        verbose_name=_('Ödeme Yöntemi')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Durum')
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('İşlem ID')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncelleme Tarihi'))
    
    class Meta:
        verbose_name = _('Ödeme')
        verbose_name_plural = _('Ödemeler')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.amount} TL - {self.get_status_display()}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Beklemede')),
        ('processing', _('İşleniyor')),
        ('completed', _('Tamamlandı')),
        ('cancelled', _('İptal Edildi')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Kullanıcı')
    )
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order',
        verbose_name=_('Ödeme')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Durum')
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Toplam Tutar')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncelleme Tarihi'))
    
    class Meta:
        verbose_name = _('Sipariş')
        verbose_name_plural = _('Siparişler')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Sipariş')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_('Kurs')
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_('Fiyat')
    )
    
    class Meta:
        verbose_name = _('Sipariş Öğesi')
        verbose_name_plural = _('Sipariş Öğeleri')
        
    def __str__(self):
        return f"{self.order.id} - {self.course.title}"
