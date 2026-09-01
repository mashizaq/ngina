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

// Publish telemetry (stubbed) to a dedicated topic and include event_type in payload
setInterval(() => {
  const telemetry = {
    type: 'telemetry',
    cpu: Math.round(Math.random() * 100),
    memory: Math.round(Math.random() * 1000),
    unit: 'MB'
  };
  publisher.publish('ngina/events/telemetry', { event_type: 'telemetry', payload: telemetry });
}, 30000);

// Publish state changes occasionally
setInterval(() => {
  const states = ['idle', 'active', 'error'];
  const state = states[Math.floor(Math.random() * states.length)];
  publisher.publish('ngina/events/state', { event_type: 'state_change', state });
}, 45000);

// Publish an alert example (rare)
setInterval(() => {
  if (Math.random() > 0.9) {
    publisher.publish('ngina/events/alert', { event_type: 'alert', level: 'warning', message: 'Example alert' });
  }
}, 60000);

// Keep process alive
process.on('SIGINT', () => {
  client.end(true, {}, () => process.exit(0));
});
