from django.db import models
from django.utils import timezone
import datetime
from . import utils

class InventoryItem(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    quantity_per_unit = models.CharField(
        max_length=100
    )  # Assuming this is a descriptive field
    minimum_unit = models.IntegerField()
    
    def __str__(self):
        return utils.get_name(self.id)
