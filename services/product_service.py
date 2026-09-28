# services/product_service.py
import os
import uuid
from database.db import SessionLocal
from database.models import Product
from config.settings import PRODUCT_UPLOAD_DIR


def save_product_image(uploaded_file):
    if uploaded_file is None:
        return None
    os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)
    ext = uploaded_file.name.split(".")[-1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(PRODUCT_UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path


def create_product(conseiller_id, name, description, price, stock, image_path=None):
    db = SessionLocal()
    try:
        product = Product(
            conseiller_id=conseiller_id, name=name, description=description,
            price=price, stock=stock, image_path=image_path, is_active=True,
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return product
    finally:
        db.close()


def get_products_by_conseiller(conseiller_id):
    db = SessionLocal()
    try:
        return (db.query(Product)
                .filter(Product.conseiller_id == conseiller_id, Product.is_active == True)
                .order_by(Product.created_at.desc()).all())
    finally:
        db.close()


def get_all_products():
    db = SessionLocal()
    try:
        return (db.query(Product).filter(Product.is_active == True)
                .order_by(Product.created_at.desc()).all())
    finally:
        db.close()


def delete_product(product_id, conseiller_id=None):
    db = SessionLocal()
    try:
        query = db.query(Product).filter(Product.id == product_id)
        if conseiller_id is not None:
            query = query.filter(Product.conseiller_id == conseiller_id)
        product = query.first()
        if product:
            product.is_active = False
            db.commit()
            return True
        return False
    finally:
        db.close()