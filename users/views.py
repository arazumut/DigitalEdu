from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm

from courses.models import Course, Enrollment, Certificate
from .models import CustomUser

def user_login(request):
    """Kullanıcı giriş sayfası."""
    if request.user.is_authenticated:
        if request.user.is_student():
            return redirect('student_dashboard')
        elif request.user.is_instructor():
            return redirect('instructor_dashboard')
        else:
            return redirect('home')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Başarıyla giriş yaptınız.')
            
            # Yönlendirme
            next_page = request.GET.get('next', None)
            if next_page:
                return redirect(next_page)
                
            if user.is_student():
                return redirect('student_dashboard')
            elif user.is_instructor():
                return redirect('instructor_dashboard')
            else:
                return redirect('home')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı!')
    
    return render(request, 'users/login.html')

def user_logout(request):
    """Kullanıcı çıkış işlemi."""
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('home')

def register(request):
    """Kullanıcı kayıt sayfası."""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_type = request.POST.get('user_type', 'student')
        
        # Basit doğrulama kontrolleri
        if password1 != password2:
            messages.error(request, 'Şifreler eşleşmiyor!')
            return render(request, 'users/register.html')
            
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Bu kullanıcı adı zaten kullanımda!')
            return render(request, 'users/register.html')
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanımda!')
            return render(request, 'users/register.html')
        
        # Kullanıcı oluşturma
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name,
            user_type=user_type
        )
        
        messages.success(request, 'Hesabınız başarıyla oluşturuldu! Şimdi giriş yapabilirsiniz.')
        return redirect('login')
    
    return render(request, 'users/register.html')

@login_required
def profile(request):
    """Kullanıcı profil sayfası."""
    return render(request, 'users/profile.html')

@login_required
def edit_profile(request):
    """Kullanıcı profil düzenleme sayfası."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        phone_number = request.POST.get('phone_number')
        
        # E-posta kontrolü
        if email != request.user.email and CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanımda!')
            return redirect('edit_profile')
        
        # Profil resmi yükleme
        profile_image = request.FILES.get('profile_image')
        if profile_image:
            request.user.profile_image = profile_image
        
        # Bilgileri güncelleme
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.bio = bio
        request.user.phone_number = phone_number
        request.user.save()
        
        messages.success(request, 'Profiliniz başarıyla güncellendi.')
        return redirect('profile')
    
    return render(request, 'users/edit_profile.html')

@login_required
def change_password(request):
    """Kullanıcı şifre değiştirme sayfası."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Önemli: Oturumu korur
            messages.success(request, 'Şifreniz başarıyla değiştirildi!')
            return redirect('profile')
        else:
            messages.error(request, 'Lütfen hataları düzeltin.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def student_dashboard(request):
    """Öğrenci kontrol paneli."""
    if not request.user.is_student():
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')
    
    # Kayıtlı kurslar
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # Sertifikalar
    certificates = Certificate.objects.filter(student=request.user).select_related('course')
    
    context = {
        'enrollments': enrollments,
        'certificates': certificates,
    }
    
    return render(request, 'users/student_dashboard.html', context)

@login_required
def instructor_dashboard(request):
    """Eğitmen kontrol paneli."""
    if not request.user.is_instructor():
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('home')
    
    # Eğitmenin kursları
    courses = Course.objects.filter(instructor=request.user)
    
    # Kurs istatistikleri
    course_stats = []
    for course in courses:
        stats = {
            'course': course,
            'total_students': Enrollment.objects.filter(course=course).count(),
            'total_revenue': Enrollment.objects.filter(course=course).count() * course.price,
            'avg_rating': course.reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0,
        }
        course_stats.append(stats)
    
    context = {
        'courses': courses,
        'course_stats': course_stats,
    }
    
    return render(request, 'users/instructor_dashboard.html', context)
