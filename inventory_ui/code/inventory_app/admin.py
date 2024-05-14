from django.contrib import admin
from . import utils

from . import models

admin.site.register(models.OrderItem)
admin.site.register(models.SupplierItem)


class SupplierInlineAdmin(admin.TabularInline):
    model = models.InventoryItem.suppliers.through


class InventoryItemInlineAdmin(admin.TabularInline): #TODO: this doesn't work for some reason
    model = models.Supplier.supplied_items.through


@admin.register(models.InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["fetched_name", "quantity_per_unit", "minimum_unit"]
    filter_horizontal = ('suppliers',)
    fields = ["item", "fetched_name", "quantity_per_unit", "minimum_unit"]
    readonly_fields = ("fetched_name",)
    inlines = (SupplierInlineAdmin,)

    def fetched_name(self, obj):
        return utils.get_item_name(obj.item)


admin.site.register(models.Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name"]
    # filter_horizontal = ("suppliers",)
    fields = ["name", "homepage"]
    inlines = (InventoryItemInlineAdmin,)