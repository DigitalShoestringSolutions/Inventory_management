from django.urls import path,include
from . import views

urlpatterns= [ 
        path('transfer',views.transferRequest)
    ]

#/action/transfer
