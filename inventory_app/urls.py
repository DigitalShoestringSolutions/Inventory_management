from django.urls import path, include
from . import views
from django.urls import re_path
from django.contrib.auth import views as auth_views
# from django.contrib.auth.views import LoginView, LogoutView
# from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.home, name='home'),
    path('adminpage/', views.admin_view, name='admin_view'),
    path('adminpage/download_stock_report/', views.download_stock_report, name='download_stock_report'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('get-item-locations/<int:item_id>', views.get_item_locations, name='get_item_locations'),
    path('user/', views.user, name='user'),
    path('stockcheck/', views.stock_check, name='stock_check'),
    re_path(r'^get-items-for-location/(?P<location_name>.+)$', views.get_items_for_location, name='get_items_for_location'),
    path('update-units-by-location/', views.update_units_by_location, name='update_units_by_location'),

    path('submit-withdrawal/', views.submit_withdrawal, name='submit_withdrawal'),
    path('track/', views.track, name='track'),
    path('track-withdrawals/', views.track_withdrawals, name='track_withdrawals'),
    path('order/', views.order, name='order'),
    path('order_view/', views.order_view, name='order_view'),
    path('consolidate-stock/<int:order_id>/', views.consolidate_stock, name='consolidate_stock'),
    path('get-locations-for-item/<int:item_id>/', views.get_locations_for_item, name='get-locations-for-item'),
    path('analyze/', views.analyze, name='analyze'),
    path('item/', views.item_search, name='item_search'),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    path('accounts/profile/', views.profile, name='profile'),

    # path('accounts/', include('django.contrib.auth.urls')),
    # path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', LogoutView.as_view(next_page='home'), name='logout'),


    # Define other URLs for your app 
]
