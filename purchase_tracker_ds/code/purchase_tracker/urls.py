from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"supplier", views.SupplierViewSet, basename="supplier")
router.register(r"supplied_item", views.SupplierItemViewSet, basename="supplied_item")
router.register(r"order", views.OrderViewSet, basename="order")
router.register(r"ordered_item", views.OrderItemViewSet, basename="ordered_item")
router.register(r"item", views.ItemViewSet, basename="item")
router.register(r"delivery", views.DeliveryViewSet, basename="delivery")


urlpatterns = router.urls

urlpatterns.extend(
    [
        # path("list/<str:id_type>", views.listByIDType),
        path("known_items/", views.known_items),
    ]
)
