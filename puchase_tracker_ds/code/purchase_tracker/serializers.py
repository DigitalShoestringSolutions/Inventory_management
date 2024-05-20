from rest_framework import serializers
from django.db import transaction

from . import models
from . import utils


class ItemSlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Item
        fields = ["id"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class SupplierSlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Supplier
        fields = ["id"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class SuppliedItemMap(serializers.ModelSerializer):
    supplier = SupplierSlugSerializer(many=False, read_only=True)

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

class ItemFullSerializer(serializers.ModelSerializer):
    sources = SuppliedItemMap(many=True, read_only=True)

    class Meta:
        model = models.Item
        fields = ["id", "sources"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class ItemPKField(serializers.Field):
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

class DeliveredItemSlugSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DeliveredItem
        fields = ["pk", "quantity_delivered", "delivery_date"]
        read_only_fields = ["pk"]


class DeliveredItemWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DeliveredItem
        fields = ["ordered_item", "quantity_delivered", "delivery_date"]


class OrderItemSerializer(serializers.ModelSerializer):
    deliveries = DeliveredItemSlugSerializer(many=True,read_only = True)
    class Meta:
        model = models.OrderItem
        fields = ["pk", "item", "quantity_requested", "deliveries"]
        read_only_fields = ["pk"]

    # def create(self, validated_data):
    #     # TODO: in transaction
    #     print(f"OI {validated_data}")
    #     item_data = validated_data.pop("item", {})
    #     item_obj,_created = models.Item.objects.get_or_create(id=item_data["id"])
    #     return models.OrderItem.objects.create(item=item_obj, **validated_data)

    def to_representation(self, instance):
        output =  super().to_representation(instance)
        output["remaining"] = instance.get_remaining()
        return output


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = [
            "pk",
            "supplier",
            "ordered_by",
            "purchase_order_reference",
            "date_enquired",
            "date_order_placed",
            "date_expected_delivery",
            "complete",
        ]
        read_only_fields = ["pk"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

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
            items_data = validated_data.pop("items", [])
            order = models.Order.objects.create(**validated_data)
            print(f"OOO {order} {items_data}")
            for order_item_data in items_data:
                models.OrderItem.objects.create(order=order, **order_item_data)

        return order


class SuppliedItemReadSerializer(serializers.ModelSerializer):
    supplier = SupplierSlugSerializer(many=False, read_only=True)
    item = ItemSlugSerializer(many=False, read_only=True)

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


class SuppliedItemWriteSerializer(serializers.ModelSerializer):
    item = ItemPKField()

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


class SupplierFullSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    supplied_items = ItemFullSerializer(many=True, read_only=True)

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

    # def update(self, instance, validated_data):
    #     # TODO: change name
    #     super().update(instance, validated_data)

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output

# class DeliverySerializer(serializers.Serializer):
#     delivered_items = DeliveredItemSerializer(many = True)

#     class Meta:
#         fields = ["delivered_items"]
