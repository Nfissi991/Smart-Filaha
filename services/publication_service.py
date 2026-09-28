# services/publication_service.py
import os
import uuid
from database.db import SessionLocal
from database.models import Publication, User
from config.settings import PUBLICATION_UPLOAD_DIR


def save_publication_image(uploaded_file):
    if uploaded_file is None:
        return None
    os.makedirs(PUBLICATION_UPLOAD_DIR, exist_ok=True)
    ext = uploaded_file.name.split(".")[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PUBLICATION_UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def create_publication(conseiller_id, title, content, publication_type="conseil",
                        image_path=None, product_id=None):
    db = SessionLocal()
    try:
        publication = Publication(
            conseiller_id=conseiller_id, title=title, content=content,
            publication_type=publication_type, image_path=image_path,
            product_id=product_id, status="published",
        )
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return publication
    finally:
        db.close()


def get_published_publications():
    db = SessionLocal()
    try:
        return (db.query(Publication, User)
                .join(User, Publication.conseiller_id == User.id)
                .filter(Publication.status == "published",
                        User.role == "conseiller",
                        User.is_active == True,
                        User.is_approved == True)
                .order_by(Publication.created_at.desc()).all())
    finally:
        db.close()


def get_my_publications(conseiller_id):
    db = SessionLocal()
    try:
        return (db.query(Publication)
                .filter(Publication.conseiller_id == conseiller_id)
                .order_by(Publication.created_at.desc()).all())
    finally:
        db.close()
def get_all_publications():
    """Bach admin ychof KOLCHI, bla ay filtre (status/approved/actif)."""
    db = SessionLocal()
    try:
        return (db.query(Publication, User)
                .join(User, Publication.conseiller_id == User.id)
                .order_by(Publication.created_at.desc()).all())
    finally:
        db.close()

def set_publication_status(publication_id, status):
    """status: 'published' | 'hidden' | 'draft'"""
    db = SessionLocal()
    try:
        pub = db.query(Publication).filter(Publication.id == publication_id).first()
        if pub:
            pub.status = status
            db.commit()
        return pub
    finally:
        db.close()

def delete_publication(publication_id, conseiller_id=None):
    db = SessionLocal()
    try:
        q = db.query(Publication).filter(Publication.id == publication_id)
        if conseiller_id is not None:
            q = q.filter(Publication.conseiller_id == conseiller_id)
        pub = q.first()
        if pub:
            db.delete(pub)
            db.commit()
            return True
        return False
    finally:
        db.close()