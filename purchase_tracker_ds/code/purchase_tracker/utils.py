import requests
from functools import lru_cache
from django.conf import settings
import datetime


### Identity DS utils
def get_name(id):
    try:
        result = do_get_identity(id)
        return result["name"]
    except:
        return "<unable to fetch name>"


# cached fetch operations (will only make the request over the network once for each ID)
@lru_cache  # can add a max_size
def do_get_identity(id):
    url = settings.IDENTITY_PROVIDER_URL 
    resp = requests.get(f"http://{url}/id/{id}")
    if resp.status_code != 200:
        raise ValueError(
            {
                "error": "Couldn't get identity",
                "status": resp.status_code,
                "message": resp.json(),
            }
        )
    return resp.json()


def create_new_supplier_identity(name):
    payload = {"name": str(name), "type": "supplier"}
    url = settings.IDENTITY_PROVIDER_URL
    resp = requests.post(f"http://{url}/id/create", json=payload)
    return resp.status_code, resp.json()


def make_transfer(item, from_loc, to_loc, quantity):
    payload = {
        "item": str(item),
        "from": str(from_loc),
        "to": str(to_loc),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "quantity": quantity,
    }
    url = settings.LOCATION_DS_URL
    resp = requests.post(f"http://{url}/action/transfer", json=payload)
    return resp.json()
