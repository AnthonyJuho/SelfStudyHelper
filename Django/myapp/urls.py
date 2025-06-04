"""ksaproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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

from django.urls import path
from myapp import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('', views.main_view),
    path('student/', views.student_search, name='student_search'),
    path('login/', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('main/', views.main_view, name='main'),
    path('mark_absent/', views.mark_absent, name='mark_absent'),
    path('unmark_absent/', views.unmark_absent, name='unmark_absent'),
    path('delete_absent/', views.delete_absent, name='delete_absent'),
]