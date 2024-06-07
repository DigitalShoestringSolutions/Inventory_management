from rest_framework import serializers
from django.db import transaction

from .. import models
from .. import utils


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderItem
        fields = ["pk", "item", "quantity_requested"]
        read_only_fields = ["pk"]

    # def create(self, validated_data):
    #     # TODO: in transaction
    #     print(f"OI {validated_data}")
    #     item_data = validated_data.pop("item", {})
    #     item_obj,_created = models.Item.objects.get_or_create(id=item_data["id"])
    #     return models.OrderItem.objects.create(item=item_obj, **validated_data)
