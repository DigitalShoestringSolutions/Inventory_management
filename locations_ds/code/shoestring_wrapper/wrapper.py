import threading
import socket
import paho.mqtt.client as mqtt
import asyncio
import requests
import json
import zmq
from zmq.asyncio import Context

ctx = Context.instance()


class MQTTMonitorThread(threading.Thread):
    def __init__(self,mqtt_config, zmq_config):
        threading.Thread.__init__(self)
        self.name = mqtt_config['id']
        self.topics = mqtt_config.get('sub_topics',[])
        self.mqtt_config = mqtt_config
        self.zmq_config = zmq_config

    def run(self):
        print("Starting " + self.name)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.run_until_complete(AsyncMqttLoop(self.name, loop, self.mqtt_config, self.zmq_config, self.topics).run())
        loop.close()
        print("Exiting " + self.name)


class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        print("MQTT> Socket opened")

        def cb():
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        print("MQTT> Socket closed")
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        print("MQTT> Watching socket for writability.")

        def cb():
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        print("MQTT> Stop watching socket for writability.")
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break


class AsyncMqttLoop:
    def __init__(self, client_id, loop, mqtt_config, zmq_config, topics=[]):
        self.client_id = client_id
        self.loop = loop
        self.mqtt_config = mqtt_config
        self.zmq_config = zmq_config
        self.initial_topics = topics

    def on_connect(self, client, userdata, flags, rc):
        print(
            "MQTT> {id}: subscribing to initial topics: {topics}".format(id=self.client_id, topics=self.initial_topics))
        for topic in self.initial_topics:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        if not self.got_message:
            print("MQTT> {id}: Got unexpected message: {msg}".format(id=self.client_id, msg=msg.decode()))
        else:
            self.got_message.set_result(msg)

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def run(self):
        self.disconnected = self.loop.create_future()

        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        aioh = AsyncioHelper(self.loop, self.client)

        # self.client.tls_set('ca.cert.pem',tls_version=2)
        self.client.connect(self.mqtt_config['broker'], self.mqtt_config['port'], 60)

        t1 = asyncio.create_task(self.check_inbound())
        t2 = asyncio.create_task(self.check_outbound())
        await asyncio.gather(t1)
        await asyncio.gather(t2)
        self.client.disconnect()
        print("MQTT> Disconnected: {}".format(await self.disconnected))

    async def check_inbound(self):
        self.got_message = self.loop.create_future()
        pub_socket = ctx.socket(zmq.PUB)
        pub_socket.bind(self.zmq_config['pub_ep'])
        while True:
            msg = await self.got_message
            print("MQTT> {id}: Got msg: {msg} on topic {topic}".format(msg=msg.payload, id=self.client_id,
                                                                       topic=msg.topic))
            zmq_msg = [self.zmq_config['inbound_topic'].encode(), msg.topic.encode(), msg.payload]

            await pub_socket.send_multipart(zmq_msg)
            self.got_message = self.loop.create_future()

    async def check_outbound(self):
        pull_socket = ctx.socket(zmq.PULL)
        pull_socket.bind(self.zmq_config['sub_ep'])
        while True:
            print("wrapper >> zmq waiting...")
            msg = await pull_socket.recv_multipart()
            print("wrapper got", msg)
            json_msg = json.loads(msg[-1])
            topic = msg[-2].decode()
            print("MQTT> {id}: Sending {msg} on topic {topic}".format(msg=json_msg, id=self.client_id, topic=topic))
            self.client.publish(topic, json.dumps(json_msg))


class Wrapper:
    inst = None;

    def __init__(self):
        self.addr_map = {

        }

    @classmethod
    def get(cls):
        if cls.inst == None:
            cls.inst = cls()
        return cls.inst

    @classmethod
    def start(cls, args):
        print("Shoestring Wrapper Starting")
        self = cls.get()
        t = MQTTMonitorThread(args['mqtt_config'], args['zmq_config'])
        t.start()

    def request(self, endpoint):
        service_id, path = endpoint.split("/", 1)
        host = self.get_addr(service_id)
        url = f"http://{host}/{path}"
        response = requests.get(url)
        return response.json()

    def subscribe_to(self):
        pass

    def publish(self):
        pass

    def get_addr(self, service_id):
        return self.addr_map[service_id]
