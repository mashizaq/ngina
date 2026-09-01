from flask import Blueprint, current_app, request, jsonify
from app import db
from app.models import Persona
import json

bp = Blueprint('api', __name__)


@bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@bp.route('/persona', methods=['GET', 'POST'])
def persona():
    if request.method == 'GET':
        personas = Persona.query.all()
        if not personas:
            # fallback default
            return jsonify({'default': {'name': 'NGINA', 'description': 'A helpful humanoid AI orchestrator', 'tone': 'friendly'}})
        return jsonify({p.name: p.to_dict() for p in personas})

    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error': 'persona name required'}), 400

    p = Persona.query.filter_by(name=name).first()
    if not p:
        p = Persona(name=name)
    p.description = data.get('description')
    p.tone = data.get('tone')
    meta = data.get('metadata')
    p.metadata = meta
    db.session.add(p)
    db.session.commit()
    return jsonify({'ok': True, 'persona': p.to_dict()})


@bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json() or {}
    message = data.get('message')
    persona_name = data.get('persona', 'default')

    if not message:
        return jsonify({'error': 'message is required'}), 400

    if persona_name == 'default':
        persona = Persona.query.filter_by(name='default').first()
        if not persona:
            persona = None
    else:
        persona = Persona.query.filter_by(name=persona_name).first()

    if persona:
        persona_dict = persona.to_dict()
    else:
        persona_dict = {'name': 'NGINA', 'description': 'A helpful humanoid AI orchestrator', 'tone': 'friendly'}

    # OpenAI integration
    response_text = None
    openai_key = current_app.config.get('OPENAI_API_KEY') or None
    try:
        from openai import ChatCompletion
        import openai
        openai.api_key = openai_key
        if openai_key:
            resp = openai.ChatCompletion.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': persona_dict.get('description')},
                    {'role': 'user', 'content': message}
                ],
                max_tokens=500
            )
            response_text = resp.choices[0].message.content.strip()
    except Exception:
        response_text = None

    if not response_text:
        response_text = f"(assistant) {persona_dict.get('name')}: {message}"

    # publish mqtt event (non-blocking)
    try:
        publisher = current_app.extensions.get('mqtt_publisher')
        if publisher:
            publisher.publish('ngina/events', {'event': 'response', 'persona': persona_dict.get('name'), 'message': response_text})
    except Exception:
        pass

    return jsonify({'response': response_text})
