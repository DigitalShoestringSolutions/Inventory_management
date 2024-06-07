import zmq
import json
import threading
from state.actions import TransferType, do_transfer

context = zmq.Context()

class StateModel:
    def __init__(self,zmq_config):
        self.subsocket = context.socket(zmq.SUB)
        self.subsocket.connect(zmq_config['pub_ep'])
        self.subsocket.setsockopt(zmq.SUBSCRIBE, zmq_config['inbound_topic'].encode())

        self.pushsocket = context.socket(zmq.PUSH)
        self.pushsocket.connect(zmq_config['sub_ep'])


    def start(self):
        t = threading.Thread(target = self.run)
        t.start()

    def run(self):
        while True:
            msg = self.subsocket.recv_multipart()
            print("StateModel got:",msg)
            try:
                topic = msg[-2].decode().split('/')
                json_msg = json.loads(msg[-1])
                self.handle_message(json_msg)
            except Exception as e:
                print("ERROR")
                print(e.msg)

    def handle_message(self,raw_msg):
        print(f"handling: {raw_msg}")
        #listen for incoming events
        try:
            transfer_type, *states =  do_transfer(raw_msg)
            
            output = []
            if transfer_type == TransferType.INDIVIDUAL:
                output = handle_individual_update(*states)
            elif transfer_type == TransferType.COLLECTION:
                output = handle_collection_update(*states)

            #send update
            for msg in output:
                self.pushsocket.send_multipart([msg["topic"].encode(),json.dumps(msg["payload"]).encode()])

        except Exception as e:
            print("ERROR")
            print (e)

def handle_collection_update(newFromState, newToState):
    output_messages = []
    
    #send update event
    to_update_msg = {
            'item_id':newToState.item_id,
            'location_link':newToState.location_link,
            'timestamp':newToState.start.isoformat(),
            'quantity':newToState.quantity
            }

    print(to_update_msg)
    output_messages.append({"topic":"location_state/update/"+to_update_msg['location_link'],"payload":to_update_msg})

        
    from_update_msg = {
        'item_id':newFromState.item_id,
        'location_link':newFromState.location_link,
        'timestamp':newFromState.start.isoformat(),
        'quantity':newFromState.quantity
        }
    
    print(from_update_msg)
    output_messages.append({"topic":"location_state/update/"+from_update_msg['location_link'],"payload":from_update_msg})

    return output_messages

def handle_individual_update(prevState, newState):
    output_messages = []
    
    if prevState is not None:
        exited_msg = {
            'item_id':prevState.item_id,
            'location_link':prevState.location_link,
            'timestamp':prevState.end.isoformat(),
            'event':'exited'
            }

        print(exited_msg)
        output_messages.append({"topic":"location_state/exited/"+exited_msg['location_link'],"payload":exited_msg})

    entered_msg = {
        'item_id':newState.item_id,
        'location_link':newState.location_link,
        'timestamp':newState.start.isoformat(),
        'event':'entered'
        }

    print(entered_msg)
    #send update
    output_messages.append({"topic":"location_state/entered/"+entered_msg['location_link'],"payload":entered_msg})

    return output_messages

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
