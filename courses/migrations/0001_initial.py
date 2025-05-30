# Generated by Django 4.2 on 2025-04-17 15:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.CharField(max_length=255, verbose_name='Cevap Metni')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Doğru mu?')),
            ],
            options={
                'verbose_name': 'Cevap',
                'verbose_name_plural': 'Cevaplar',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Kategori Adı')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
            ],
            options={
                'verbose_name': 'Kategori',
                'verbose_name_plural': 'Kategoriler',
            },
        ),
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('certificate_number', models.CharField(max_length=50, unique=True, verbose_name='Sertifika Numarası')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='Veriliş Tarihi')),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='certificates/', verbose_name='PDF Dosyası')),
            ],
            options={
                'verbose_name': 'Sertifika',
                'verbose_name_plural': 'Sertifikalar',
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Kurs Başlığı')),
                ('slug', models.SlugField(unique=True, verbose_name='Slug')),
                ('description', models.TextField(verbose_name='Açıklama')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Fiyat')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='İndirimli Fiyat')),
                ('thumbnail', models.ImageField(upload_to='course_thumbnails/', verbose_name='Kapak Resmi')),
                ('difficulty', models.CharField(choices=[('beginner', 'Başlangıç'), ('intermediate', 'Orta'), ('advanced', 'İleri')], default='beginner', max_length=20, verbose_name='Zorluk Seviyesi')),
                ('duration', models.PositiveIntegerField(help_text='Toplam saat cinsinden süre', verbose_name='Süre')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')),
                ('is_published', models.BooleanField(default=False, verbose_name='Yayında mı?')),
            ],
            options={
                'verbose_name': 'Kurs',
                'verbose_name_plural': 'Kurslar',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CourseReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], verbose_name='Değerlendirme')),
                ('comment', models.TextField(verbose_name='Yorum')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')),
            ],
            options={
                'verbose_name': 'Kurs Değerlendirmesi',
                'verbose_name_plural': 'Kurs Değerlendirmeleri',
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Tamamlandı mı?')),
                ('progress', models.PositiveIntegerField(default=0, verbose_name='İlerleme')),
            ],
            options={
                'verbose_name': 'Kayıt',
                'verbose_name_plural': 'Kayıtlar',
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Ders Başlığı')),
                ('content_type', models.CharField(choices=[('video', 'Video'), ('text', 'Metin'), ('quiz', 'Quiz')], default='video', max_length=10, verbose_name='İçerik Tipi')),
                ('video_url', models.URLField(blank=True, verbose_name='Video URL')),
                ('content', models.TextField(blank=True, verbose_name='İçerik')),
                ('duration', models.PositiveIntegerField(default=0, help_text='Dakika cinsinden süre', verbose_name='Süre')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                ('is_free', models.BooleanField(default=False, verbose_name='Ücretsiz mi?')),
            ],
            options={
                'verbose_name': 'Ders',
                'verbose_name_plural': 'Dersler',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField(verbose_name='Soru Metni')),
                ('question_type', models.CharField(choices=[('multiple_choice', 'Çoktan Seçmeli'), ('true_false', 'Doğru/Yanlış'), ('short_answer', 'Kısa Cevap')], default='multiple_choice', max_length=20, verbose_name='Soru Tipi')),
                ('points', models.PositiveSmallIntegerField(default=1, verbose_name='Puan')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
            ],
            options={
                'verbose_name': 'Soru',
                'verbose_name_plural': 'Sorular',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Başlık')),
                ('description', models.TextField(blank=True, verbose_name='Açıklama')),
                ('pass_score', models.PositiveSmallIntegerField(default=70, help_text='Sınavı geçmek için gerekli minimum puan (%)', verbose_name='Geçme Puanı')),
                ('time_limit', models.PositiveIntegerField(default=30, help_text='Dakika cinsinden sınav süresi', verbose_name='Süre Limiti')),
                ('is_final', models.BooleanField(default=False, verbose_name='Final Sınavı mı?')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Sınav',
                'verbose_name_plural': 'Sınavlar',
            },
        ),
        migrations.CreateModel(
            name='QuizAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, verbose_name='Puan')),
                ('status', models.CharField(choices=[('in_progress', 'Devam Ediyor'), ('completed', 'Tamamlandı'), ('timed_out', 'Süre Aşımı')], default='in_progress', max_length=20, verbose_name='Durum')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Başlangıç Zamanı')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='Tamamlanma Zamanı')),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='courses.quiz', verbose_name='Sınav')),
            ],
            options={
                'verbose_name': 'Sınav Denemesi',
                'verbose_name_plural': 'Sınav Denemeleri',
            },
        ),
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_answer', models.CharField(blank=True, max_length=255, verbose_name='Metin Cevabı')),
                ('is_correct', models.BooleanField(default=False, verbose_name='Doğru mu?')),
                ('attempt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='courses.quizattempt', verbose_name='Deneme')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.question', verbose_name='Soru')),
                ('selected_answer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='courses.answer', verbose_name='Seçilen Cevap')),
            ],
            options={
                'verbose_name': 'Öğrenci Cevabı',
                'verbose_name_plural': 'Öğrenci Cevapları',
            },
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Bölüm Başlığı')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Sıra')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='courses.course', verbose_name='Kurs')),
            ],
            options={
                'verbose_name': 'Bölüm',
                'verbose_name_plural': 'Bölümler',
                'ordering': ['order'],
            },
        ),
    ]
