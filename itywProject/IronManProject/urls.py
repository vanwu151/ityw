"""IronManProject URL Configuration

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
from django.urls import path
from ITYW import views
from django.views import static 
from django.conf import settings 
from django.conf.urls import url 



urlpatterns = [
    path('json_test/', views.json_test),
    path('', views.relogin),
    path('login/', views.login),
    path('logininfo/', views.logininfo),
    path('logout/', views.logout),
    path('useriteminfo/', views.useriteminfo),
    path('itemstockinfo/', views.itemstockinfo),
    path('manageiteminfo/', views.manageiteminfo),
    path('Additem/', views.Additem),
    path('register/', views.register),
    path('EditItem/', views.EditItem),
    path('Moditem/', views.Moditem),
    path('searchitem/', views.searchitem),
    path('PageItemInfo/', views.PageItemInfo),
    path('PageItemStock/', views.PageItemStock),
    path('PageUserItem/', views.PageUserItem),
    path('searchitemsn/', views.searchitemsn),
    path('searchuserinfo/', views.searchuserinfo),
    path('searchitemstock/', views.searchitemstock),
    path('Modrole/', views.ModRole),
    path('Modinfo/', views.Modinfo),
    path('InfoModed/', views.InfoModed),
    path('Manage/', views.Manage),
    path('admin/', admin.site.urls),
    # path('PageFunc/', views.PageFunc),
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),    
]
