from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', _('Öğrenci')),
        ('instructor', _('Eğitmen')),
        ('admin', _('Admin')),
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='student',
        verbose_name=_('Kullanıcı Tipi')
    )
    bio = models.TextField(blank=True, verbose_name=_('Biyografi'))
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True,
        verbose_name=_('Profil Resmi')
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_('Doğum Tarihi')
    )
    phone_number = models.CharField(
        max_length=15, 
        blank=True,
        verbose_name=_('Telefon Numarası')
    )
    
    class Meta:
        verbose_name = _('Kullanıcı')
        verbose_name_plural = _('Kullanıcılar')
        
    def is_student(self):
        return self.user_type == 'student'
    
    def is_instructor(self):
        return self.user_type == 'instructor'
    
    def is_admin_user(self):
        return self.user_type == 'admin'
    
    def __str__(self):
        return self.get_full_name() or self.username
