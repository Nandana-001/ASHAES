"""
URL configuration for exam project.

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
from myapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',login,name='login'),
    path('login/',login,name='login'),
    path('teacher_login/',teacher_login,name='teacher_login'),
    path('student_registeration/',student_registration,name='student_registration'),
    path('student_login/',student_login,name='student_login'),
    path('profile_view/',profile_view,name='profile_view'),
    path('index/',index,name='index'),
    path('teacher_view/',teacher_view,name='teacher_view'),
    path('teacher_home/',teacher_home,name='teacher_home'),
    path('answerkey/',answerkey,name='answerkey'),
    path('upload_answerkey/',upload_answerkey,name='upload_answerkey'),
    path('student_submit/',student_submit,name='student_submit'),
    path('upload_answer_key/',upload_answer_key,name='upload_answer_key'),
    path('profile/',profile,name='profile'),
    path('evaluate/',evaluate,name='evaluate'),
    path('evaluate_answer_key/<str:subject>/', evaluate_answer_key, name='evaluate_answer_key'),
    path('logout_view/',logout_view,name='logout_view'),
    path('teacher_dashboard/',teacher_dashboard,name='teacher_dashboard'),
]
