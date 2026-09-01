from flask import Flask, request, jsonify, g
import os
import json
import sqlite3
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MQTT_URL = os.getenv('MQTT_URL', 'mqtt://mosquitto:1883')
MQTT_USER = os.getenv('MQTT_USER')
MQTT_PASS = os.getenv('MQTT_PASS')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
DB_PATH = os.getenv('DB_PATH', 'data/ngina.db')

# Lazy import for optional OpenAI usage
try:
    import openai
    openai.api_key = OPENAI_API_KEY
except Exception:
    openai = None

# Database helpers (SQLite)
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        # ensure data directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            tone TEXT,
            metadata TEXT
        )
        """
    )
    db.commit()

# Ensure DB is initialized on startup
with app.app_context():
    init_db()

# Simple in-memory persona fallback (kept for compatibility)
_default_persona = {
    "name": "NGINA",
    "description": "A helpful humanoid AI orchestrator",
    "tone": "friendly"
}

def fetch_all_personas():
    db = get_db()
    cur = db.execute('SELECT name, description, tone, metadata FROM personas')
    rows = cur.fetchall()
    result = {}
    for r in rows:
        meta = {}
        try:
            meta = json.loads(r['metadata']) if r['metadata'] else {}
        except Exception:
            meta = {}
        result[r['name']] = {
            'name': r['name'],
            'description': r['description'],
            'tone': r['tone'],
            'metadata': meta
        }
    return result

def get_persona(name: str):
    db = get_db()
    cur = db.execute('SELECT name, description, tone, metadata FROM personas WHERE name = ?', (name,))
    r = cur.fetchone()
    if not r:
        return None
    meta = {}
    try:
        meta = json.loads(r['metadata']) if r['metadata'] else {}
    except Exception:
        meta = {}
    return {
        'name': r['name'],
        'description': r['description'],
        'tone': r['tone'],
        'metadata': meta
    }

def upsert_persona(payload: dict):
    name = payload.get('name')
    description = payload.get('description')
    tone = payload.get('tone')
    metadata = payload.get('metadata')
    metadata_json = json.dumps(metadata) if metadata is not None else None

    db = get_db()
    # INSERT OR REPLACE will replace the row when name conflicts
    db.execute(
        'INSERT INTO personas (name, description, tone, metadata) VALUES (?, ?, ?, ?)'
        ' ON CONFLICT(name) DO UPDATE SET description=excluded.description, tone=excluded.tone, metadata=excluded.metadata',
        (name, description, tone, metadata_json)
    )
    db.commit()
    return get_persona(name)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/persona', methods=['GET', 'POST'])
def persona():
    if request.method == 'GET':
        personas = fetch_all_personas()
        # If DB is empty, return the default persona to preserve previous behavior
        if not personas:
            return jsonify({ 'default': _default_persona })
        return jsonify(personas)

    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({"error": "persona name required"}), 400
    persona = upsert_persona(data)
    return jsonify({"ok": True, "persona": persona})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    persona_name = data.get('persona', 'default')

    if not message:
        return jsonify({"error": "message is required"}), 400

    persona = None
    if persona_name == 'default':
        # try to get a persona named 'default' from DB, otherwise use fallback
        persona = get_persona('default') or _default_persona
    else:
        persona = get_persona(persona_name) or _default_persona

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
        payload = json.dumps({"event": "response", "persona": persona.get('name'), "message": response_text})
        client.publish('ngina/events', payload, qos=1)
        client.disconnect()
    except Exception:
        # best-effort; don't fail the request on publish errors
        pass

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
