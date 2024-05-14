from django.db import models

class IdentityType(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=30, help_text="The type of identity e.g. Product Type, Product ID, Location")
    tag = models.CharField(max_length=8, unique=True,help_text='A unique tag that prefixes the id string e.g. "prodtype", "prod_id", "loc"')
    individual = models.BooleanField(default=False, help_text="Set to true if identities of this type are individual (e.g. part id), set to false if identities of this type are collections (e.g. part type)")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'ID Types'

class IdentityEntry(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=300, blank=True, null=True)
    type = models.ForeignKey(IdentityType,on_delete=models.CASCADE,related_name="identities")
    parent = models.ForeignKey('self',blank=True,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.type.title}:{self.name}"
    
    def get_id(self):
        return f"{self.type.tag}@{self.auto_id}"

    class Meta:
        verbose_name_plural = "ID Entries"
        unique_together = ('type', 'auto_id',)

class ExtraField(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    for_type = models.ForeignKey(IdentityType, on_delete=models.CASCADE)
    key = models.CharField(max_length=15)

    class Meta:
        unique_together = ('key', 'for_type',)

class ExtraFieldEntry(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    for_entry = models.ForeignKey(IdentityEntry, on_delete = models.CASCADE)
    field = models.ForeignKey(ExtraField, on_delete = models.CASCADE)
    value = models.CharField(max_length=50)

    class Meta:
        unique_together = ('field', 'for_entry',)

class IdentifierType(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=30, help_text="The type of identification used e.g. barcode, RFID, Bluetooth Low Energy")
    tag = models.CharField(max_length=8, unique=True, help_text='Tag used to identify that this type of identifier is used e.g. "barcode", "rfid", "ble"')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Identifier Types'

class Identifier(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    value = models.CharField(max_length=50)
    type = models.ForeignKey(IdentifierType, on_delete=models.CASCADE, related_name="identifiers")
    target = models.ForeignKey(IdentityEntry, on_delete=models.CASCADE, related_name = "identifiers")

    def __str__(self):
        return f"{self.type.title}:{self.value}"

class IdentifierPattern(models.Model):
    auto_id = models.BigAutoField(primary_key=True)
    pattern = models.CharField(max_length=50, help_text="Regex pattern to extract details from barcode")
    defaults = models.JSONField(help_text="default/constant identity values - used if not extracted by pattern")
    label = models.CharField(max_length=50, help_text="label describing what this pattern is for")
    identifier_type = models.ForeignKey(IdentifierType, on_delete=models.CASCADE, related_name="patterns")
    id_type = models.ForeignKey(IdentityType, on_delete=models.CASCADE, related_name="patterns")
