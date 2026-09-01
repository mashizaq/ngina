import threading
import queue
import time
import json
import os
import logging
from paho.mqtt import client as mqtt_client

logger = logging.getLogger('ngina.mqtt')
logger.setLevel(logging.INFO)


class MqttPublisher:
    def __init__(self, app=None):
        self._client = None
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._stop = threading.Event()
        if app:
            self.init_app(app)

    def init_app(self, app):
        self._mqtt_url = os.getenv('MQTT_URL', app.config.get('MQTT_URL', 'mqtt://mosquitto:1883'))
        self._mqtt_user = os.getenv('MQTT_USER', app.config.get('MQTT_USER'))
        self._mqtt_pass = os.getenv('MQTT_PASS', app.config.get('MQTT_PASS'))
        # start worker
        self._thread.start()

    def _connect_client(self):
        import urllib.parse
        parsed = urllib.parse.urlparse(self._mqtt_url)
        host = parsed.hostname or 'mosquitto'
        port = parsed.port or 1883
        client_id = f'ngina-py-pub-{int(time.time())}'
        client = mqtt_client.Client(client_id)
        if self._mqtt_user and self._mqtt_pass:
            client.username_pw_set(self._mqtt_user, self._mqtt_pass)
        try:
            client.connect(host, port)
            client.loop_start()
            logger.info('MQTT connected to %s:%s', host, port)
            return client
        except Exception as e:
            logger.error('MQTT connect failed: %s', e)
            return None

    def publish(self, topic, message):
        payload = json.dumps({**message, 'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())})
        self._queue.put((topic, payload))

    def _worker(self):
        while not self._stop.is_set():
            try:
                if not self._client:
                    self._client = self._connect_client()
                try:
                    topic, payload = self._queue.get(timeout=1)
                except queue.Empty:
                    time.sleep(0.1)
                    continue
                if not self._client:
                    # requeue and wait
                    self._queue.put((topic, payload))
                    time.sleep(2)
                    continue
                # publish
                def on_publish(client, userdata, mid):
                    logger.debug('published %s', mid)

                self._client.publish(topic, payload, qos=1)
            except Exception as e:
                logger.exception('mqtt worker error: %s', e)
                time.sleep(2)

    def stop(self):
        self._stop.set()
        if self._client:
            try:
                self._client.loop_stop()
                self._client.disconnect()
            except Exception:
                pass
