"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('imageboard.urls')),
    path('login', include('imageboard.urls')),
    path('signup', include('imageboard.urls')),
    path('logout', include('imageboard.urls')),
    path('tags', include('imageboard.urls')),
    path('upload', include('imageboard.urls')),
    re_path(r'view/[1|2|3|4|5|6|7|8|9]{1}\d*', include('imageboard.urls')),
    path('search', include('imageboard.urls'))
]
