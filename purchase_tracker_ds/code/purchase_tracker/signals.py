from django.db.models.signals import post_save
from . import models

# Runs post create callback when saved
post_save.connect(models.DeliveredItem.post_create, sender=models.DeliveredItem)
