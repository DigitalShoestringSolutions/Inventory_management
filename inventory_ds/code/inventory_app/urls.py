from django.urls import path
from . import views

urlpatterns = [
    ##
    ## /state/ -- Current Inventory State
    ##
    # current state grouped by item - for display to user
    path("state/by-items", views.state_items),
    # current state grouped by item with extra details useful for inventory manager
    path("state/by-items/detailed", views.state_items_detailed),
    # current state grouped by inventory location
    path("state/by-locations", views.state_locations),
    ##
    ## /list/ -- List what's available (id and name)
    ##
    # all known locations
    path("list/locations", views.list_locations),
    # all locations where specified item is present
    path("list/locations/for/<str:item_id>",views.list_locations_for_item),
    # all known items
    path("list/items",views.list_items),
    # all items present at specified location
    path("list/items/at/<str:location_id>",views.list_items_at_location),
    # all items that exist but aren't registered with inventory
    path("list/items/unregistered"),
    ##
    ## /action/ -- Actions that can be performed
    ##
    # withdraw items from a location
    path("action/withdraw"),
    # transfer items from one location to another
    path("action/transfer"),
    # replenish stock from a recieved delivery
    path("action/replenish"),
    # create a new order
    path("action/order"),
    ##
    ## /summary/ -- Summary / Insights about inventory control
    ##
    # overall stock levels vs minimum levels
    path("summary/levels"),
    # stock levels vs minimum levels by location
    path("summary/levels/by-location"),
    # average number of withdrawals for each item in a given period
    path("summary/rate/withdrawals"),  # ?from=<from>&to=<to>
    # average number of transfers for each item in a given period
    path("summary/rate/transfers"),  # ?from=<from>&to=<to>
    # summary of the quantities of items on order
    path("summary/on-order"),
    # summary of the estimated time till re-order will be required for items
    path("summary/time-till-order"),
]
