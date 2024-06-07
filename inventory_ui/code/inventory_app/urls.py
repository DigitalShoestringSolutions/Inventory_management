from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("", views.HomePageView.as_view(), name="home"),
    path("withdraw/", views.WithdrawalPageView.as_view(), name="withdraw"),
    path("admin/", views.AdminPageView.as_view(), name="admin_view"),
    path("order/", views.OrderPageView.as_view(), name="order_view"),
    path("track/", views.TrackPageView.as_view(), name="track"),
    path("analyze/", views.AnalyzePageView.as_view(), name="analyze"),
    # AJAX
    path(
        "get-item-details/<str:item_id>/",
        views.get_item_details,
        name="get_item_details",
    ),
    path(
        "consolidate-stock/<int:order_id>/",
        views.consolidate_stock,
        name="consolidate_stock",
    ),
    path(
        "get-locations-for-item/<str:item_id>/",
        views.get_locations_for_item,
        name="get-locations-for-item",
    ),
    # redirects
    path(
        "download_stock_report", views.download_stock_report, name="download_stock_report"
    ),
]
