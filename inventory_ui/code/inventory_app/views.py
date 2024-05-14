from django.shortcuts import render, redirect, get_object_or_404
from .forms import CreateItemForm
from .models import InventoryItem, OrderItem
from django.http import JsonResponse
from django.http import HttpResponse
from io import BytesIO
from openpyxl import Workbook
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import F, ExpressionWrapper, fields
from django.db import transaction
from django.db.models import Count, Case, When, IntegerField, Sum, Max, Avg, F
from django.db.models.functions import Coalesce
import datetime
import dateutil.parser
import requests
from . import utils


def home(request):
    items = get_all_items()

    # items_on_order = OrderItem.objects.filter(on_order__gt=0).count()
    items_on_order = OrderItem.objects.filter(on_order__gt=0, completed=False).count()

    (
        items_below_minimum,
        items_5_more_than_minimum,
        items_greater_than_5_more_than_minimum,
    ) = get_stock_alert_data(items)

    below_minimum_counts, below_minimum_locations = (
        get_items_below_location_threshold_data()
    )

    context = {
        "items": items,
        "items_on_order": items_on_order,
        "items_below_minimum": items_below_minimum,
        "items_5_more_than_minimum": items_5_more_than_minimum,
        "items_greater_than_5_more_than_minimum": items_greater_than_5_more_than_minimum,
        "below_minimum_locations": below_minimum_locations,
        "below_threshold_counts": below_minimum_counts,
    }

    return render(request, "inventory_app/home.html", context)


def analyze(request):
    items = fetch_all_items()  # Retrieve all inventory items

    # items_on_order = OrderItem.objects.filter(on_order__gt=0).count()
    items_on_order = OrderItem.objects.filter(on_order__gt=0, completed=False).count()

    (
        items_below_minimum,
        items_5_more_than_minimum,
        items_greater_than_5_more_than_minimum,
    ) = get_stock_alert_data(items)

    below_minimum_counts, below_minimum_locations = (
        get_items_below_location_threshold_data()
    )

    ##########################################
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    # Query to get the total units withdrawn for each item in the last week, then order by the total and take the top 5
    top_withdrawals = (
        ItemWithdrawal.objects.filter(date_withdrawn__gte=one_week_ago)
        .values("item__item")
        .annotate(total_withdrawn=Sum("units_withdrawn"))
        .order_by("-total_withdrawn")[:5]
    )

    items_labels = [withdrawal["item__item"] for withdrawal in top_withdrawals]
    withdrawals_data = [withdrawal["total_withdrawn"] for withdrawal in top_withdrawals]

    ##########################################
    # Query to calculate lead time and get the top 5 items with the longest lead times
    # top_lead_times = OrderItem.objects.annotate(
    #     lead_time=ExpressionWrapper(F('order_lead_time') - F('oracle_order_date'), output_field=fields.DurationField())
    # ).order_by('-lead_time')[:5]

    # items_lead_time_labels = [item.item.item for item in top_lead_times]  # Adjust based on your model's structure
    #    = [item.lead_time.days for item in top_lead_times]
    top_lead_times = (
        OrderItem.objects.annotate(
            lead_time=ExpressionWrapper(
                F("order_lead_time") - F("oracle_order_date"),
                output_field=fields.DurationField(),
            )
        )
        .values("item__item")
        .annotate(max_lead_time=Max("lead_time"))
        .order_by("-max_lead_time")[:5]
    )

    items_lead_time_labels = [item["item__item"] for item in top_lead_times]
    lead_times = [
        item["max_lead_time"].days for item in top_lead_times
    ]  # Extracting days from lead time

    ####################EXPERIMENTAL FORECASTING######################

    # Calculate one week ago from now
    one_week_ago = timezone.now() - timezone.timedelta(days=7)

    # Get the average daily withdrawal rate for each item over the last week
    avg_withdrawals_per_item = (
        ItemWithdrawal.objects.filter(date_withdrawn__gte=one_week_ago)
        .values("item_id")
        .annotate(avg_daily_withdrawn=Avg("units_withdrawn"))
    )

    # Convert to a dictionary for easier access
    avg_withdrawals_dict = {
        withdrawal["item_id"]: withdrawal["avg_daily_withdrawn"]
        for withdrawal in avg_withdrawals_per_item
    }

    # For each inventory item, calculate net stock and estimate days until stock runs out
    items_forecast = []
    for item in InventoryItem.objects.all():
        item_id = item.id
        total_on_order = OrderItem.objects.filter(
            item_id=item_id, completed=False
        ).aggregate(total_on_order=Coalesce(Sum("on_order"), 0))["total_on_order"]

        net_stock = item.unit - total_on_order
        avg_daily_withdrawn = avg_withdrawals_dict.get(item_id, 0)
        # net_stock = item.unit - OrderItem.objects.filter(item_id=item_id, completed=False).aggregate(total_on_order=Sum('on_order'))['total_on_order'] or 0

        # Avoid division by zero
        days_until_out = (
            (net_stock / avg_daily_withdrawn) if avg_daily_withdrawn else float("inf")
        )

        items_forecast.append(
            {
                "item": item,
                "net_stock": net_stock,
                "avg_daily_withdrawn": avg_daily_withdrawn,
                "days_until_out": days_until_out,
            }
        )
        print(items_forecast)

    context = {
        "items": items,
        "items_on_order": items_on_order,
        "items_below_minimum": items_below_minimum,
        "items_5_more_than_minimum": items_5_more_than_minimum,
        "items_greater_than_5_more_than_minimum": items_greater_than_5_more_than_minimum,
        "below_minimum_locations": below_minimum_locations,
        "below_threshold_counts": below_minimum_counts,
        "items_labels": items_labels,
        "withdrawals_data": withdrawals_data,
        "items_lead_time_labels": items_lead_time_labels,
        "lead_times": lead_times,
        "items_forecast": items_forecast,
    }

    return render(request, "inventory_app/analyze.html", context)


