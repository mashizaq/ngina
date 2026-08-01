import mqtt from 'mqtt';
import { MqttEventPublisher } from './event-bus/mqtt-event-publisher';

const MQTT_URL = process.env.MQTT_URL || 'mqtt://mosquitto:1883';
const MQTT_USER = process.env.MQTT_USER;
const MQTT_PASS = process.env.MQTT_PASS;

function createClient() {
  const options: any = {};
  if (MQTT_USER && MQTT_PASS) {
    options.username = MQTT_USER;
    options.password = MQTT_PASS;
  }
  const client = mqtt.connect(MQTT_URL, options);
  client.on('connect', () => {
    console.log('Node publisher connected to MQTT broker');
  });
  client.on('error', (err) => {
    console.error('MQTT error', err);
  });
  return client;
}

const client = createClient();
const publisher = new MqttEventPublisher(client);

// Periodically publish a heartbeat event for demonstration
setInterval(() => {
  publisher.publish('ngina/events', { type: 'heartbeat', msg: 'publisher alive' });
}, 15000);

// Keep process alive
process.on('SIGINT', () => {
  client.end(true, {}, () => process.exit(0));
});
