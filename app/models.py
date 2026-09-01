from app import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy import Column, Integer, String, Text

try:
    # Use native JSON type when available
    metadata_type = JSON
except Exception:
    metadata_type = Text


class Persona(db.Model):
    __tablename__ = 'personas'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), unique=True, nullable=False)
    description = Column(Text)
    tone = Column(String(64))
    metadata = Column(metadata_type)

    def to_dict(self):
        return {
            'name': self.name,
            'description': self.description,
            'tone': self.tone,
            'metadata': self.metadata
        }
