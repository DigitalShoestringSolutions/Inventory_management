from django.urls import path,include
from rest_framework import routers
from . import views
# from django.shortcuts import redirect

# def redirect_root(request):
#     response = redirect('jobs/')
#     return response


urlpatterns= [ 
        path('',views.getAllEvents),
        path('for/<str:item_id>',views.eventsForChild),
        path('to/<str:location_link>',views.eventsToParent),
        path('from/<str:location_link>',views.eventsFromParent),
        path('at/<str:location_link>',views.eventsAtParent),
    ]

#/events/                           ?from=timestamp ?to=timestamp
#/events/for/<item_id>              ?from=timestamp ?to=timestamp
#/events/to/<loc_id>                ?from=timestamp ?to=timestamp
#/events/from/<loc_id>              ?from=timestamp ?to=timestamp
#/events/at/<loc_id>                ?from=timestamp ?to=timestamp
