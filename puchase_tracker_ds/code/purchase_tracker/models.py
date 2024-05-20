from django.db import models
import datetime
from . import utils


class Supplier(models.Model):
    id = models.CharField(max_length=32, primary_key=True)

    # internal analysis
    performance_metric = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    def __str__(self):
        return utils.get_name(self.id)


class Item(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    suppliers = models.ManyToManyField(
        Supplier, through="SuppliedItem", related_name="supplied_items"
    )  # Not strictly needed here as the relationship is defined in the SupplierItem model, but it helps with related_name

    def __str__(self):
        return utils.get_name(self.id)


class SuppliedItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="sources")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    # optional
    product_page = models.URLField(max_length=200, null=True, blank=True)
    # cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # internal analysis
    expected_lead_time = models.DurationField(null=True, blank=True)

    # metadata
    last_updated = models.DateField(
        auto_now=True
    )  # Automatically updates whenever the Model is saved

    def __str__(self):
        return f"{str(self.item)} from {self.supplier}"

    class Meta:
        unique_together = (
            "item",
            "supplier",
        )

    def update_lead_time(self):
        results = (
            DeliveredItem.objects.filter(
                ordered_item__order__supplier=self.supplier,
                ordered_item__item=self.item,
            )
            .annotate(
                actual_lead_time=models.F("delivery_date")
                - models.F("ordered_item__order__date_order_placed")
            )
        )

        weighted_sum = 0
        total_sum = 0
        for result in results:
            days = result.actual_lead_time / datetime.timedelta(days=1)
            weighted_sum += days * result.quantity_delivered
            total_sum += result.quantity_delivered

        if total_sum != 0:
            new_lead_time = datetime.timedelta(days=weighted_sum/total_sum)
            self.expected_lead_time = new_lead_time
            return True
        return False

class Order(models.Model):
    supplier = models.ForeignKey(
        Supplier, related_name="current_orders", on_delete=models.CASCADE
    )
    purchase_order_reference = models.CharField(
        max_length=40, help_text="The purchase order reference number"
    )
    ordered_by = models.CharField(
        max_length=30, help_text="The person or department that the order is for"
    )

    # Dates
    date_enquired = models.DateField(null=True, blank=True)
    date_order_placed = models.DateField(default=datetime.date.today)
    date_expected_delivery = models.DateField()

    # Status
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.purchase_order_reference}"

    def is_overdue(self):
        return datetime.date.today() > self.date_expected_delivery and not self.complete


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, related_name="ordered", on_delete=models.CASCADE)
    quantity_requested = models.IntegerField()

    class Meta:
        unique_together = (
            "item",
            "order",
        )

    def get_remaining(self):
        delivered = self.deliveries.aggregate(
            models.Sum("quantity_delivered", default=0)
        )["quantity_delivered__sum"]
        return self.quantity_requested - delivered
    


class DeliveredItem(models.Model):
    ordered_item = models.ForeignKey(
        OrderItem, related_name="deliveries", on_delete=models.CASCADE
    )
    quantity_delivered = models.IntegerField()
    delivery_date = models.DateField(default=datetime.date.today)
