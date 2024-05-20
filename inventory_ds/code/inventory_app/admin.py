from django.contrib import admin
from . import utils

from . import models

@admin.register(models.InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ["fetched_name", "quantity_per_unit", "minimum_unit"]
    fields = ["id", "fetched_name", "quantity_per_unit", "minimum_unit"]
    readonly_fields = ("fetched_name",)

    def fetched_name(self, obj):
        return utils.get_name(obj.id)


# admin.site.register(models.Supplier)
# class SupplierAdmin(admin.ModelAdmin):
#     list_display = ["name"]
#     # filter_horizontal = ("suppliers",)
#     fields = ["name", "homepage"]
#     inlines = (InventoryItemInlineAdmin,)