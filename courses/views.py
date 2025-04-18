from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.db.models import Avg, Count, Q

from .models import (
    Course, Category, Section, Lesson, Enrollment,
    CourseReview, Quiz, Question, Answer, QuizAttempt,
    StudentAnswer, Certificate
)
from users.models import CustomUser

def course_list(request):
    """Tüm kursların listelendiği sayfayı gösterir."""
    category_slug = request.GET.get('category', None)
    difficulty = request.GET.get('difficulty', None)
    search_query = request.GET.get('q', None)
    sort_by = request.GET.get('sort', '-created_at')  # Varsayılan sıralama: en yeni
    
    courses = Course.objects.filter(is_published=True)
    
    # Filtreleme
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    if difficulty:
        courses = courses.filter(difficulty=difficulty)
    
    if search_query:
        courses = courses.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Sıralama
    if sort_by == 'price':
        courses = courses.order_by('price')
    elif sort_by == '-price':
        courses = courses.order_by('-price')
    elif sort_by == 'title':
        courses = courses.order_by('title')
    elif sort_by == 'popularity':
        courses = courses.annotate(enrollment_count=Count('enrollments')).order_by('-enrollment_count')
    else:  # '-created_at'
        courses = courses.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(courses, 9)  # Her sayfada 9 kurs
    page_number = request.GET.get('page', 1)
    courses = paginator.get_page(page_number)
    
    # Kategoriler sidebar için
    categories = Category.objects.all()
    
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': category_slug,
        'selected_difficulty': difficulty,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    
    return render(request, 'courses/course_list.html', context)

def course_detail(request, slug):
    """Kurs detay sayfasını gösterir."""
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Kurs içeriği: bölümler ve dersler
    sections = Section.objects.filter(course=course).order_by('order')
    
    # Eğitmen bilgisi
    instructor = course.instructor
    
    # İlgili kurslar
    related_courses = Course.objects.filter(
        category=course.category, 
        is_published=True
    ).exclude(id=course.id)[:3]
    
    # Kurs değerlendirmeleri
    reviews = CourseReview.objects.filter(course=course).select_related('student')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # Kullanıcı bu kursa kayıtlı mı?
    is_enrolled = False
    user_review = None
    
    if request.user.is_authenticated:
        is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
        user_review = CourseReview.objects.filter(student=request.user, course=course).first()
    
    context = {
        'course': course,
        'sections': sections,
        'instructor': instructor,
        'related_courses': related_courses,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'is_enrolled': is_enrolled,
        'user_review': user_review,
    }
    
    return render(request, 'courses/course_detail.html', context)

def course_category(request, slug):
    """Belirli bir kategori içindeki kursları listeler."""
    category = get_object_or_404(Category, slug=slug)
    return redirect(f"{'/courses/?category=' + slug}")

def instructor_courses(request, username):
    """Belirli bir eğitmenin kurslarını listeler."""
    instructor = get_object_or_404(CustomUser, username=username, user_type='instructor')
    courses = Course.objects.filter(instructor=instructor, is_published=True)
    
    context = {
        'instructor': instructor,
        'courses': courses,
    }
    
    return render(request, 'courses/instructor_courses.html', context)

@login_required
def course_create(request):
    """Eğitmenin yeni kurs oluşturabildiği sayfa."""
    if not request.user.is_instructor():
        messages.error(request, "Bu sayfaya erişim yetkiniz yok.")
        return redirect('home')
    
    # Form işleme ve kurs oluşturma mantığı burada olacak
    # Bu örnek için detaylandırılmayacak
    
    context = {
        'categories': Category.objects.all(),
    }
    
    return render(request, 'courses/course_form.html', context)

@login_required
def course_edit(request, slug):
    """Eğitmenin kursunu düzenleyebildiği sayfa."""
    course = get_object_or_404(Course, slug=slug)
    
    # Sadece kursun eğitmeni düzenleyebilir
    if request.user != course.instructor:
        messages.error(request, "Bu kursu düzenleme yetkiniz yok.")
        return redirect('course_detail', slug=slug)
    
    # Form işleme ve kurs düzenleme mantığı burada olacak
    # Bu örnek için detaylandırılmayacak
    
    context = {
        'course': course,
        'categories': Category.objects.all(),
    }
    
    return render(request, 'courses/course_form.html', context)

