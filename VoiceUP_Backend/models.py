from flask_sqlalchemy import SQLAlchemy
import uuid
from datetime import datetime

db = SQLAlchemy()

# Table de liaison pour la relation Many-to-Many entre Utilisateurs et Conversations
participants = db.Table('participants',
    db.Column('user_id', db.String(36), db.ForeignKey('user.id'), primary_key=True),
    db.Column('conversation_id', db.String(36), db.ForeignKey('conversation.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    avatarUrl = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation vers les messages envoyés
    messages = db.relationship('Message', backref='sender', lazy=True)

class Conversation(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100))
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation Many-to-Many vers les Utilisateurs
    users = db.relationship('User', secondary=participants, backref='conversations')
    # Relation vers les messages de la conversation
    messages = db.relationship('Message', backref='conversation', lazy=True)

class Message(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversationId = db.Column(db.String(36), db.ForeignKey('conversation.id'), nullable=False)
    senderId = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    
    type = db.Column(db.String(10), nullable=False)  # 'TEXT' ou 'AUDIO'
    isEncrypted = db.Column(db.Boolean, default=True)
    
    # Pour le texte chiffré ou l'URL du fichier audio chiffré
    encryptedPayload = db.Column(db.Text) 
    encryptedBlobUrl = db.Column(db.String(255))
    iv = db.Column(db.String(255))
    
    # Aperçu optionnel (souvent non chiffré pour la liste des convs)
    contentPreview = db.Column(db.Text)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Lien vers la transcription
    transcription = db.relationship('Transcription', backref='message', uselist=False)

class Transcription(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    messageId = db.Column(db.String(36), db.ForeignKey('message.id'), unique=True)
    text = db.Column(db.Text, nullable=False)
    confidence = db.Column(db.Float)
    createdAt = db.Column(db.DateTime, default=datetime.utcnow)