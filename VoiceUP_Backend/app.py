import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from models import db, User, Conversation, Message, Transcription

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.init_app(app)

with app.app_context():
    db.create_all()

# --- ENDPOINTS EXISTANTS (CONTACTS / CONVS) ---

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    users = User.query.all()
    return jsonify([{"id": u.id, "name": u.name, "avatarUrl": u.avatarUrl} for u in users])

# --- NOUVEAU : ENVOI DE MESSAGE ---

@app.route('/api/conversations/<conv_id>/messages', methods=['POST'])
def send_message(conv_id):
    # On vérifie si c'est un message texte (JSON) ou audio (Multipart)
    if request.is_json:
        data = request.get_json()
        new_msg = Message(
            conversationId=conv_id,
            senderId=data.get('senderId'),
            type='TEXT',
            encryptedPayload=data.get('encryptedPayload'),
            iv=data.get('iv'),
            contentPreview=data.get('plaintextPreview') # Optionnel
        )
        db.session.add(new_msg)
        db.session.commit()
        return jsonify({"id": new_msg.id, "status": "sent"}), 201

    else:
        # Cas du message AUDIO (envoi de fichier)
        file = request.files.get('file')
        sender_id = request.form.get('senderId')
        iv = request.form.get('iv')
        transcription_text = request.form.get('transcription')

        if not file:
            return jsonify({"error": "Fichier manquant"}), 400

        # Sécurisation du nom de fichier (on utilise un UUID pour éviter les conflits)
        filename = f"{uuid.uuid4()}.enc"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        new_msg = Message(
            conversationId=conv_id,
            senderId=sender_id,
            type='AUDIO',
            encryptedBlobUrl=f"/api/uploads/{filename}",
            iv=iv
        )
        db.session.add(new_msg)
        db.session.flush() # Pour récupérer l'ID du message avant le commit final

        # Si une transcription est fournie par le client
        if transcription_text:
            new_trans = Transcription(
                messageId=new_msg.id,
                text=transcription_text,
                confidence=request.form.get('confidence', 1.0)
            )
            db.session.add(new_trans)

        db.session.commit()
        return jsonify({"id": new_msg.id, "status": "uploaded"}), 201

# --- RÉCUPÉRATION DES MESSAGES ---

@app.route('/api/conversations/<conv_id>/messages', methods=['GET'])
def get_messages(conv_id):
    messages = Message.query.filter_by(conversationId=conv_id).order_by(Message.createdAt.asc()).all()
    return jsonify([{
        "id": m.id,
        "senderId": m.senderId,
        "type": m.type,
        "encryptedPayload": m.encryptedPayload,
        "encryptedBlobUrl": m.encryptedBlobUrl,
        "iv": m.iv,
        "createdAt": m.createdAt.isoformat(),
        "transcription": m.transcription.text if m.transcription else None
    } for m in messages])

# --- ACCÈS AUX FICHIERS AUDIO ---

@app.route('/api/uploads/<filename>')
def downloaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/messages/<message_id>/transcription', methods=['GET'])
def get_message_transcription(message_id):
    trans = Transcription.query.filter_by(messageId=message_id).first()
    if not trans:
        return jsonify({"error": "Transcription non trouvée"}), 404
    
    return jsonify({
        "id": trans.id,
        "messageId": trans.messageId,
        "text": trans.text,
        "confidence": trans.confidence,
        "createdAt": trans.createdAt.isoformat()
    }), 200

@app.route('/api/messages/<message_id>', methods=['GET'])
def get_message_details(message_id):
    m = Message.query.get_or_404(message_id)
    return jsonify({
        "id": m.id,
        "conversationId": m.conversationId,
        "senderId": m.senderId,
        "type": m.type,
        "isEncrypted": m.isEncrypted,
        "encryptedBlobUrl": m.encryptedBlobUrl,
        "iv": m.iv,
        "createdAt": m.createdAt.isoformat()
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)