def user(request):  # this is the base withdrawl page
    list_of_available_items = fetch_item_list()
    print(list_of_available_items)
    return render(
        request, "inventory_app/user.html", {"items": list_of_available_items}
    )


def order(request):
    items = fetch_item_list()
    orders = OrderItem.objects.all()
    return render(
        request, "inventory_app/order.html", {"items": items, "orders": orders}
    )


def track(request):
    raw_withdrawals = fetch_all_withdrawls()
    withdrawals = [
        {
            "item": utils.get_item_name(entry["child"]),
            "location": utils.get_location_name(entry["from_parent"]),
            "date_withdrawn": dateutil.parser.isoparse(entry["timestamp"]).strftime(
                "%d %b %Y %H:%M"
            ),
            "units_withdrawn": entry["quantity"],
            "withdrawn_by": entry["to_parent"].split("@")[
                -1
            ],  # TODO: maybe do properly with ID in ID manager
        }
        for entry in raw_withdrawals
    ]

    return render(request, "inventory_app/track.html", {"withdrawals": withdrawals})


def admin_view(request):
    # Initialize forms outside of the if block to ensure they are available in the entire function scope
    add_form = CreateItemForm()
    # update_form = StockUpdateForm()

    if request.method == "POST":
        if "add" in request.POST:  # If the add operation is requested
            add_form = CreateItemForm(request.POST)  # Reinitialize with posted data
            if add_form.is_valid():
                # print(add_form.data)
                create_new_item(add_form.data['item_name'],add_form.data['quantity_per_unit'],add_form.data['minimum_unit'])
                return redirect("admin_view")  # Redirect to avoid double posting
        # No longer used
        # elif "update" in request.POST:  # If the update operation is requested
        #     update_form = StockUpdateForm(request.POST)  # Reinitialize with posted data
        #     if update_form.is_valid():
        #         # update_form.save()
        #         print(update_form.data)
        #         return redirect("admin_view")  # Redirect to avoid double posting

    raw_items = get_all_items()  # Fetch items regardless of POST or GET request

    inv_items = InventoryItem.objects.all()
    # group by item_id
    grouped_items = {}
    for item in raw_items:
        item_id = item["child"]

        if item_id not in grouped_items:
            grouped_items[item_id] = {"total": 0, "locations": [], "name":item['name']}

            found_inv_items = inv_items.filter(item=item_id)
            if len(found_inv_items) >0:
                inv_item = found_inv_items[0]
                grouped_items[item_id]["quantity_per_unit"] = inv_item.quantity_per_unit
                grouped_items[item_id]["minimum_unit"] = inv_item.minimum_unit

        grouped_items[item_id]["total"] += item["quantity"] if item["quantity"] else 0
        grouped_items[item_id]["locations"].append(item["location"])

    processed_items = [
        {
            "id": item_id,
            "item": entry["name"],
            "locations": ",\n".join(entry["locations"]),
            "unit": entry["total"],
            "quantity_per_unit": entry["quantity_per_unit"],
            "minimum_unit": entry["minimum_unit"],
        }
        for (item_id, entry) in grouped_items.items()
    ]
    # <td>{{ item.id }}</td>
    #                 <td>{{ item.item }}</td>
    #                 <td>{{ item.locations }}</td>
    #                 <td>{{ item.supplier }}</td>
    #                 <td>{{ item.quantity_per_unit }}</td>
    #                 <td>{{ item.unit }}</td>
    #                 <td>{{ item.minimum_unit }}</td>
    #                 <td>{{ item.cost }}</td>
    return render(
        request,
        "inventory_app/adminpage.html",
        # {"update_form": update_form, "add_form": add_form, "items": processed_items},
        {"add_form": add_form, "items": processed_items},
    )


