from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction

from courses.models import Course, Enrollment
from .models import Cart, CartItem, Payment, Order, OrderItem

import stripe
from decimal import Decimal

# Stripe kurulumu
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def cart(request):
    """Kullanıcının sepet içeriğini gösterir."""
    # Kullanıcının sepetini al veya oluştur
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Sepet öğelerini al
    cart_items = CartItem.objects.filter(cart=cart).select_related('course')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': cart.get_total_price()
    }
    
    return render(request, 'payments/cart.html', context)

@login_required
def add_to_cart(request, course_id):
    """Kursu sepete ekler."""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    
    # Kullanıcı zaten kursa kayıtlı mı?
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, 'Zaten bu kursa kayıtlısınız.')
        return redirect('course_detail', slug=course.slug)
    
    # Kullanıcının sepetini al veya oluştur
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Kurs zaten sepette mi?
    if CartItem.objects.filter(cart=cart, course=course).exists():
        messages.info(request, 'Bu kurs zaten sepetinizde.')
    else:
        # Kursu sepete ekle
        CartItem.objects.create(cart=cart, course=course)
        messages.success(request, f"'{course.title}' kursu sepetinize eklendi.")
    
    # Ana sayfadan mı geldi?
    if 'HTTP_REFERER' in request.META and 'home' in request.META['HTTP_REFERER']:
        return redirect('home')
    
    # Kurs detayından mı geldi?
    if 'HTTP_REFERER' in request.META and course.slug in request.META['HTTP_REFERER']:
        return redirect('course_detail', slug=course.slug)
    
    # Varsayılan yönlendirme
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Kursu sepetten çıkarır."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    course_title = cart_item.course.title
    cart_item.delete()
    
    messages.success(request, f"'{course_title}' kursu sepetinizden çıkarıldı.")
    return redirect('cart')

@login_required
def checkout(request):
    """Ödeme sayfasını gösterir."""
    # Kullanıcının sepetini al
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('course')
        
        if not cart_items.exists():
            messages.error(request, 'Sepetiniz boş. Lütfen önce kurs ekleyin.')
            return redirect('course_list')
        
        total_price = cart.get_total_price()
        
        if request.method == 'POST':
            # Ödeme işlemi - örnek olarak dummy payment
            # Gerçek projede Stripe veya başka bir ödeme yöntemi kullanılır
            try:
                with transaction.atomic():
                    # Ödeme oluştur
                    payment = Payment.objects.create(
                        user=request.user,
                        amount=total_price,
                        payment_method='credit_card',
                        status='completed',
                        transaction_id=f"DUMMY-{cart.id}-{request.user.id}"
                    )
                    
                    # Sipariş oluştur
                    order = Order.objects.create(
                        user=request.user,
                        payment=payment,
                        status='completed',
                        total_amount=total_price
                    )
                    
                    # Sipariş öğeleri oluştur ve kurslara kayıt ol
                    for item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            course=item.course,
                            price=item.course.effective_price()
                        )
                        
                        # Kullanıcıyı kursa kaydet
                        Enrollment.objects.create(
                            student=request.user,
                            course=item.course
                        )
                    
                    # Sepeti temizle
                    cart_items.delete()
                    
                    messages.success(request, 'Ödeme başarıyla tamamlandı. Kurslarınıza kaydınız yapıldı!')
                    return redirect('payment_success')
            
            except Exception as e:
                messages.error(request, f'Ödeme işlemi sırasında bir hata oluştu: {str(e)}')
                return redirect('payment_fail')
        
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY
        }
        
        return render(request, 'payments/checkout.html', context)
    
    except Cart.DoesNotExist:
        messages.error(request, 'Sepetiniz bulunamadı.')
        return redirect('course_list')

@login_required
def payment_success(request):
    """Başarılı ödeme sayfası."""
    return render(request, 'payments/payment_success.html')

@login_required
def payment_fail(request):
    """Başarısız ödeme sayfası."""
    return render(request, 'payments/payment_fail.html')

@login_required
def order_history(request):
    """Kullanıcının sipariş geçmişini gösterir."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders
    }
    
    return render(request, 'payments/order_history.html', context)

@login_required
def order_detail(request, order_id):
    """Sipariş detaylarını gösterir."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order).select_related('course')
    
    context = {
        'order': order,
        'order_items': order_items
    }
    
    return render(request, 'payments/order_detail.html', context)
