from rest_framework import serializers
from django.db import transaction

from .. import models
from .. import utils

from . import items

class Slug(serializers.ModelSerializer):
    class Meta:
        model = models.Supplier
        fields = ["id"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


#     def to_internal_value(self, data):
#         print(f"IN INTERNAL {data}")
#         # output = super().to_internal_value(data)
#         # print(f"AFTER {output}")
#         try:
#             item = models.Item.objects.get(**data)
#         except models.Item.DoesNotExist:
#             item = models.Item(**data)
#         return data


class Full(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    supplied_items = items.SlugSerializer(many=True, read_only=True)

    class Meta:
        model = models.Supplier
        fields = ["id", "name", "supplied_items"]
        read_only_fields = ["id"]
        # extra_kwargs = {"name": {"write_only": True}}

    def create(self, validated_data):
        name = validated_data.pop("name")
        status, payload = utils.create_new_supplier_identity(name)
        if status != 201:
            raise serializers.ValidationError(
                {"error": "Couldn't create a new identity", "response": payload}
            )
        validated_data["id"] = payload["id"]
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # TODO: change name
        super().update(instance, validated_data)

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output
