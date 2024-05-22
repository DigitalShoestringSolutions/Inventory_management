from rest_framework import serializers
from django.db import transaction

from .. import models
from .. import utils

import purchase_tracker.serializers.supplied_items

class SlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = ["id"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class FullSerializer(serializers.ModelSerializer):
    suppliers = purchase_tracker.serializers.supplied_items.ItemMap(
        many=True, read_only=True
    )
    class Meta:
        model = models.Item
        fields = ["id", "sources"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class PKField(serializers.Field):
    def to_representation(self, instance):
        return instance.id

    def to_internal_value(self, id):
        try:
            instance = models.Item.objects.get(id=id)
        except models.Item.DoesNotExist:
            try:
                utils.do_get_identity(id)
                instance = models.Item.objects.create(id=id)
            except ValueError as e:
                raise serializers.ValidationError(
                    {"error": "Item identity doesn't exist", "response": e.args}
                )
        return instance
