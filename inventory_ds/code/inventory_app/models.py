from django.db import models
from django.utils import timezone
import datetime
from . import utils


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    homepage = models.URLField(max_length=200)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    item = models.CharField(max_length=32, primary_key=True)
    quantity_per_unit = models.CharField(
        max_length=100
    )  # Assuming this is a descriptive field
    minimum_unit = models.IntegerField()
    suppliers = models.ManyToManyField(
        Supplier, through="SupplierItem", related_name="supplied_items"
    )  # Not strictly needed here as the relationship is defined in the SupplierItem model, but it helps with related_name

    def __str__(self):
        return utils.get_item_name(self.item)


class SupplierItem(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    supplier_link = models.URLField(max_length=200, null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_lead_time = models.DurationField(null=True, blank=True)
    # potentially useful information to add:
    last_updated = models.DateField(
        auto_now=True
    )  # Automatically updates whenever the Model is saved

    def __str__(self):
        return f"{str(self.item)} from {self.supplier.name}"


class OrderItem(models.Model):
    supplier_item = models.ForeignKey(
        SupplierItem, related_name="current_orders", on_delete=models.CASCADE
    )
    on_order = models.IntegerField(default=0)
    quantity_per_unit = models.CharField(
        max_length=100
    )  # Assuming this is a descriptive field
    unit = models.IntegerField()  ## ? What is this ? (Greg)
    minimum_unit = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateField(default=datetime.date.today)
    requested_by = models.CharField(max_length=255)
    oracle_order_date = models.DateField(default=datetime.date.today)
    oracle_po = models.CharField(max_length=255)
    order_lead_time = models.DateField()  ## ? Expected Delivery ? (Greg)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.item)

    def calculate_lead_time(self):
        if self.order_lead_time and self.oracle_order_date:
            return (self.order_lead_time - self.oracle_order_date).days
        return 0

    def days_since_oracle_order(self):
        return (
            (date.today() - self.oracle_order_date).days
            if self.oracle_order_date
            else 0
        )
