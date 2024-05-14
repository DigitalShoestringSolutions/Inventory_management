import requests
from functools import lru_cache

### Identity DS utils
def get_location_name(id):
    try:
        return do_get_name(id)
    except:
        return "<unable to fetch name>"


def get_item_name(id):
    try:
        return do_get_name(id)
    except:
        return "<unable to fetch name>"


# cached fetch operations (will only make the request over the network once for each ID)
@lru_cache  # can add a max_size
def do_get_name(id):
    # TODO: move to settings.py
    url = "identity-ds.docker.local"
    resp = requests.get(f"http://{url}/id/{id}")
    return resp.json()[0]["name"]