def get_item_details(request, item_id):
    # TODO: work out if still needed
    item = InventoryItem.objects.filter(pk=item_id).first()
    if item:
        data = {
            # "supplier": item.suppliers.name if item.supplier else "",
            # "units": 10,  # item.unit,
            "minimum_units": item.minimum_unit,
            # "cost": 1,#item.cost,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Item not found"}, status=404)


def submit_withdrawal(request):
    if request.method == "POST":
        item_id = request.POST.get("item")
        location_id = request.POST.get("location")
        units_withdrawn = int(request.POST.get("units_withdrawn"))
        withdrawn_by = request.POST.get("withdrawn_by")

        # TODO: handle errors
        make_transfer(item_id, location_id, f"person@{withdrawn_by}", units_withdrawn)

        messages.success(request, "Successfully recorded.")
        items = InventoryItem.objects.all().order_by("item")  # TODO

        return render(request, "inventory_app/user.html", {"items": items})
    else:
        return HttpResponse("Invalid request", status=400)


def download_stock_report(request):
    # Fetch data
    data = [
        (entry["name"], entry["location"], entry["quantity"], entry["start"])
        for entry in get_all_items()
    ]  # This fetches all Stock items as tuples

    data.insert(0, ("Item", "Location", "Quantity", "Last Update"))

    # Create a workbook
    wb = Workbook()
    ws = wb.active

    # Write data to worksheet
    for row in data:
        ws.append(row)

    # Save the workbook to a virtual file
    virtual_workbook = BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)

    # Build the response
    response = HttpResponse(
        virtual_workbook.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="stock_report.xlsx"'

    return response


# This doesn't seem to be used
# def track_withdrawals(request):
#     unique_withdrawn_by = (
#         ItemWithdrawal.objects.order_by("withdrawn_by")
#         .values_list("withdrawn_by", flat=True)
#         .distinct()
#     )
#     unique_items = InventoryItem.objects.order_by("item").distinct()
#     selected_items = request.GET.getlist("item")  # Fetch selected items from request

#     if request.method == "GET":
#         withdrawn_by = request.GET.get("withdrawn_by")
#         selected_items = request.GET.getlist(
#             "item"
#         )  # This method handles multiple values for 'item'

#         if withdrawn_by and withdrawn_by != "All":
#             withdrawals = withdrawals.filter(withdrawn_by__icontains=withdrawn_by)
#         if selected_items:
#             withdrawals = withdrawals.filter(item__item__in=selected_items)

#         # For CSV export
#         if "export" in request.GET:
#             response = HttpResponse(
#                 content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#             )
#             response["Content-Disposition"] = 'attachment; filename="withdrawals.xlsx"'

#             wb = Workbook()
#             ws = wb.active
#             ws.append(["Item", "Date Withdrawn", "Units Withdrawn", "Withdrawn By"])

#             for withdrawal in withdrawals:
#                 ws.append(
#                     [
#                         withdrawal.item.item,
#                         withdrawal.date_withdrawn.strftime("%Y-%m-%d %H:%M"),
#                         withdrawal.units_withdrawn,
#                         withdrawal.withdrawn_by,
#                     ]
#                 )

#             virtual_workbook = BytesIO()
#             wb.save(virtual_workbook)
#             virtual_workbook.seek(0)
#             response.write(virtual_workbook.getvalue())
#             return response

#     return render(
#         request,
#         "inventory_app/track.html",
#         {
#             "unique_withdrawn_by": unique_withdrawn_by,
#             "unique_items": unique_items,
#             "withdrawals": withdrawals,
#             "selected_items": selected_items,
#         },
#     )


def get_locations_for_item(request, item_id):
    print(f"get for {item_id}")
    raw_item_locations = fetch_item_locations(item_id)
    simplified_item_locations = [
        {
            "id": entry["parent"],
            "name": utils.get_location_name(entry["parent"]),
            "quantity": entry["quantity"],
        }
        for entry in raw_item_locations
    ]

    return JsonResponse(simplified_item_locations, safe=False)


def order_view(request):
    if request.method == "POST":
        item_id = request.POST.get("item")
        location_id = request.POST.get(
            "location"
        )  # This will be the ID of the location
        supplier = request.POST.get("supplier")
        units = request.POST.get("units")
        minimum_units = request.POST.get("minimum_units")
        cost = request.POST.get("cost")
        unit_ord = request.POST.get("unit_ord")
        request_date = request.POST.get("request_date")
        requested_by = request.POST.get("requested_by")
        oracle_order_date = request.POST.get("oracle_order_date")
        oracle_po = request.POST.get("oracle_po")
        order_lead_time = request.POST.get("order_lead_time")

        item = get_object_or_404(InventoryItem, id=item_id)
        location = get_object_or_404(
            Location, id=location_id
        )  # Fetch the Location instance

        # Record the order item
        OrderItem.objects.create(
            item=item,
            location=location,  # Use the Location instance here
            supplier=supplier,
            on_order=int(unit_ord),
            quantity_per_unit=units,
            unit=int(units),  # Assuming 'units' refers to 'unit' here; adjust if needed
            minimum_unit=int(minimum_units),
            cost=cost,  # Make sure to convert the string to a Decimal
            request_date=request_date,
            requested_by=requested_by,
            oracle_order_date=oracle_order_date,
            oracle_po=oracle_po,
            order_lead_time=order_lead_time,
        )

        messages.success(request, "Order successfully recorded.")
        items = InventoryItem.objects.all().order_by("item")
        orders = OrderItem.objects.all().order_by("item")

        return render(
            request, "inventory_app/order.html", {"items": items, "orders": orders}
        )
    else:
        return HttpResponse("Invalid request", status=400)


def consolidate_stock(request, order_id):
    if request.method == "POST":
        order_item = get_object_or_404(OrderItem, id=order_id)
        inventory_item = (
            order_item.item
        )  # Assuming 'item' is a ForeignKey to InventoryItem

        # TODO:
        make_transfer(
            inventory_item.pk,
            f"supplier@{order_item.supplier}",
            "InboundGoods",
            order_item.on_order,
        )
        if not order_item.completed:
            inventory_item.unit += order_item.on_order
            inventory_item.save()
            order_item.completed = True
            order_item.save()
            return JsonResponse(
                {"success": True, "message": "Stock consolidated successfully."}
            )
        else:
            return JsonResponse(
                {"success": False, "message": "Order already completed."}
            )
    return JsonResponse({"success": False, "message": "Invalid request"})


##############
# Common DB Operations
##############


def create_new_item(name, quantity_per_unit, minimum_unit):
    identity = create_new_id(name)
    InventoryItem.objects.create(
        item=identity["id"], quantity_per_unit=quantity_per_unit, minimum_unit=minimum_unit
    )


def add_new_stock(id, supplier_name, quantity):
    make_transfer(
        id,
        f"supplier@{supplier_name}",
        "loc@inbound",
        quantity,
    )


def get_stock_alert_data(items):
    items_below_minimum = 0
    items_5_more_than_minimum = 0
    items_greater_than_5_more_than_minimum = 0

    # group py item_id
    grouped_totals = {}
    for item in items:
        item_id = item["child"]
        if item_id not in grouped_totals:
            grouped_totals[item_id] = 0
        grouped_totals[item_id] += item["quantity"] if item["quantity"] else 0

    for item_id, total in grouped_totals.items():
        # find InventoryItem for item_id
        inv_item = InventoryItem.objects.get(item=item_id)
        # get minimum_unit
        minimum_unit = inv_item.minimum_unit
        # compare to total for that item
        if total < minimum_unit:
            items_below_minimum += 1
        elif total == minimum_unit + 5:
            items_5_more_than_minimum += 1
        elif total > minimum_unit + 5:
            items_greater_than_5_more_than_minimum += 1

    return (
        items_below_minimum,
        items_5_more_than_minimum,
        items_greater_than_5_more_than_minimum,
    )


def get_items_below_location_threshold_data():
    # items_below_minimum_by_location = (
    #     InventoryItem.objects.annotate(
    #         below_minimum=Case(
    #             When(unit__lt=F("minimum_unit"), then=1),
    #             default=0,
    #             output_field=IntegerField(),
    #         )
    #     )
    #     .values("location__name")
    #     .annotate(total_below_minimum=Sum("below_minimum"))
    #     .order_by("location__name")
    # )

    below_minimum_locations = [
        # item["location__name"] for item in items_below_minimum_by_location
    ]
    below_minimum_counts = [
        # item["total_below_minimum"] for item in items_below_minimum_by_location
    ]

    return below_minimum_counts, below_minimum_locations


### Layered functions
def get_all_items():
    items_by_location = fetch_all_items()
    # add names
    for item in items_by_location:
        item["name"] = utils.get_item_name(item["child"])
        item["location"] = utils.get_item_name(item["parent"])
    return items_by_location


### Location DS utils:
def make_transfer(item, from_loc, to_loc, quantity):
    payload = {
        "item": str(item),
        "from": str(from_loc),
        "to": str(to_loc),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "quantity": quantity,
    }
    url = "locations-ds.docker.local"  # TODO: move to settings.py
    resp = requests.post(f"http://{url}/action/transfer", json=payload)
    return resp.json()


def fetch_item_locations(item_id):
    url = "locations-ds.docker.local"  # TODO: move to settings.py
    resp = requests.get(f"http://{url}/state/for/{item_id}/at/loc@")
    return resp.json()


def fetch_all_items():
    url = "locations-ds.docker.local"  # TODO: move to settings.py
    resp = requests.get(f"http://{url}/state/for/item@/at/loc@")
    return resp.json()


def fetch_item_list():
    url = "identity-ds.docker.local"  # TODO: move to settings.py
    resp = requests.get(f"http://{url}/id/list/item")
    return resp.json()


def fetch_all_withdrawls():
    url = "locations-ds.docker.local"  # TODO: move to settings.py
    resp = requests.get(f"http://{url}/events/from/loc@")
    return resp.json()


def create_new_id(name):
    payload = {"name": str(name), "type": "item"}
    url = "identity-ds.docker.local"  # TODO: move to settings.py
    resp = requests.post(f"http://{url}/id/create", json=payload)
    return resp.json()
