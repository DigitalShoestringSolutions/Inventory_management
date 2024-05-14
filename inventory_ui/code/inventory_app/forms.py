from django import forms
from . import models
from django.forms.widgets import TextInput, NumberInput, DateTimeInput, DateInput

# No longer used I believe
# class StockUpdateForm(forms.ModelForm):
#     item_name = forms.CharField(label="Item Name", max_length=40)
#     class Meta:
#         model = models.InventoryItem
#         fields = ["item", "item_name", "quantity_per_unit", "minimum_unit"]

#         widgets = {
#             "minimum_unit": NumberInput(attrs={"step": "1"}),
#             "item_name": TextInput(attrs={"type": "text"}),
#             "quantity_per_unit": TextInput(attrs={"type": "text"}),
#             "supplier_link": TextInput(attrs={"type": "text"}),
#         }


class CreateItemForm(forms.ModelForm):
    item_name = forms.CharField(label="Item Name",max_length=40)
    class Meta:
        model = models.InventoryItem

        fields = ["item_name","quantity_per_unit", "minimum_unit"]

        widgets = {
            "item_name": TextInput(attrs={"type": "text"}),
            "minimum_unit": NumberInput(attrs={"step": "1"}),
            "quantity_per_unit": TextInput(attrs={"type": "text"}),
        }

# No longer used I believe
# class OrderForm(forms.ModelForm):
#     # location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
#     class Meta:
#         model = models.InventoryItem
#         # fields = ['item', 'location', 'supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost']
#         fields = ["item", "quantity_per_unit", "minimum_unit"]

#         widgets = {
#             # 'unit': NumberInput(attrs={'step': "1"}),
#             'minimum_unit': NumberInput(attrs={'step': "1"}),
#             # 'cost': NumberInput(attrs={'step': "0.01"}),  # Consider allowing decimal steps for cost
#             'item': TextInput(attrs={'type': 'text'}),
#             # 'location': TextInput(attrs={'type': 'text'}),
#             # 'supplier': TextInput(attrs={'type': 'text'}),  # Added missing field
#             'quantity_per_unit': TextInput(attrs={'type': 'text'}),
#         }

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = InventoryItem
#         fields = ['item', 'supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost', 'request_date',
#          'requested_by', 'oracle_order_date', 'oracle_ordered_by', 'oracle_po', 'order_lead_time', 'supplier_link']

#         widgets = {
#             'request_date': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'oracle_order_date': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'order_lead_time': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'unit': NumberInput(attrs={'step': "1"}),  # Adjust step for appropriate increments
#             'minimum_unit': NumberInput(attrs={'step': "1"}),
#             'cost': NumberInput(attrs={'step': "1"}),
#             'item': TextInput(attrs={'type': 'text'}),
#             'supplier': TextInput(attrs={'type': 'text'}),
#             'quantity_per_unit': TextInput(attrs={'type': 'text'}),
#             'oracle_ordered_by': TextInput(attrs={'type': 'text'}),
#             'oracle_po': TextInput(attrs={'type': 'text'}),
#             'requested_by': TextInput(attrs={'type': 'text'}),
#             'supplier_link': TextInput(attrs={'type': 'text'}),
#         }
