from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.db.models import Count, Avg
from django.urls import reverse
from .models import (
    Category, Course, Section, Lesson, Enrollment, CourseReview,
    Quiz, Question, Answer, QuizAttempt, StudentAnswer, Certificate
)

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    show_change_link = True

class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    show_change_link = True

class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor_link', 'category_link', 'price_display', 'difficulty', 'is_published_badge', 'sections_count', 'students_count', 'average_rating', 'created_at')
    list_filter = ('category', 'difficulty', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'instructor__username', 'instructor__first_name', 'instructor__last_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'instructor', 'category', 'description')
        }),
        (_('Fiyatlandırma'), {
            'fields': ('price', 'discount_price')
        }),
        (_('Detaylar'), {
            'fields': ('thumbnail', 'difficulty', 'duration')
        }),
        (_('Durum'), {
            'fields': ('is_published',)
        }),
    )
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _sections_count=Count('sections', distinct=True),
            _students_count=Count('enrollments', distinct=True),
            _average_rating=Avg('reviews__rating')
        )
        return queryset
    
    def sections_count(self, obj):
        count = getattr(obj, '_sections_count', 0)
        return count
    sections_count.short_description = _('Bölümler')
    sections_count.admin_order_field = '_sections_count'
    
    def students_count(self, obj):
        count = getattr(obj, '_students_count', 0)
        url = reverse('admin:courses_enrollment_changelist') + f'?course__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    students_count.short_description = _('Öğrenciler')
    students_count.admin_order_field = '_students_count'
    
    def average_rating(self, obj):
        avg = getattr(obj, '_average_rating', None)
        if avg is not None:
            return format_html(
                '<span style="color: #ff9800; font-weight: bold;">{:.1f} <i class="fas fa-star"></i></span>',
                avg
            )
        return '-'
    average_rating.short_description = _('Değerlendirme')
    average_rating.admin_order_field = '_average_rating'
    
    def price_display(self, obj):
        if obj.discount_price and obj.discount_price < obj.price:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} TL</span> &nbsp; '
                '<span style="color: #28a745; font-weight: bold;">{} TL</span>',
                obj.price, obj.discount_price
            )
        return f"{obj.price} TL"
    price_display.short_description = _('Fiyat')
    price_display.admin_order_field = 'price'
    
    def is_published_badge(self, obj):
        if obj.is_published:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px;">{}</span>',
                _('Yayında')
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; font-size: 11px;">{}</span>',
            _('Taslak')
        )
    is_published_badge.short_description = _('Durum')
    is_published_badge.admin_order_field = 'is_published'
    
    def instructor_link(self, obj):
        url = reverse('admin:users_customuser_change', args=[obj.instructor.id])
        return format_html('<a href="{}">{}</a>', url, obj.instructor.get_full_name() or obj.instructor.username)
    instructor_link.short_description = _('Eğitmen')
    instructor_link.admin_order_field = 'instructor__username'
    
    def category_link(self, obj):
        url = reverse('admin:courses_category_change', args=[obj.category.id])
        return format_html('<a href="{}">{}</a>', url, obj.category.name)
    category_link.short_description = _('Kategori')
    category_link.admin_order_field = 'category__name'

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'courses_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_courses_count=Count('courses'))
        return queryset
    
    def courses_count(self, obj):
        count = getattr(obj, '_courses_count', 0)
        url = reverse('admin:courses_course_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">{}</a>', url, count)
    courses_count.short_description = _('Kurslar')
    courses_count.admin_order_field = '_courses_count'

class SectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order', 'lessons_count')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')
    inlines = [LessonInline]
    list_select_related = ('course',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_lessons_count=Count('lessons'))
        return queryset
    
    def lessons_count(self, obj):
        count = getattr(obj, '_lessons_count', 0)
        return count
    lessons_count.short_description = _('Dersler')
    lessons_count.admin_order_field = '_lessons_count'

class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_completed', 'progress_percentage')
    list_filter = ('is_completed', 'enrolled_at')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'course__title')
    list_select_related = ('student', 'course')
    date_hierarchy = 'enrolled_at'
    
    def progress_percentage(self, obj):
        if obj.progress > 0:
            return format_html(
                '<div style="background: #eee; width: 100px; height: 20px; border-radius: 10px; overflow: hidden;">'
                '<div style="background: #4caf50; width: {}%; height: 100%;"></div>'
                '</div> {}%',
                obj.progress, obj.progress
            )
        return '0%'
    progress_percentage.short_description = _('İlerleme')

class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating_stars', 'comment_preview', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('course__title', 'student__username', 'student__first_name', 'student__last_name', 'comment')
    readonly_fields = ('created_at',)
    
    def rating_stars(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: #ff9800; letter-spacing: 3px;">{}</span>', stars)
    rating_stars.short_description = _('Değerlendirme')
    rating_stars.admin_order_field = 'rating'
    
    def comment_preview(self, obj):
        if obj.comment:
            preview = obj.comment[:50] + ('...' if len(obj.comment) > 50 else '')
            return preview
        return '-'
    comment_preview.short_description = _('Yorum')

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    max_num = 6

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'quiz', 'question_type', 'points', 'order')
    list_filter = ('quiz', 'question_type')
    search_fields = ('question_text',)
    inlines = [AnswerInline]

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'section', 'is_final', 'pass_score', 'time_limit')
    list_filter = ('course', 'is_final')
    search_fields = ('title', 'description', 'course__title')
    inlines = [QuestionInline]

class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    readonly_fields = ('question', 'selected_answer', 'text_answer', 'is_correct')
    can_delete = False

class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'is_passed', 'time_spent', 'started_at')
    list_filter = ('status', 'started_at')
    search_fields = ('student__username', 'quiz__title')
    readonly_fields = ('score', 'status', 'started_at', 'completed_at')
    
    def time_spent(self, obj):
        if obj.completed_at and obj.started_at:
            seconds = (obj.completed_at - obj.started_at).total_seconds()
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}m {seconds}s"
        return "-"
    time_spent.short_description = _('Harcanan Süre')
    
    def is_passed(self, obj):
        return obj.is_passed()
    is_passed.boolean = True
    is_passed.short_description = _('Geçti mi?')

class CertificateAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'certificate_number', 'issue_date')
    list_filter = ('issue_date', 'course')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'course__title', 'certificate_number')
    readonly_fields = ('certificate_number', 'issue_date')
    date_hierarchy = 'issue_date'

admin.site.register(Category, CategoryAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Lesson)
admin.site.register(Enrollment, EnrollmentAdmin)
admin.site.register(CourseReview, CourseReviewAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(QuizAttempt, QuizAttemptAdmin)
admin.site.register(Certificate, CertificateAdmin)
