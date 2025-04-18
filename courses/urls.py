from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('category/<slug:slug>/', views.course_category, name='course_category'),
    path('instructor/<str:username>/', views.instructor_courses, name='instructor_courses'),
    path('new/', views.course_create, name='course_create'),
    path('edit/<slug:slug>/', views.course_edit, name='course_edit'),
    
    # Bölüm ve ders yönetimi
    path('<slug:course_slug>/sections/new/', views.section_create, name='section_create'),
    path('<slug:course_slug>/sections/<int:section_id>/edit/', views.section_edit, name='section_edit'),
    path('<slug:course_slug>/sections/<int:section_id>/delete/', views.section_delete, name='section_delete'),
    path('<slug:course_slug>/sections/<int:section_id>/lessons/new/', views.lesson_create, name='lesson_create'),
    path('<slug:course_slug>/sections/<int:section_id>/lessons/<int:lesson_id>/edit/', views.lesson_edit, name='lesson_edit'),
    path('<slug:course_slug>/sections/<int:section_id>/lessons/<int:lesson_id>/delete/', views.lesson_delete, name='lesson_delete'),
    
    # Öğrenci ilerleme ve yorumlar
    path('<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    path('<slug:slug>/review/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('<slug:slug>/review/<int:review_id>/delete/', views.delete_review, name='delete_review'),
    
    # Sınav ve sertifika
    path('<slug:course_slug>/quizzes/new/', views.quiz_create, name='quiz_create'),
    path('<slug:course_slug>/quizzes/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('<slug:course_slug>/quizzes/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('<slug:course_slug>/quizzes/<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('<slug:course_slug>/quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<slug:course_slug>/quizzes/<int:quiz_id>/results/', views.quiz_results, name='quiz_results'),
    path('<slug:course_slug>/certificate/', views.generate_certificate, name='generate_certificate'),
] 