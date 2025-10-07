from models import db, Message

class MessageRepository:
    def get_all(self):
        return Message.query.order_by(Message.id.desc()).all()

    def get_by_id(self, id):
        return Message.query.get_or_404(id)

    def save(self, text, photo_path):
        message = Message(text=text, photo=photo_path)
        db.session.add(message)
        db.session.commit()
        return message

    def delete(self, message):
        db.session.delete(message)
        db.session.commit()
        return message
