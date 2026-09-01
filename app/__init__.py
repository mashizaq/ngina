from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    # Configuration via env
    database_url = os.getenv('DATABASE_URL') or os.getenv('DB_URL') or os.getenv('DB_PATH')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # fallback to SQLite in data directory
        os.makedirs('data', exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/ngina.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # register blueprints
    from .api import bp as api_bp
    app.register_blueprint(api_bp)

    # initialize mqtt publisher
    from .mqtt import MqttPublisher
    mqtt = MqttPublisher(app)
    app.extensions['mqtt_publisher'] = mqtt

    return app
