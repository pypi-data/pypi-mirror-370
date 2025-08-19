"""
URL configuration for bpserver project.

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
from django.urls import path,re_path
from app01 import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
urlpatterns = [
    path("", views.index),
    path("login/", views.login),
    path("basedir/", views.basedir),
    path("hashcheck/", views.hashCheck),
    path("dirs/", views.dirs),
    path("uploadfile/", views.uploadfile),
    path("checkversion/", views.checkversion),
    path("weblogin/", views.weblogin),
    path("webensure/", views.webensure),
    path("ping/", views.ping),
    path("projectlist/", views.projectlist),
    path("islive", views.islive),
    path("islive/", views.islive),
    re_path(r"^getdirs/(?P<path>.*)$", views.getdirs),
    re_path(r"^clientgetdirs/(?P<path>.*)$", views.clientgetdirs),
    path("doc/", TemplateView.as_view(template_name="index.html"), name="doc"),
    path("dirishere/",TemplateView.as_view(template_name="index.html"), name="dirishere"),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)