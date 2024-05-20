from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Q, Sum, F

from . import serializers

from . import models 


class SupplierViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List suppliers
        """
        qs = models.Supplier.objects.all()
        serializer = serializers.SupplierFullSerializer(qs, many=True)
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

    # Implement in future if there is something to change
    # def update(self, request, pk=None):
    #     """
    #     Update supplier
    #     """
    #     supplier = get_object_or_404(models.Supplier, pk=pk)
    #     serializer = serializers.SupplierFullSerializer(supplier, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """
        Remove supplier
        """
        get_object_or_404(models.Supplier,pk=pk).delete()
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
        '''
        Create new supplied item
        ''' 
        serializer = serializers.SuppliedItemWriteSerializer(
            data=request.data
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
        '''
        List all orders
        ''' 
        qs = models.Order.objects.filter(complete=False).order_by("date_expected_delivery")
        serializer = serializers.OrderSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        '''
        Create new order
        ''' 
        serializer = serializers.OrderSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """
        Fetch order details
        """
        order = get_object_or_404(models.Order, pk=pk)
        serializer = serializers.OrderSerializer(
            order, many=False
        )
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
        List all orders
        """
        qs = models.Item.objects.all()
        serializer = serializers.ItemFullSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """
        Fetch order details
        """
        order = get_object_or_404(models.Item, pk=pk)
        serializer = serializers.ItemFullSerializer(order, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeliveryViewSet(viewsets.ViewSet):
    def create(self, request):
        '''
        Create new delivery
        ''' 
        serializer = serializers.DeliveredItemWriteSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ViewSet):
    def list(self,request):
        '''
        List all items on order
        '''
        results = models.OrderItem.objects.filter(order__complete=False).annotate(
                remaining=F("quantity_requested")
                - Sum("deliveries__quantity_delivered", default=0)
            ).values("item","remaining")
        print(results)
        grouped = {}
        for result in results:
            grouped[result["item"]] = grouped.get(result["item"], 0) + result["remaining"]
        
        out = [{"item":k,"remaining":v} for k,v in grouped.items()]
        return Response(out, status=status.HTTP_200_OK)
