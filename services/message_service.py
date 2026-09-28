# services/message_service.py
from sqlalchemy import or_, and_
from database.db import SessionLocal
from database.models import Message, User


def send_message(sender_id, receiver_id, content):
    content = content.strip()
    if not content or sender_id == receiver_id:
        return None
    db = SessionLocal()
    try:
        receiver = db.query(User).filter(User.id == receiver_id, User.is_active == True).first()
        if not receiver:
            return None
        message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content, is_read=False)
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    finally:
        db.close()


def get_conversation(user_id, other_user_id):
    db = SessionLocal()
    try:
        return (db.query(Message)
                .filter(or_(
                    and_(Message.sender_id == user_id, Message.receiver_id == other_user_id),
                    and_(Message.sender_id == other_user_id, Message.receiver_id == user_id)
                ))
                .order_by(Message.created_at.asc()).all())
    finally:
        db.close()


def mark_messages_read(user_id, other_user_id):
    db = SessionLocal()
    try:
        (db.query(Message)
         .filter(Message.sender_id == other_user_id, Message.receiver_id == user_id, Message.is_read == False)
         .update({"is_read": True}))
        db.commit()
    finally:
        db.close()


def get_unread_count(user_id):
    db = SessionLocal()
    try:
        return db.query(Message).filter(Message.receiver_id == user_id, Message.is_read == False).count()
    finally:
        db.close()


def get_my_conversations(user_id):
    db = SessionLocal()
    try:
        messages = (db.query(Message)
                    .filter(or_(Message.sender_id == user_id, Message.receiver_id == user_id))
                    .order_by(Message.created_at.desc()).all())
        user_ids = set()
        for m in messages:
            if m.sender_id != user_id:
                user_ids.add(m.sender_id)
            if m.receiver_id != user_id:
                user_ids.add(m.receiver_id)
        if not user_ids:
            return []
        return db.query(User).filter(User.id.in_(user_ids)).all()
    finally:
        db.close()