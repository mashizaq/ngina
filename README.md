# NGina Orchestrator — scaffold

This branch provides a minimal scaffold for the NGina humanoid orchestrator: a Flask-based HTTP service and a Node/TypeScript MQTT event publisher. Demo archives (NGINA.zip, ngina 2.zip, archive/) are removed per project direction.

Quickstart (development):

1. Create a .env file from the example and fill in any API keys:

   cp .env.example .env
   # set OPENAI_API_KEY if you want LLM responses

2. Start services with Docker Compose:

   docker compose up --build

3. Use the HTTP API:

   curl -X POST http://localhost:5000/chat -H 'Content-Type: application/json' -d '{"message":"Hello"}'

Notes:
- The Python service will attempt to call OpenAI if OPENAI_API_KEY is provided. No keys are committed to the repo.
- The Node publisher connects to the MQTT broker and publishes periodic heartbeat events to ngina/events.
