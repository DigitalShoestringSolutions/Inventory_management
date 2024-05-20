"""
URL configuration for site_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.shortcuts import redirect


def redirect_root(request):
    response = redirect("/admin")
    return response


urlpatterns = [
    path("", redirect_root),
    path("admin/", admin.site.urls),
    path("api/",include("purchase_tracker.urls"))
]


admin.site.site_header = "Purchase Tracker Admin"
admin.site.site_title = "Purchase Tracker Admin Portal"
admin.site.index_title = "Welcome to Purchase Order Tracker Administration Portal"

from django.contrib.auth.models import Group

admin.site.unregister(Group)
