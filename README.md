# NGina Orchestrator — scaffold

NGina is a small humanoid orchestrator demo combining a Flask HTTP service (Python) and a Node/TypeScript MQTT event publisher. It demonstrates a simple persona-driven chat API, optional OpenAI integration, and MQTT event publishing for downstream consumers.

## Quick summary
- Web API: Flask app (app.py) exposing /health, /persona, and /chat endpoints.
- MQTT publisher: Node/TypeScript publisher located in src/backend that publishes heartbeat/response events to an MQTT broker.
- Containerized: Dockerfile and docker-compose.yml to run the stack locally (web, mosquitto broker, and node-publisher).

## Top-level layout
```
.
├─ .env.example                # example environment variables
├─ .gitignore
├─ .github/                    # CI/workflow config (if present)
├─ CHARACTER_PROFILE.md        # persona/character notes
├─ LOCALIZATION_NAMES.md       # localization-related names
├─ Dockerfile                  # container image for the Flask web service
├─ docker-compose.yml          # local compose stack (web, mosquitto, node-publisher)
├─ requirements.txt            # Python deps (Flask, paho-mqtt, openai, ...)
├─ package-lock.json           # Node lockfile (publisher)
├─ README.md                   # this file
├─ NGINA.zip, "ngina 2.zip"     # demo/archive artifacts
├─ archive/                    # older archives / demo content
├─ app.py                      # Flask web application (primary Python entrypoint)
├─ scripts/                    # helper scripts (dev utilities)
└─ src/
   └─ backend/                 # Node/TypeScript MQTT publisher
       ├─ package.json
       ├─ package-lock.json
       ├─ tsconfig.json
       └─ src/                 # publisher source (TypeScript)
```

## What runs and how it fits together
- The Flask app (app.py) handles HTTP requests for health, persona management, and chat. It optionally calls OpenAI (if OPENAI_API_KEY is set) to generate responses, otherwise returns a simple stub echo.
- After generating a response, the Flask app publishes a JSON event to the MQTT topic ngina/events (best-effort).
- The Node/TypeScript publisher (src/backend) publishes heartbeat or other periodic events to the same MQTT broker for demo purposes. The publisher can be extended to publish additional event types (telemetry, state, alerts) so consumers can react to different runtime signals.
- docker-compose wires the three services together: web (Flask), mosquitto (Eclipse Mosquitto MQTT broker), and node-publisher (built from src/backend).

## Environment variables
Important variables used by the stack:
- OPENAI_API_KEY — optional, enable OpenAI ChatCompletion for chat responses.
- MQTT_URL — broker URL (defaults to mqtt://mosquitto:1883 in code).
- MQTT_USER / MQTT_PASS — optional MQTT credentials.
These are provided via .env (copy from .env.example).

## Run (shortest path — development)
1. Copy the example env file and edit values:
```bash
cp .env.example .env
# edit .env to set OPENAI_API_KEY (optional), MQTT_URL, MQTT_USER, MQTT_PASS
```

2. Start the full stack with Docker Compose:
```bash
docker compose up --build
```
This will build the web image (Dockerfile), build the node-publisher from src/backend, and start a Mosquitto broker.

3. Call the chat endpoint:
```bash
curl -X POST http://localhost:5000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello"}'
```

Alternative: run Flask locally (without Docker)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app.py
flask run --host=0.0.0.0
```

Run the Node/TypeScript publisher locally (optional)
```bash
cd src/backend
npm install
# use package.json scripts, e.g. npm run build && npm start (see package.json)
```

## API (brief)
- GET /health
  - Returns status OK: {"status":"ok"}
- GET /persona
  - Returns in-memory persona store (JSON).
- POST /persona
  - Create/update a persona. JSON body must include "name".
- POST /chat
  - Body: {"message": "<text>", "persona": "<optional-persona-name>"}
  - Returns: {"response": "<assistant text>"}
  - If OPENAI_API_KEY is set, the app will attempt to use OpenAI ChatCompletion; otherwise it replies with a stub echo.
  - After responding, the service publishes an MQTT message to topic ngina/events:
    {"event":"response","persona":"<name>","message":"<text>"}

## Notable files & where to look
- app.py — Flask routes and main application logic (OpenAI integration and MQTT publish).
- Dockerfile — builds the Flask service image (Python 3.11-slim).
- docker-compose.yml — defines services and how they connect; mosquitto config is mounted from ./mosquitto/config.
- requirements.txt — Python dependencies: Flask, python-dotenv, paho-mqtt, openai, etc.
- src/backend — Node/TypeScript MQTT publisher that the compose stack builds as node-publisher.

## Development notes & TODOs
- Personas persistence: personas are currently stored in-memory in app.py. This repository will persist personas to a small SQLite database (e.g., using SQLAlchemy or sqlite3) so personas survive restarts and are easy to query. See app.py for the persona endpoints; migrate the in-memory dict to a lightweight DB-backed model.
- Node publisher events: extend src/backend to publish additional event types beyond heartbeat/response (for example: telemetry, state_change, alert). Consumers can subscribe to topics like ngina/events/telemetry or include an "event_type" field in the payload.
- MQTT publishes are best-effort and synchronous; consider using a background worker or queued publisher for robustness.
- The repository contains demo archives (NGINA.zip, ngina 2.zip) under the top level and archive/ — review and remove if not needed.
- Add tests and CI workflows as needed (there is a .github directory for workflows if present).

## License
(If applicable) Add your license file or license information here.

## Questions you might want to ask
- Should personas persist to a small DB (SQLite) or an external store?
- Do you want the node publisher to publish additional event types (e.g., telemetry, state changes)?
- Should we add a small client example showing subscription to ngina/events?
