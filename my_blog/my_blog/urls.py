"""
URL configuration for my_blog project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from blog import views

from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('blog/',views.blog_home, name='blog_home'),
    path('blog/', views.post_list, name='post_list'),
    path('blog/create', views.post_create, name= 'post_form'),
    path('blog/<int:pk>/', views.post_detail, name='post_detail'),
    path('blog/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('blog/<int:pk>/delete/', views.post_delete, name='post_delete'),
    path('login/',auth_views.LoginView.as_view(template_name='blog/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
