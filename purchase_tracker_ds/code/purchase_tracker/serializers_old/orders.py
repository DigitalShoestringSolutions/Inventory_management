from rest_framework import serializers
from django.db import transaction

from .. import models
from .. import utils
from . import order_items


class OrderSerializer(serializers.ModelSerializer):
    items = order_items.OrderItemSerializer(many=True)
    class Meta:
        model = models.Order
        fields = [
            "pk",
            "supplier",
            "ordered_by",
            "purchase_order_reference",
            "items",
            "date_enquired",
            "date_order_placed",
            "date_expected_delivery",
            "complete",
        ]
        read_only_fields = ["pk"]

    def create(self, validated_data):
        print(f"O {validated_data}")

        with transaction.atomic():
            items_data = validated_data.pop("items",[])
            order = models.Order.objects.create(**validated_data)
            print(f"OOO {order} {items_data}")
            for order_item_data in items_data:
                models.OrderItem.objects.create(order=order,**order_item_data)

        return order
