from django.db import transaction
from .models import Edge, Event, Node
from enum import Enum
import dateutil.parser

# TODO: Error on performing individual transfer against collection and vice versa
# TODO: check event timestamp is not before record's start time
##  Move to DB managed timestamps??

class TransferType(Enum):
    INDIVIDUAL = 1
    COLLECTION = 2

def do_transfer(raw_msg):
    # validate message - will throw exception if required keys not present
    timestamp = dateutil.parser.isoparse(raw_msg['timestamp'])
    loc_link_from = raw_msg.get('from',None)
    loc_link_to = raw_msg['to']
    item_id = raw_msg['item']
    quantity = raw_msg.get('quantity',None)

    if loc_link_from == loc_link_to:
        return

    child = Node.objects.find_or_make(item_id)
    from_parent = Node.objects.find_or_make(loc_link_from)
    to_parent = Node.objects.find_or_make(loc_link_to)

    # log event
    event = Event(
        child=child,
        from_parent=from_parent,
        to_parent=to_parent,
        quantity=quantity,
        timestamp=timestamp,
    )

    # check item individual or collection?
    if event.quantity is not None and event.from_parent is not None:  
        fromState, toState = do_collection_transfer(event)
        result = TransferType.COLLECTION, fromState, toState
    else:
        oldState, newState = do_individual_transfer(event)
        result = TransferType.INDIVIDUAL, oldState, newState

    event.save()
    return result


def do_collection_transfer(event):
    with transaction.atomic():
        try:

            prevFromState = Edge.objects.get(parent=event.from_parent,child=event.child,end__isnull=True)
            prevFromState.end = event.timestamp
            prevFromQuantity = prevFromState.quantity
            prevFromState.save()
        except Edge.DoesNotExist:
            prevFromQuantity=0

        # can check quantity rather than deliberate exception on single tracked
        try:
            prevToState = Edge.objects.get(
                parent=event.to_parent, child=event.child, end__isnull=True
            )
            prevToState.end = event.timestamp
            prevToQuantity=prevToState.quantity
            prevToState.save()
        except Edge.DoesNotExist:
            prevToQuantity=0

        newToQuantity = increment_quantity(prevToQuantity,event.quantity)
        newFromQuantity = decrement_quantity(prevFromQuantity,event.quantity)

        print(f"{event.from_parent}:{prevFromQuantity}>{newFromQuantity},{event.to_parent}:{prevToQuantity}>{newToQuantity}")

        newToState = Edge(
            child=event.child,
            parent=event.to_parent,
            start=event.timestamp,
            quantity=newToQuantity,
        )
        newFromState = Edge(
            child=event.child,
            parent=event.from_parent,
            start=event.timestamp,
            quantity=newFromQuantity,
        )

        # only save if there is a non-zero value
        if newToQuantity != 0:
            newToState.save()
        if newFromQuantity != 0:
            newFromState.save()

        return newFromState, newToState

def do_individual_transfer(event):
    with transaction.atomic():
        try:
            prevState = Edge.objects.get(child=event.child,end__isnull=True)

            event.from_parent = prevState.parent

            if prevState.parent == event.to_parent:
                return None, prevState

            prevState.end = event.timestamp
            prevState.save()

        except Edge.DoesNotExist:
            prevState = None

        newState = Edge.objects.create(
            child=event.child,
            parent=event.to_parent,
            start=event.timestamp,
        )
        return prevState, newState


## Utils:
def increment_quantity(base,amount):
    if base is None:
        return amount
    if amount is None:
        return base
    return base + amount

def decrement_quantity(base,amount):
    if base is None:
        return -1 * amount
    if amount is None:
        return base
    return base - amount
