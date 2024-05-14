from django.contrib import admin
from . import models
# from adminsortable.admin import SortableAdmin
import datetime
import time

# node inline


@admin.register(models.Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ["edge_id", "child", "parent", "start", "end", "quantity"]
    fields = ("edge_id", "child", "parent", "start", "end", "quantity")
    readonly_fields = ("edge_id",)
    list_filter = ["parent", "child__type"]
    ordering = ["-start"]

@admin.register(models.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        "event_id",
        "child",
        "from_parent",
        "to_parent",
        "timestamp",
        "quantity",
    ]
    fields = (
        "event_id",
        "child",
        "from_parent",
        "to_parent",
        "timestamp",
        "quantity",
    )
    readonly_fields = ('event_id',)
    list_filter = ["child", "to_parent"]
    ordering = ['event_id']


# @admin.register(models.Node)
admin.site.register(models.Node)
