from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count, Avg
from courses.models import Course, CourseReview, Enrollment, Category, Certificate
from users.models import CustomUser
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

def home(request):
    """Ana sayfa görünümü"""
    popular_courses = Course.objects.filter(is_published=True).annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')[:3]
    student_reviews = CourseReview.objects.select_related('student', 'course').order_by('-created_at')[:3]
    
    # İstatistikler
    student_count = CustomUser.objects.filter(user_type='student').count()
    instructor_count = CustomUser.objects.filter(user_type='instructor').count()
    course_count = Course.objects.filter(is_published=True).count()
    
    context = {
        'popular_courses': popular_courses,
        'student_reviews': student_reviews,
        'student_count': student_count,
        'instructor_count': instructor_count,
        'course_count': course_count,
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """Hakkımızda sayfası görünümü"""
    return render(request, 'core/about.html')

def contact(request):
    """İletişim sayfası görünümü"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        email_message = f"İsim: {name}\nE-posta: {email}\nMesaj: {message}"
        
        try:
            send_mail(
                subject=subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.')
            return redirect('contact')
        except Exception as e:
            messages.error(request, f'Mesajınız gönderilemedi. Hata: {str(e)}')
    
    return render(request, 'core/contact.html')

def subscribe(request):
    """E-bülten aboneliği işleme"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if email:
            # Burada e-posta aboneliği için veritabanına kayıt veya e-posta servisi entegrasyonu yapılabilir
            # Bu örnek için basit bir mesaj gösteriyoruz
            messages.success(request, 'E-bülten aboneliğiniz başarıyla kaydedildi!')
        else:
            messages.error(request, 'Lütfen geçerli bir e-posta adresi girin.')
    
    return redirect('home')

@staff_member_required
def admin_dashboard(request):
    """
    Django admin panelindeki özel gösterge panosu için istatistikleri sağlar.
    Bu görünüm, templates/admin/index.html şablonunu doldurmak için kullanılır.
    """
    context = {
        'custom_user_count': CustomUser.objects.count(),
        'course_count': Course.objects.count(),
        'enrollment_count': Enrollment.objects.count(),
        'category_count': Category.objects.count(),
        'certificate_count': Certificate.objects.count(),
        'student_count': CustomUser.objects.filter(user_type='student').count(),
        'instructor_count': CustomUser.objects.filter(user_type='instructor').count(),
        'title': 'EduPlus Admin Paneli',
    }
    
    # Son eklenen kurslar
    context['recent_courses'] = Course.objects.order_by('-created_at')[:5]
    
    # Popüler kurslar (en çok kayıt olan)
    context['popular_courses'] = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # Son eklenen kullanıcılar
    context['recent_users'] = CustomUser.objects.order_by('-date_joined')[:5]
    
    return context

@staff_member_required
def admin_index(request):
    """Admin paneli dashboard sayfası için context veri hazırlama."""
    
    # Kurs istatistikleri
    total_courses = Course.objects.count()
    published_courses = Course.objects.filter(is_published=True).count()
    draft_courses = total_courses - published_courses
    
    # Kullanıcı istatistikleri
    students_count = CustomUser.objects.filter(user_type='student').count()
    instructors_count = CustomUser.objects.filter(user_type='instructor').count()
    admin_count = CustomUser.objects.filter(user_type='admin').count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = CustomUser.objects.filter(is_active=False).count()
    
    # Kayıt istatistikleri
    enrollments_count = Enrollment.objects.count()
    completed_courses = Enrollment.objects.filter(is_completed=True).count()
    
    # Son eklenen veriler
    recent_courses = Course.objects.select_related('instructor', 'category').order_by('-created_at')[:5]
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-date_enrolled')[:5]
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_reviews = CourseReview.objects.select_related('student', 'course').order_by('-created_at')[:5]
    
    # Popüler kurslar
    popular_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # En çok değerlendirilen kurslar
    top_rated_courses = Course.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(review_count__gt=0).order_by('-avg_rating')[:5]
    
    context = {
        'current_date': timezone.now().date(),
        'students_count': students_count,
        'instructors_count': instructors_count,
        'admin_count': admin_count,
        'courses_count': total_courses,
        'published_courses': published_courses,
        'draft_courses': draft_courses,
        'enrollments_count': enrollments_count,
        'completed_courses': completed_courses,
        'active_users': active_users,
        'inactive_users': inactive_users,
        
        'recent_courses': recent_courses,
        'recent_enrollments': recent_enrollments,
        'recent_users': recent_users,
        'recent_reviews': recent_reviews,
        'popular_courses': popular_courses,
        'top_rated_courses': top_rated_courses,
        
        # Admin için app_list
        'app_list': [
            {
                'name': _('Kurslar'),
                'app_label': 'courses',
                'models': [
                    {
                        'name': _('Kurslar'),
                        'admin_url': reverse('admin:courses_course_changelist'),
                        'add_url': reverse('admin:courses_course_add'),
                    },
                    {
                        'name': _('Kategoriler'),
                        'admin_url': reverse('admin:courses_category_changelist'),
                        'add_url': reverse('admin:courses_category_add'),
                    },
                    {
                        'name': _('Kayıtlar'),
                        'admin_url': reverse('admin:courses_enrollment_changelist'),
                        'add_url': reverse('admin:courses_enrollment_add'),
                    },
                ],
            },
            {
                'name': _('Kullanıcılar'),
                'app_label': 'users',
                'models': [
                    {
                        'name': _('Tüm Kullanıcılar'),
                        'admin_url': reverse('admin:users_customuser_changelist'),
                        'add_url': reverse('admin:users_customuser_add'),
                    },
                ],
            },
            {
                'name': _('Ödemeler'),
                'app_label': 'payments',
                'models': [
                    {
                        'name': _('Siparişler'),
                        'admin_url': reverse('admin:payments_order_changelist'),
                        'add_url': reverse('admin:payments_order_add'),
                    },
                    {
                        'name': _('Ödemeler'),
                        'admin_url': reverse('admin:payments_payment_changelist'),
                        'add_url': reverse('admin:payments_payment_add'),
                    },
                ],
            },
        ],
    }
    
    return render(request, 'admin/index.html', context)
