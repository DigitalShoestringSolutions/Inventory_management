import datetime

MQTT = {
        'broker':'mqtt.docker.local',
        'port':1883,
        'id':'locations_db',
        'sub_topics':[]
    }

DELETE_ON_COMPLETE=True
DELETE_THRESHOLD = datetime.timedelta(days=0)


