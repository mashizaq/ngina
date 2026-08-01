import { logger } from '../utils/logger';

export class MqttEventPublisher {
    private client: any;

    constructor(client: any) {
        this.client = client;
    }

    public publish(topic: string, message: any): void {
        const payload = JSON.stringify({
            ...message,
            timestamp: new Date().toISOString()
        });

        // Non-blocking fire-and-forget publish pattern
        this.client.publish(topic, payload, { qos: 1 }, (error: any) => {
            if (error) {
                logger.error(`MQTT publish failed on topic ${topic}:`, error);
            } else {
                logger.debug(`MQTT event streamed to ${topic}`);
            }
        });
    }
}
