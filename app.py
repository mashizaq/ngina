from flask import Flask, request, jsonify
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MQTT_URL = os.getenv('MQTT_URL', 'mqtt://mosquitto:1883')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Lazy import for optional OpenAI usage
try:
    import openai
    openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None

# Simple in-memory persona store (replace with persistent storage as needed)
personas = {
    "default": {
        "name": "NGINA",
        "description": "A helpful humanoid AI orchestrator",
        "tone": "friendly"
    }
}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/persona', methods=['GET', 'POST'])
def persona():
    if request.method == 'GET':
        return jsonify(personas)
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"error": "persona name required"}), 400
    personas[name] = data
    return jsonify({"ok": True, "persona": personas[name]})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    persona_name = data.get('persona', 'default')

    if not message:
        return jsonify({"error": "message is required"}), 400

    persona = personas.get(persona_name, personas['default'])

    # Simple prompt assembly
    prompt = f"Persona: {persona.get('description')}\nTone: {persona.get('tone')}\nUser: {message}\nAssistant:"

    response_text = None

    if openai and OPENAI_API_KEY:
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": persona.get('description')},
                    {"role": "user", "content": message}
                ],
                max_tokens=500
            )
            response_text = resp.choices[0].message.content.strip()
        except Exception as e:
            response_text = f"[error calling OpenAI: {str(e)}]"
    else:
        # Fallback simple echo responder
        response_text = f"(stub) {persona.get('name')}: {message}"

    # Publish an MQTT event to signal the response (non-blocking best-effort)
    try:
        from paho.mqtt import client as mqtt_client
        import urllib.parse

        # paho expects hostname and port; parse MQTT_URL if possible
        parsed = urllib.parse.urlparse(MQTT_URL)
        host = parsed.hostname or 'mosquitto'
        port = parsed.port or 1883
        client_id = f'ngina-python-pub'
        client = mqtt_client.Client(client_id)
        if MQTT_USER and MQTT_PASS:
            client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host, port)
        payload = json.dumps({"event": "response", "persona": persona_name, "message": response_text})
        client.publish('ngina/events', payload, qos=1)
        client.disconnect()
    except Exception:
        # best-effort; don't fail the request on publish errors
        pass

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
