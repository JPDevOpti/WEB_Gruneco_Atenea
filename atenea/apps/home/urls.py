# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views
from .views import login_view

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Matches any html file
    re_path(r'^(?!login).*\.*', views.pages, name='pages'),
    
]

