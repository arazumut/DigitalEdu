from django.urls import path
from .views import home, contact, about, admin_index, subscribe

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('admin-dashboard/', admin_index, name='admin_dashboard'),
    path('subscribe/', subscribe, name='subscribe'),
] 