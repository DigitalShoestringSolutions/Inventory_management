from django.urls import path,include
from rest_framework import routers
from . import views
from django.shortcuts import redirect

# def redirect_root(request):
#     response = redirect('jobs/')
#     return response


urlpatterns = [
    path("list/<str:id_type>", views.listByIDType),
    path("list", views.listByIDType),
    path("create", views.createID),
    path("types", views.listTypes),
    path("get/<str:identifier_type>/<str:identifier>", views.identify),
    path("upload", views.uploadIdentities),
    path("<str:id>", views.getID),
    path("", views.getIDs),
]


# /id/list/<tag>    ?full
# /id/get/<identifier_type>/<identifier> ?full
### check Identifier List
### if found return id, desc, name
### if none, check against patterns
### if found
# /id/<id>


# TODO: create ID_TYPE
# TODO: create ID
