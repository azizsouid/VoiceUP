from app import app
from models import db, User, Conversation

def seed_data():
    with app.app_context():
        # 1. Nettoyage (Optionnel : à ne faire que si tu veux repartir de zéro)
        # db.drop_all()
        # db.create_all()

        # Vérifier si on a déjà des utilisateurs pour éviter les doublons
        if User.query.first():
            print("La base de données contient déjà des données.")
            return

        print("Initialisation des contacts fictifs...")

        # 2. Création de l'utilisateur principal (Toi)
        me = User(name="Moi-même", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=me")
        
        # 3. Création des 5 contacts fictifs (VoiceUP Prototype)
        contacts = [
            User(name="Amina", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=Amina"),
            User(name="Yassine", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=Yassine"),
            User(name="Sonia", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=Sonia"),
            User(name="Karim", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=Karim"),
            User(name="Léa", avatarUrl="https://api.dicebear.com/7.x/avataaars/svg?seed=Lea")
        ]

        db.session.add(me)
        db.session.add_all(contacts)
        db.session.commit()

        # 4. Création d'une conversation de test avec Amina
        print("Création d'une conversation de test...")
        conv = Conversation(title="Amina")
        conv.users.append(me)
        conv.users.append(contacts[0]) # Amina

        db.session.add(conv)
        db.session.commit()

        print("Base de données initialisée avec succès !")
        print(f"ID de 'Moi-même' (à utiliser dans ton app mobile) : {me.id}")

if __name__ == '__main__':
    seed_data()