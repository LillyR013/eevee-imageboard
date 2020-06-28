from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name='logout'),
    path('tags', views.tags, name='tags'),
    path('upload', views.upload, name='upload'),
    re_path(r'view/[1|2|3|4|5|6|7|8|9]{1}\d*', views.displayImage, name='displayImage'),
    path('search', views.search, name='search')
]