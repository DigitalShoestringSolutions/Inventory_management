from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q, Sum, F, Count

from rest_framework.decorators import api_view, renderer_classes, action
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from django.conf import settings
import requests
import datetime

from . import serializers

from . import models
from . import utils


class SupplierViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List suppliers
        """
        detail = request.GET.get("detail", "min")
        filter_active = request.GET.get("active")
        if filter_active:
            qs = models.Supplier.objects.annotate(
                num_active_orders=Count("current_orders")
            ).filter(num_active_orders__gt=0)
        else:
            qs = models.Supplier.objects.all()
        if detail == "full":
            serializer = serializers.SupplierFullSerializer(qs, many=True)
        else:
            serializer = serializers.SupplierSlugSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create supplier
        """
        serializer = serializers.SupplierFullSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Get supplier and supplied items
        """
        supplier = get_object_or_404(models.Supplier, pk=pk)
        serializer = serializers.SupplierFullSerializer(supplier, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    ##[{"item":"item@4","expected_lead_time":"7 00:00:00"},{"item":"item@9","expected_lead_time":null},{"item":"item@10","expected_lead_time":null},{"item":"item@12","expected_lead_time":null}]
    @action(detail=True, methods=["put"])
    def update_supplied_items(self, request, pk=None):
        supplier = get_object_or_404(models.Supplier, pk=pk)
        supplied_items = {entry.item.id:entry.id for entry in supplier.supplied_items.all()}

        new_items = []
        for entry in request.data:
            item_id = entry["item"]
            expected_lead_time_raw = entry.get("expected_lead_time")
            product_page_raw = entry.get("product_page")

            expected_lead_time = None
            if expected_lead_time_raw:
                expected_lead_time = datetime.timedelta(days=int(expected_lead_time_raw))

            if item_id in supplied_items:
                print(f"UPDATE {item_id}")
                instance = models.SuppliedItem.objects.get(id=supplied_items[item_id])
                instance.expected_lead_time = expected_lead_time
                instance.save()
                del supplied_items[item_id]
            else:
                print(f"CREATE {item_id}")
                item,_created = models.Item.objects.get_or_create(id=item_id)
                models.SuppliedItem.objects.update_or_create(
                    supplier=supplier, item=item, expected_lead_time=expected_lead_time
                )

        remove_qs = models.SuppliedItem.objects.filter(id__in=supplied_items.values())
        if len(remove_qs)>0:
            print(f"Deleting {remove_qs} as they were not present in the update")
            remove_qs.delete()

        serializer = serializers.SupplierFullSerializer(supplier, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Remove supplier
        """
        get_object_or_404(models.Supplier, pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class SupplierItemViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        List suppliers
        """
        qs = models.SuppliedItem.objects.all()
        # for obj in qs:
        #     updated = obj.update_lead_time()
        #     if updated: obj.save()
        serializer = serializers.SuppliedItemReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create new supplied item
        """
        serializer = serializers.SuppliedItemWriteSerializer(
            data=request.data, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """
        Update supplied item
        """
        suppliedItem = get_object_or_404(models.SuppliedItem, pk=pk)
        serializer = serializers.SuppliedItemWriteSerializer(
            suppliedItem, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Remove supplied item
        """
        get_object_or_404(models.SuppliedItem, pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        List all orders
        """
        supplier = request.GET.get("supplier")

        filter = Q(complete=False)
        if supplier is not None:
            filter = filter & Q(supplier=supplier)
        qs = models.Order.objects.filter(filter).order_by("date_expected_delivery")
        serializer = serializers.OrderReadSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create new order
        """
        serializer = serializers.OrderWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Fetch order details
        """
        order = get_object_or_404(models.Order, pk=pk)
        serializer = serializers.OrderReadSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """
        Ammend order or set complete
        """
        order = get_object_or_404(models.Order, pk=pk)
        serializer = serializers.OrderUpdateSerializer(order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        Partial update
        """
        order = get_object_or_404(models.Order, pk=pk)
        serializer = serializers.OrderUpdateSerializer(
            order, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Delete order
        """
        get_object_or_404(models.Order, pk=pk).delete()
        return Response(status=status.HTTP_200_OK)


class ItemViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        List all items
        """
        qs = models.Item.objects.all()
        serializer = serializers.ItemFullSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self,request):
        """
        Create new item
        """
        name = request.data.get("name")
        if name:
            url = settings.IDENTITY_PROVIDER_URL
            resp = requests.post(f"http://{url}/id/create",{"name":name,"type":"item"})
            if resp.status_code == 201:
                obj = resp.json()
                item = models.Item.objects.create(id=obj['id'])
                serializer = serializers.ItemSlugSerializer(item)
                return Response(serializer.data, status=201)
            else:
                return Response(resp.json,status=resp.status_code)
        else:
            return Response({"message":"name not provided"},status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Fetch item details
        """
        order = get_object_or_404(models.Item, pk=pk)
        serializer = serializers.ItemFullSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeliveryViewSet(viewsets.ViewSet):
    def create(self, request):
        """
        Create new delivery
        """
        serializer = serializers.DeliveredItemWriteSerializer(
            data=request.data, many=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # TODO move
        # settings.INBOUND_LOCATION_ID
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderItemViewSet(viewsets.ViewSet):
    def list(self, request):
        """
        List all items on order
        """
        detail = request.GET.get("detail", "summary")
        if detail == "full":
            supplier = request.GET.get("supplier")
            filter = (
                Q(order__complete=False, order__supplier=supplier)
                if supplier
                else Q(order__complete=False)
            )

            results = (
                models.OrderItem.objects.filter(filter)
                .annotate(
                    remaining=F("quantity_requested")
                    - Sum("deliveries__quantity_delivered", default=0),
                    purchase_order=F("order__purchase_order_reference"),
                    expected_delivery=F("order__date_expected_delivery"),
                )
                .values(
                    "id", "item", "remaining", "purchase_order", "expected_delivery"
                )
            )
            results = [
                {**entry, "item": utils.get_name(entry["item"])} for entry in results
            ]
            return Response(results, status=status.HTTP_200_OK)
        else:
            results = (
                models.OrderItem.objects.filter(order__complete=False)
                .annotate(
                    remaining=F("quantity_requested")
                    - Sum("deliveries__quantity_delivered", default=0)
                )
                .values("item", "remaining")
            )
            print(results)
            grouped = {}
            for result in results:
                grouped[result["item"]] = (
                    grouped.get(result["item"], 0) + result["remaining"]
                )

            out = [{"item": k, "remaining": v} for k, v in grouped.items()]
            return Response(out, status=status.HTTP_200_OK)


@api_view(("GET",))
@renderer_classes((JSONRenderer, BrowsableAPIRenderer))
def known_items(request):
    url = settings.IDENTITY_PROVIDER_URL
    resp = requests.get(f"http://{url}/id/list/item")
    return Response(resp.json(),status=status.HTTP_200_OK)
