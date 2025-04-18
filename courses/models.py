from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Kategori Adı'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    
    class Meta:
        verbose_name = _('Kategori')
        verbose_name_plural = _('Kategoriler')
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Course(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', _('Başlangıç')),
        ('intermediate', _('Orta')),
        ('advanced', _('İleri')),
    )
    
    title = models.CharField(max_length=200, verbose_name=_('Kurs Başlığı'))
    slug = models.SlugField(unique=True, verbose_name=_('Slug'))
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='courses',
        limit_choices_to={'user_type': 'instructor'},
        verbose_name=_('Eğitmen')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        verbose_name=_('Kategori')
    )
    description = models.TextField(verbose_name=_('Açıklama'))
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_('Fiyat')
    )
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_('İndirimli Fiyat')
    )
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/',
        verbose_name=_('Kapak Resmi')
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner',
        verbose_name=_('Zorluk Seviyesi')
    )
    duration = models.PositiveIntegerField(
        help_text=_('Toplam saat cinsinden süre'),
        verbose_name=_('Süre')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Güncellenme Tarihi'))
    is_published = models.BooleanField(default=False, verbose_name=_('Yayında mı?'))
    
    class Meta:
        verbose_name = _('Kurs')
        verbose_name_plural = _('Kurslar')
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('course_detail', kwargs={'slug': self.slug})
        
    def __str__(self):
        return self.title
        
    def effective_price(self):
        return self.discount_price if self.discount_price else self.price
        
class Section(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_('Kurs')
    )
    title = models.CharField(max_length=200, verbose_name=_('Bölüm Başlığı'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Sıra'))
    
    class Meta:
        verbose_name = _('Bölüm')
        verbose_name_plural = _('Bölümler')
        ordering = ['order']
        
    def __str__(self):
        return f"{self.course.title} - {self.title}"
        
class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('video', _('Video')),
        ('text', _('Metin')),
        ('quiz', _('Quiz')),
    )
    
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name=_('Bölüm')
    )
    title = models.CharField(max_length=200, verbose_name=_('Ders Başlığı'))
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='video',
        verbose_name=_('İçerik Tipi')
    )
    video_url = models.URLField(blank=True, verbose_name=_('Video URL'))
    content = models.TextField(blank=True, verbose_name=_('İçerik'))
    duration = models.PositiveIntegerField(
        default=0,
        help_text=_('Dakika cinsinden süre'),
        verbose_name=_('Süre')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Sıra'))
    is_free = models.BooleanField(default=False, verbose_name=_('Ücretsiz mi?'))
    
    class Meta:
        verbose_name = _('Ders')
        verbose_name_plural = _('Dersler')
        ordering = ['order']
        
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'user_type': 'student'},
        verbose_name=_('Öğrenci')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Kurs')
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Kayıt Tarihi'))
    is_completed = models.BooleanField(default=False, verbose_name=_('Tamamlandı mı?'))
    progress = models.PositiveIntegerField(default=0, verbose_name=_('İlerleme'))
    
    class Meta:
        verbose_name = _('Kayıt')
        verbose_name_plural = _('Kayıtlar')
        unique_together = ['student', 'course']
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

class CourseReview(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Kurs')
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Öğrenci')
    )
    rating = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        verbose_name=_('Değerlendirme')
    )
    comment = models.TextField(verbose_name=_('Yorum'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Oluşturulma Tarihi'))
    
    class Meta:
        verbose_name = _('Kurs Değerlendirmesi')
        verbose_name_plural = _('Kurs Değerlendirmeleri')
        unique_together = ['course', 'student']
        
    def __str__(self):
        return f"{self.course.title} - {self.student.username} - {self.rating}"

class Quiz(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name=_('Kurs')
    )
    title = models.CharField(max_length=200, verbose_name=_('Başlık'))
    description = models.TextField(blank=True, verbose_name=_('Açıklama'))
    pass_score = models.PositiveSmallIntegerField(
        default=70,
        help_text=_('Sınavı geçmek için gerekli minimum puan (%)'),
        verbose_name=_('Geçme Puanı')
    )
    time_limit = models.PositiveIntegerField(
        default=30,
        help_text=_('Dakika cinsinden sınav süresi'),
        verbose_name=_('Süre Limiti')
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quizzes',
        verbose_name=_('Bölüm')
    )
    is_final = models.BooleanField(
        default=False, 
        verbose_name=_('Final Sınavı mı?')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Sınav')
        verbose_name_plural = _('Sınavlar')
    
    def __str__(self):
        return self.title

class Question(models.Model):
    QUESTION_TYPE_CHOICES = (
        ('multiple_choice', _('Çoktan Seçmeli')),
        ('true_false', _('Doğru/Yanlış')),
        ('short_answer', _('Kısa Cevap')),
    )
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Sınav')
    )
    question_text = models.TextField(verbose_name=_('Soru Metni'))
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='multiple_choice',
        verbose_name=_('Soru Tipi')
    )
    points = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_('Puan')
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_('Sıra'))
    
    class Meta:
        verbose_name = _('Soru')
        verbose_name_plural = _('Sorular')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.question_text[:50]}..."

class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name=_('Soru')
    )
    answer_text = models.CharField(max_length=255, verbose_name=_('Cevap Metni'))
    is_correct = models.BooleanField(default=False, verbose_name=_('Doğru mu?'))
    
    class Meta:
        verbose_name = _('Cevap')
        verbose_name_plural = _('Cevaplar')
    
    def __str__(self):
        return self.answer_text

class QuizAttempt(models.Model):
    STATUS_CHOICES = (
        ('in_progress', _('Devam Ediyor')),
        ('completed', _('Tamamlandı')),
        ('timed_out', _('Süre Aşımı')),
    )
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name=_('Öğrenci')
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name=_('Sınav')
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Puan')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name=_('Durum')
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Başlangıç Zamanı'))
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Tamamlanma Zamanı')
    )
    
    class Meta:
        verbose_name = _('Sınav Denemesi')
        verbose_name_plural = _('Sınav Denemeleri')
        unique_together = ['student', 'quiz']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"
    
    def is_passed(self):
        if self.score is None:
            return False
        return self.score >= self.quiz.pass_score

class StudentAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='student_answers',
        verbose_name=_('Deneme')
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name=_('Soru')
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_('Seçilen Cevap')
    )
    text_answer = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Metin Cevabı')
    )
    is_correct = models.BooleanField(default=False, verbose_name=_('Doğru mu?'))
    
    class Meta:
        verbose_name = _('Öğrenci Cevabı')
        verbose_name_plural = _('Öğrenci Cevapları')
        unique_together = ['attempt', 'question']
    
    def __str__(self):
        return f"{self.attempt.student.username} - {self.question}"

class Certificate(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_('Öğrenci')
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name=_('Kurs')
    )
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Sertifika Numarası')
    )
    issue_date = models.DateField(auto_now_add=True, verbose_name=_('Veriliş Tarihi'))
    pdf_file = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True,
        verbose_name=_('PDF Dosyası')
    )
    
    class Meta:
        verbose_name = _('Sertifika')
        verbose_name_plural = _('Sertifikalar')
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.certificate_number}"
