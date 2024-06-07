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


class SuppliedItemReverseMap(serializers.ModelSerializer):
    item = ItemSlugSerializer(many=False, read_only=True)

    class Meta:
        model = models.SuppliedItem
        fields = [
            "id",
            "item",
            "product_page",
            "expected_lead_time",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        if instance.expected_lead_time:
            output["expected_lead_time"] = instance.expected_lead_time.days
        return output


class SuppliedItemMap(serializers.ModelSerializer):
    supplier = SupplierSlugSerializer(many=False, read_only=True)

    class Meta:
        model = models.SuppliedItem
        fields = [
            "id",
            "supplier",
            "product_page",
            "expected_lead_time",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        if instance.expected_lead_time:
            output["expected_lead_time"] = instance.expected_lead_time.days
        return output


class ItemFullSerializer(serializers.ModelSerializer):
    sources = SuppliedItemMap(many=True, read_only=True)

    class Meta:
        model = models.Item
        fields = ["id", "sources"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output


class ItemidField(serializers.Field):
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
        fields = ["id", "quantity_delivered", "delivery_date"]
        read_only_fields = ["id"]


class DeliveredItemWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DeliveredItem
        fields = ["ordered_item", "quantity_delivered", "delivery_date"]


class OrderItemReadSerializer(serializers.ModelSerializer):
    deliveries = DeliveredItemSlugSerializer(many=True,read_only = True)
    item = ItemSlugSerializer(read_only=True)
    class Meta:
        model = models.OrderItem
        fields = ["id", "item", "quantity_requested", "deliveries"]
        read_only_fields = ["id"]

    def to_representation(self, instance):
        output =  super().to_representation(instance)
        output["remaining"] = instance.get_remaining()
        return output


class OrderItemWriteSerializer(serializers.ModelSerializer):
    deliveries = DeliveredItemSlugSerializer(many=True, read_only=True)

    class Meta:
        model = models.OrderItem
        fields = ["id", "item", "quantity_requested", "deliveries"]
        read_only_fields = ["id"]


class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = [
            "id",
            "supplier",
            "ordered_by",
            "purchase_order_reference",
            "date_enquired",
            "date_order_placed",
            "date_expected_delivery",
            "complete",
        ]
        read_only_fields = ["id"]


class OrderReadSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True)
    supplier = SupplierSlugSerializer(read_only = True)

    class Meta:
        model = models.Order
        fields = [
            "id",
            "supplier",
            "ordered_by",
            "purchase_order_reference",
            "items",
            "date_enquired",
            "date_order_placed",
            "date_expected_delivery",
            "complete",
        ]
        read_only_fields = ["id"]


class OrderWriteSerializer(serializers.ModelSerializer):
    items = OrderItemWriteSerializer(many=True)

    class Meta:
        model = models.Order
        fields = [
            "id",
            "supplier",
            "ordered_by",
            "purchase_order_reference",
            "items",
            "date_enquired",
            "date_order_placed",
            "date_expected_delivery",
            "complete",
        ]
        read_only_fields = ["id"]

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
            "id",
            "item",
            "supplier",
            "product_page",
            "expected_lead_time",
            "last_updated",
        ]
        read_only_fields = ["id", "last_updated"]

    def to_representation(self, instance):
        output = super().to_representation(instance)
        if instance.expected_lead_time:
            output["expected_lead_time"] = instance.expected_lead_time.days
        return output


class SuppliedItemWriteSerializer(serializers.ModelSerializer):
    item = ItemidField()

    class Meta:
        model = models.SuppliedItem
        fields = [
            "item",
            "supplier",
            "product_page",
            "expected_lead_time",
        ]


class SupplierFullSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    supplied_items = SuppliedItemReverseMap(many=True, read_only=True)

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

    def to_representation(self, instance):
        output = super().to_representation(instance)
        output["name"] = utils.get_name(instance.id)
        return output

# class DeliverySerializer(serializers.Serializer):
#     delivered_items = DeliveredItemSerializer(many = True)

#     class Meta:
#         fields = ["delivered_items"]
