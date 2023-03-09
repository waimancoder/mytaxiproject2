"""mytaxi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf.urls import handler500
from django.contrib import admin
from django.urls import path, include
from user_account.views import custom_404_page_not_found, custom_500_page_not_found

handler404 = custom_404_page_not_found
handler500 = custom_500_page_not_found

urlpatterns = [
    path('', include('user_account.urls')),
    path('admin/', admin.site.urls),
    path('', include('rides.urls')),
]

