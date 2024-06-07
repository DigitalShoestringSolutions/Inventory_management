from rest_framework import serializers
from django.db import transaction

from .. import models
from .. import utils

from . import suppliers, items

class Read(serializers.ModelSerializer):
    supplier = suppliers.Slug(many=False, read_only=True)
    item = items.SlugSerializer(many=False, read_only=True)

    class Meta:
        model = models.SuppliedItem
        fields = [
            "pk",
            "item",
            "supplier",
            "product_page",
            "expected_lead_time",
            "last_updated",
        ]
        read_only_fields = ["pk", "last_updated"]


class ItemMap(serializers.ModelSerializer):
    supplier = suppliers.Slug(many=False, read_only=True)

    class Meta:
        model = models.SuppliedItem
        fields = [
            "pk",
            "supplier",
            "product_page",
            "expected_lead_time",
            "last_updated",
        ]
        read_only_fields = ["pk", "last_updated"]


class Write(serializers.ModelSerializer):
    item = items.PKField()
    class Meta:
        model = models.SuppliedItem
        fields = [
            "item",
            "supplier",
            "product_page",
            "expected_lead_time",
        ]

    # def validate_item(self, value):
    #     print(f"validator {value}")
    #     return value