@login_required
def course_enroll(request, slug):
    """Öğrencinin kursa kaydolması."""
    if not request.user.is_student():
        messages.error(request, "Sadece öğrenciler kursa kaydolabilir.")
        return redirect('course_detail', slug=slug)
        
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Kullanıcı zaten kursa kayıtlı mı?
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "Zaten bu kursa kayıtlısınız.")
        return redirect('course_detail', slug=slug)
    
    # Kayıt oluştur
    Enrollment.objects.create(
        student=request.user,
        course=course,
    )
    
    messages.success(request, f"{course.title} kursuna başarıyla kaydoldunuz!")
    return redirect('course_detail', slug=slug)

@login_required
def add_review(request, slug):
    """Öğrencinin kurs için değerlendirme eklemesi."""
    if not request.user.is_student():
        messages.error(request, "Sadece öğrenciler değerlendirme yazabilir.")
        return redirect('course_detail', slug=slug)
        
    course = get_object_or_404(Course, slug=slug, is_published=True)
    
    # Öğrenci bu kursa kayıtlı mı?
    if not Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.error(request, "Sadece kursa kayıtlı öğrenciler değerlendirme yazabilir.")
        return redirect('course_detail', slug=slug)
    
    # Öğrenci zaten değerlendirme yazmış mı?
    if CourseReview.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "Zaten bu kurs için bir değerlendirme yazmışsınız. Düzenlemek istiyorsanız değerlendirmenizi güncelleyin.")
        return redirect('course_detail', slug=slug)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if not rating or not comment:
            messages.error(request, "Lütfen bir puan ve yorum ekleyin.")
            return redirect('course_detail', slug=slug)
        
        # Değerlendirme oluştur
        CourseReview.objects.create(
            student=request.user,
            course=course,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, "Değerlendirmeniz başarıyla kaydedildi. Teşekkürler!")
        return redirect('course_detail', slug=slug)
    
    return redirect('course_detail', slug=slug)

# Diğer görünümler kullanılmadığı için kısa tutulmuştur
# Projenin ilerleyen aşamalarında eklenebilir

@login_required
def edit_review(request, slug, review_id):
    """Öğrencinin kurs değerlendirmesini düzenlemesi."""
    return render(request, 'courses/review_form.html')

@login_required
def delete_review(request, slug, review_id):
    """Öğrencinin kurs değerlendirmesini silmesi."""
    return redirect('course_detail', slug=slug)

@login_required
def section_create(request, course_slug):
    """Eğitmenin kursa yeni bölüm eklemesi."""
    return render(request, 'courses/section_form.html')

@login_required
def section_edit(request, course_slug, section_id):
    """Eğitmenin kurs bölümünü düzenlemesi."""
    return render(request, 'courses/section_form.html')

@login_required
def section_delete(request, course_slug, section_id):
    """Eğitmenin kurs bölümünü silmesi."""
    return redirect('course_detail', slug=course_slug)

@login_required
def lesson_create(request, course_slug, section_id):
    """Eğitmenin bölüme ders eklemesi."""
    return render(request, 'courses/lesson_form.html')

@login_required
def lesson_edit(request, course_slug, section_id, lesson_id):
    """Eğitmenin dersi düzenlemesi."""
    return render(request, 'courses/lesson_form.html')

@login_required
def lesson_delete(request, course_slug, section_id, lesson_id):
    """Eğitmenin dersi silmesi."""
    return redirect('course_detail', slug=course_slug)

@login_required
def quiz_create(request, course_slug):
    """Eğitmenin kursa sınav eklemesi."""
    return render(request, 'courses/quiz_form.html')

@login_required
def quiz_detail(request, course_slug, quiz_id):
    """Sınav detay sayfası."""
    return render(request, 'courses/quiz_detail.html')

@login_required
def quiz_edit(request, course_slug, quiz_id):
    """Eğitmenin sınavı düzenlemesi."""
    return render(request, 'courses/quiz_form.html')

@login_required
def quiz_delete(request, course_slug, quiz_id):
    """Eğitmenin sınavı silmesi."""
    return redirect('course_detail', slug=course_slug)

@login_required
def take_quiz(request, course_slug, quiz_id):
    """Öğrencinin sınavı çözmesi."""
    return render(request, 'courses/take_quiz.html')

@login_required
def quiz_results(request, course_slug, quiz_id):
    """Sınav sonuçları."""
    return render(request, 'courses/quiz_results.html')

@login_required
def generate_certificate(request, course_slug):
    """Kurs sertifikası oluşturma."""
    # Bu fonksiyon, öğrenci kursu tamamladığında ve yeterli başarıyı gösterdiğinde sertifika oluşturur
    # PDF oluşturma mantığı burada olacak
    return HttpResponse('Sertifika oluşturuldu')
