# view/dashboard_conseiller.py
# Smart Filaha - Dashboard Conseiller
import os
import html
import base64
from textwrap import dedent
from collections import Counter
import streamlit as st
from sqlalchemy import or_, and_
from database.db import SessionLocal
from database.models import Message, Product, User
from config.settings import COLORS
from services.publication_service import (
    create_publication,
    get_my_publications,
    save_publication_image,
    delete_publication,
)
from services.product_service import (
    create_product,
    save_product_image,
)
C = COLORS
# ================================================================
# PATHS / ASSETS
# ================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logof.png")
HERO_PATH = os.path.join(ASSETS_DIR, "images.jpg")
def H(content):
    st.markdown(dedent(content), unsafe_allow_html=True)
def esc(value):
    return html.escape("" if value is None else str(value))
def fmt_date(value, with_time=True):
    if not value:
        return ""
    try:
        return value.strftime("%d/%m/%Y %H:%M" if with_time else "%d/%m/%Y")
    except Exception:
        return str(value)
def resolve_file(path):
    if not path:
        return None
    raw = str(path).strip().strip('"').strip("'")
    raw = raw.replace("\\", "/")
    if not raw:
        return None
    candidates = [raw]
    if not os.path.isabs(raw):
        candidates.extend([
            os.path.join(os.getcwd(), raw),
            os.path.join(BASE_DIR, raw),
            os.path.join(BASE_DIR, raw.lstrip("/\\")),
            os.path.join(BASE_DIR, "uploads", raw.lstrip("/\\")),
            os.path.join(BASE_DIR, "uploads", "products", os.path.basename(raw)),
            os.path.join(BASE_DIR, "uploads", "publications", os.path.basename(raw)),
        ])
    basename = os.path.basename(raw)
    if basename:
        candidates.extend([
            os.path.join(BASE_DIR, "uploads", "products", basename),
            os.path.join(BASE_DIR, "uploads", "publications", basename),
        ])
    seen = set()
    for candidate in candidates:
        candidate = os.path.normpath(candidate)
        if candidate in seen:
            continue
        seen.add(candidate)
        if os.path.isfile(candidate):
            return candidate
    return None
def image_data_uri(path):
    path = resolve_file(path)
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            raw = f.read()
        ext = os.path.splitext(path)[1].lower()
        mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }.get(ext, "image/jpeg")
        return f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
    except Exception:
        return None
LOGO_URI = image_data_uri(LOGO_PATH)
HERO_URI = image_data_uri(HERO_PATH)
# ================================================================
# LANGUAGE
# ================================================================
LANGS = {
    "Français": "fr",
    "العربية": "ar",
    "الدارجة المغربية": "darija",
}
TEXTS = {
    "fr": {
        "dashboard": "Tableau de bord",
        "publications": "Mes publications",
        "products": "Mes produits",
        "messages": "Mes messages",
        "farmers": "Mes agriculteurs",
        "profile": "Mon profil",
        "logout": "Déconnexion",
        "nav": "Navigation",
        "search": "Rechercher une publication, un produit, un agriculteur...",
        "hello": "Bonjour",
        "hero_sub": "Voici un aperçu de votre activité de conseiller agricole aujourd'hui.",
        "live": "Données en direct",
        "pubs": "Publications",
        "products_short": "Produits",
        "messages_short": "Messages",
        "farmers_short": "Agriculteurs",
        "recent_pubs": "Publications récentes",
        "recent_pubs_sub": "Vos derniers conseils et contenus partagés",
        "activity": "Activité",
        "activity_sub": "Publications par jour",
        "week": "Cette semaine",
        "conversations": "Mes dernières conversations",
        "conversations_sub": "Échanges récents avec les agriculteurs",
        "open_messages": "Ouvrir les messages",
        "popular_products": "Produits populaires",
        "popular_products_sub": "Produits proposés aux agriculteurs",
        "catalog": "Votre catalogue",
        "manage_products": "Gérer mes produits",
        "all_pubs": "Voir toutes mes publications",
        "published": "Publié le",
        "no_pub": "Aucune publication pour le moment.",
        "no_product": "Aucun produit ajouté.",
        "no_conv": "Aucune conversation.",
        "contact": "Contacts actifs",
        "content": "Votre contenu",
        "catalog_current": "Catalogue actuel",
        "farmers_contact": "Agriculteurs en contact",
        "active": "EN DIRECT",
        "messages_page_sub": "Échangez directement avec les agriculteurs et retrouvez votre historique.",
        "conversations_page": "Conversations",
        "active_conversation": "Agriculteur · conversation active",
        "write_message": "Écrivez votre message...",
        "send": "Envoyer",
        "no_messages": "Aucun message dans cette conversation.",
        "products_page_sub": "Gérez les produits proposés aux agriculteurs.",
        "add_product": "Ajouter un produit",
        "product_name": "Nom du produit",
        "description": "Description",
        "price": "Prix (DH)",
        "stock": "Stock",
        "add": "Ajouter",
        "delete": "Supprimer",
        "fill_name_price": "Remplissez au moins le nom et le prix.",
        "added": "Produit ajouté !",
        "pub_page_sub": "Conseils, articles, annonces et publications produits.",
        "new_pub": "Nouvelle publication",
        "title": "Titre",
        "type": "Type",
        "image_optional": "Image (optionnel)",
        "link_product": "Lier à un produit",
        "publish": "Publier",
        "pub_created": "Publication créée !",
        "fill_title_content": "Remplissez au moins le titre et le contenu.",
        "farmers_page_sub": "Les agriculteurs ayant déjà échangé avec vous.",
        "open_conversation": "Ouvrir la conversation",
        "profile_sub": "Informations et sécurité du compte.",
        "new_password": "Nouveau mot de passe",
        "confirm_password": "Confirmer le mot de passe",
        "save": "Enregistrer",
        "password_mismatch": "Les mots de passe ne correspondent pas.",
        "updated": "Mot de passe mis à jour !",
        "no_change": "Aucune modification.",
        "farmer": "Agriculteur",
        "stock_ok": "En stock",
        "stock_low": "Stock faible",
        "article": "article",
    },
    "ar": {
        "dashboard": "لوحة التحكم",
        "publications": "منشوراتي",
        "products": "منتجاتي",
        "messages": "رسائلي",
        "farmers": "الفلاحون",
        "profile": "ملفي الشخصي",
        "logout": "تسجيل الخروج",
        "nav": "التنقل",
        "search": "ابحث عن منشور أو منتج أو فلاح...",
        "hello": "مرحبا",
        "hero_sub": "هذه نظرة سريعة على نشاطك كمستشار فلاحي اليوم.",
        "live": "بيانات مباشرة",
        "pubs": "المنشورات",
        "products_short": "المنتجات",
        "messages_short": "الرسائل",
        "farmers_short": "الفلاحون",
        "recent_pubs": "أحدث المنشورات",
        "recent_pubs_sub": "آخر النصائح والمحتويات التي شاركتها",
        "activity": "النشاط",
        "activity_sub": "المنشورات حسب اليوم",
        "week": "هذا الأسبوع",
        "conversations": "آخر المحادثات",
        "conversations_sub": "آخر التبادلات مع الفلاحين",
        "open_messages": "فتح الرسائل",
        "popular_products": "المنتجات الشائعة",
        "popular_products_sub": "المنتجات المقترحة للفلاحين",
        "catalog": "الكتالوج",
        "manage_products": "إدارة المنتجات",
        "all_pubs": "عرض جميع منشوراتي",
        "published": "نشر في",
        "no_pub": "لا توجد منشورات حاليا.",
        "no_product": "لا توجد منتجات.",
        "no_conv": "لا توجد محادثات.",
        "contact": "جهات اتصال نشطة",
        "content": "محتواك",
        "catalog_current": "الكتالوج الحالي",
        "farmers_contact": "فلاحون على اتصال",
        "active": "مباشر",
        "messages_page_sub": "تواصل مباشرة مع الفلاحين واطلع على سجل المحادثات.",
        "conversations_page": "المحادثات",
        "active_conversation": "فلاح · محادثة نشطة",
        "write_message": "اكتب رسالتك...",
        "send": "إرسال",
        "no_messages": "لا توجد رسائل في هذه المحادثة.",
        "products_page_sub": "إدارة المنتجات المقترحة للفلاحين.",
        "add_product": "إضافة منتج",
        "product_name": "اسم المنتج",
        "description": "الوصف",
        "price": "الثمن (درهم)",
        "stock": "المخزون",
        "add": "إضافة",
        "delete": "حذف",
        "fill_name_price": "أدخل الاسم والثمن على الأقل.",
        "added": "تمت إضافة المنتج!",
        "pub_page_sub": "نصائح ومقالات وإعلانات ومنشورات المنتجات.",
        "new_pub": "منشور جديد",
        "title": "العنوان",
        "type": "النوع",
        "image_optional": "الصورة (اختياري)",
        "link_product": "ربط بمنتج",
        "publish": "نشر",
        "pub_created": "تم إنشاء المنشور!",
        "fill_title_content": "أدخل العنوان والمحتوى على الأقل.",
        "farmers_page_sub": "الفلاحون الذين تواصلوا معك سابقا.",
        "open_conversation": "فتح المحادثة",
        "profile_sub": "معلومات الحساب والأمان.",
        "new_password": "كلمة المرور الجديدة",
        "confirm_password": "تأكيد كلمة المرور",
        "save": "حفظ",
        "password_mismatch": "كلمتا المرور غير متطابقتين.",
        "updated": "تم تحديث كلمة المرور!",
        "no_change": "لا يوجد تغيير.",
        "farmer": "فلاح",
        "stock_ok": "متوفر",
        "stock_low": "مخزون منخفض",
        "article": "مقال",
    },
    "darija": {
        "dashboard": "Tableau de bord",
        "publications": "Les publications dyali",
        "products": "Les produits dyali",
        "messages": "Les messages dyali",
        "farmers": "Les fellaha",
        "profile": "Profil dyali",
        "logout": "Sortie",
        "nav": "Navigation",
        "search": "Qelleb 3la publication, produit, wla fellah...",
        "hello": "Salam",
        "hero_sub": "Hna wahed l'aperçu 3la l'activité dyalk k conseiller agricole lyoum.",
        "live": "Données directes",
        "pubs": "Publications",
        "products_short": "Produits",
        "messages_short": "Messages",
        "farmers_short": "Fellaha",
        "recent_pubs": "Akher publications",
        "recent_pubs_sub": "Akher nsae7 w contenu li partageiti",
        "activity": "Activité",
        "activity_sub": "Publications par nhar",
        "week": "Had simana",
        "conversations": "Akher conversations",
        "conversations_sub": "Akher lhadra m3a lfellaha",
        "open_messages": "7ell les messages",
        "popular_products": "Produits populaires",
        "popular_products_sub": "Produits li kat9dem lfellaha",
        "catalog": "Catalogue dyalk",
        "manage_products": "Seyyer les produits",
        "all_pubs": "Chof ga3 les publications",
        "published": "Tncher f",
        "no_pub": "Mazal ma kaynach publication.",
        "no_product": "Mazal ma kayn 7ta produit.",
        "no_conv": "Mazal ma kaynach conversation.",
        "contact": "Contacts actifs",
        "content": "Contenu dyalk",
        "catalog_current": "Catalogue daba",
        "farmers_contact": "Fellaha f contact",
        "active": "DIRECT",
        "messages_page_sub": "Hder direct m3a lfellaha w l9a lhistorique dyal messages.",
        "conversations_page": "Conversations",
        "active_conversation": "Fellah · conversation active",
        "write_message": "Kteb message...",
        "send": "Sift",
        "no_messages": "Ma kaynach messages f had conversation.",
        "products_page_sub": "Seyyer les produits li kat9dem lfellaha.",
        "add_product": "Zid produit",
        "product_name": "Smit produit",
        "description": "Description",
        "price": "Taman (DH)",
        "stock": "Stock",
        "add": "Zid",
        "delete": "7yed",
        "fill_name_price": "3mer smiya w taman 3la l9el.",
        "added": "Tzad produit!",
        "pub_page_sub": "Nsae7, articles, annonces w publications produits.",
        "new_pub": "Publication jdida",
        "title": "Titre",
        "type": "Type",
        "image_optional": "Tsawra (ikhtiyari)",
        "link_product": "Rbet m3a produit",
        "publish": "Publier",
        "pub_created": "Tcreat publication!",
        "fill_title_content": "3mer titre w contenu 3la l9el.",
        "farmers_page_sub": "Lfellaha li tbadlti m3ahom.",
        "open_conversation": "7ell conversation",
        "profile_sub": "Ma3loumat w sécurité dyal compte.",
        "new_password": "Password jdida",
        "confirm_password": "2ekked password",
        "save": "7fed",
        "password_mismatch": "Les passwords ma mtaba9inch.",
        "updated": "Tbdlat password!",
        "no_change": "Ma tbdal walo.",
        "farmer": "Fellah",
        "stock_ok": "Kayen",
        "stock_low": "Stock 9lil",
        "article": "article",
    },
}
def current_lang():
    return st.session_state.get("ui_lang", "fr")
def t(key):
    return TEXTS[current_lang()].get(key, TEXTS["fr"].get(key, key))
def set_direction():
    rtl = current_lang() == "ar"
    H(f"""
    <style>
        body, .stApp {{ direction:{'rtl' if rtl else 'ltr'}; }}
        .rtl-note {{ direction:{'rtl' if rtl else 'ltr'}; }}
    </style>
    """)
# ================================================================
# DB : MESSAGES
# ================================================================
def get_my_farmers(conseiller_id):
    db = SessionLocal()
    try:
        rows = db.query(Message).filter(
            or_(
                Message.sender_id == conseiller_id,
                Message.receiver_id == conseiller_id
            )
        ).all()
        ids = set()
        for message in rows:
            ids.add(
                message.receiver_id
                if message.sender_id == conseiller_id
                else message.sender_id
            )
        if not ids:
            return []
        return db.query(User).filter(
            User.id.in_(ids)
        ).order_by(User.username.asc()).all()
    finally:
        db.close()
def get_conversation(conseiller_id, farmer_id):
    db = SessionLocal()
    try:
        return db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == conseiller_id,
                    Message.receiver_id == farmer_id
                ),
                and_(
                    Message.sender_id == farmer_id,
                    Message.receiver_id == conseiller_id
                ),
            )
        ).order_by(Message.created_at.asc()).all()
    finally:
        db.close()
def send_message(sender_id, receiver_id, content):
    if not content or not content.strip():
        return
    db = SessionLocal()
    try:
        db.add(Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip()
        ))
        db.commit()
    finally:
        db.close()
def get_unread_count(conseiller_id):
    db = SessionLocal()
    try:
        return db.query(Message).filter(
            Message.receiver_id == conseiller_id,
            Message.is_read == False  # noqa: E712
        ).count()
    finally:
        db.close()
def mark_conversation_read(conseiller_id, farmer_id):
    db = SessionLocal()
    try:
        db.query(Message).filter(
            Message.receiver_id == conseiller_id,
            Message.sender_id == farmer_id,
            Message.is_read == False,  # noqa: E712
        ).update({"is_read": True})
        db.commit()
    finally:
        db.close()
def get_latest_message(conseiller_id, farmer_id):
    db = SessionLocal()
    try:
        return db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == conseiller_id,
                    Message.receiver_id == farmer_id
                ),
                and_(
                    Message.sender_id == farmer_id,
                    Message.receiver_id == conseiller_id
                ),
            )
        ).order_by(Message.created_at.desc()).first()
    finally:
        db.close()
# ================================================================
# DB : PRODUITS
# ================================================================
def get_my_products(conseiller_id):
    db = SessionLocal()
    try:
        return db.query(Product).filter(
            Product.conseiller_id == conseiller_id
        ).order_by(Product.created_at.desc()).all()
    finally:
        db.close()
def add_product(conseiller_id, name, description, price, stock, image_path=None):
    create_product(
        conseiller_id=conseiller_id,
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_path=image_path,
    )
def delete_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            db.delete(product)
            db.commit()
    finally:
        db.close()
# ================================================================
# DESIGN
# ================================================================
def styles():
    hero = f"url('{HERO_URI}')" if HERO_URI else "none"
    logo = f"url('{LOGO_URI}')" if LOGO_URI else "none"
    H(f"""
    <style>
    #MainMenu, footer, [data-testid="stDecoration"] {{ visibility:hidden; }}
    [data-testid="stAppViewContainer"] {{ background:#f4f7f4; }}
    [data-testid="stHeader"] {{ background:transparent; }}
    .block-container {{ max-width:1460px!important; padding:20px 30px 55px!important; }}
    div[data-testid="stVerticalBlock"] {{ gap:0.65rem; }}
    a {{ text-decoration:none!important; }}
    section[data-testid="stSidebar"] {{
        background:#073e2c!important;
        width:238px!important;
        min-width:238px!important;
    }}
    section[data-testid="stSidebar"]>div {{ background:#073e2c!important; }}
    section[data-testid="stSidebar"] * {{ color:#edf8f1; }}
    section[data-testid="stSidebar"] .stButton>button {{
        width:100%!important;
        background:transparent!important;
        border:1px solid transparent!important;
        color:#eaf5ef!important;
        border-radius:12px!important;
        text-align:left!important;
        min-height:42px!important;
        padding:8px 12px!important;
        font-size:12px!important;
        font-weight:700!important;
        box-shadow:none!important;
        margin:3px 0!important;
        transition:.18s ease;
    }}
    section[data-testid="stSidebar"] .stButton>button:hover {{
        background:rgba(255,255,255,.09)!important;
        border-color:rgba(255,255,255,.05)!important;
    }}
    section[data-testid="stSidebar"] .stButton>button:focus {{
        outline:none!important;
        box-shadow:none!important;
    }}
    .brand {{ padding:4px 5px 18px; border-bottom:1px solid rgba(255,255,255,.13); margin-bottom:18px; }}
    .brand-logo {{ width:100%; height:105px; background-image:{logo}; background-repeat:no-repeat; background-position:center; background-size:contain; }}
    .brand-fallback {{ font-size:18px; font-weight:900; color:white; padding:25px 5px; }}
    .nav-caption {{ font-size:8px; text-transform:uppercase; letter-spacing:.18em; color:#82ae98; font-weight:900; margin:0 7px 8px; }}
    .side-account {{ margin-top:34px; padding:13px; border:1px solid rgba(255,255,255,.14); background:rgba(255,255,255,.055); border-radius:14px; }}
    .side-account-name {{ font-size:11px; font-weight:900; }}
    .side-account-role {{ font-size:8px; color:#9ec4b1; margin-top:4px; }}
    .topbar {{ background:white; border:1px solid #dfe9e2; border-radius:16px; min-height:58px; padding:8px 12px; display:flex; align-items:center; gap:13px; box-shadow:0 5px 20px rgba(20,65,44,.06); margin-bottom:16px; }}
    .top-brand {{ display:none; width:160px; min-width:160px; height:40px; background-image:{logo}; background-repeat:no-repeat; background-position:left center; background-size:contain; }}
    .top-search {{ flex:1; height:38px; border:1px solid #e0e8e3; background:#f7faf8; border-radius:11px; display:flex; align-items:center; padding:0 13px; color:#9aa69f; font-size:10px; }}
    .top-user {{ display:flex; align-items:center; gap:8px; white-space:nowrap; }}
    .top-avatar {{ width:34px; height:34px; border-radius:50%; background:#e3f0e7; display:flex; align-items:center; justify-content:center; font-size:15px; }}
    .top-user-name {{ font-size:10px; font-weight:900; color:#214b39; }}
    .top-user-role {{ font-size:7px; color:#89958e; margin-top:2px; }}
    .notif {{ position:relative; width:34px; height:34px; border-radius:10px; background:#f1f6f3; display:flex; align-items:center; justify-content:center; font-size:14px; }}
    .badge {{ position:absolute; top:-4px; right:-4px; background:#d7434f; color:white; border-radius:10px; min-width:16px; height:16px; font-size:8px; display:flex; align-items:center; justify-content:center; font-weight:900; }}
    .st-key-cons_mobile_nav {{ display:none; }}
    .st-key-cons_mobile_nav [data-testid="stColumn"],
    .st-key-cons_mobile_nav [data-testid="column"] {{ padding:0!important; }}
    .st-key-cons_mobile_nav .stButton {{ margin-bottom:6px!important; }}
    .st-key-cons_mobile_nav .stButton>button {{ min-height:44px!important; font-size:10px!important; white-space:normal!important; }}
    .st-key-cons_mobile_nav button[kind="primary"],
    .st-key-cons_mobile_nav button[data-testid="stBaseButton-primary"] {{
        background:#116641!important; color:white!important; border-color:#116641!important;
    }}
    @media (max-width:900px) {{
        section[data-testid="stSidebar"] {{ display:none!important; }}
        .st-key-cons_mobile_nav {{ display:block!important; }}
        .block-container {{ max-width:100%!important; padding:12px 12px 35px!important; }}
        .topbar {{ padding:9px 10px; gap:8px; min-height:auto; }}
        .top-brand {{ display:block; width:115px; min-width:115px; height:34px; }}
        .top-search {{ display:none; }}
        .top-user-role {{ display:none; }}
        .top-user-name {{ font-size:9px; }}
        .notif, .top-avatar {{ width:32px; height:32px; }}
        .hero {{ height:auto!important; min-height:245px!important; border-radius:18px!important; margin-bottom:13px!important; background-position:center!important; }}
        .hero-inner {{ padding:28px 22px!important; }}
        .hero-title {{ font-size:24px!important; line-height:1.15!important; max-width:520px; }}
        .hero-sub {{ font-size:11px!important; line-height:1.55!important; max-width:600px; }}
        .hero-pill {{ font-size:9px!important; padding:7px 10px!important; }}
        .stat-card {{ min-height:112px!important; padding:14px!important; }}
        .stat-value {{ font-size:25px!important; }}
        .stat-label {{ font-size:9px!important; line-height:1.35!important; }}
        .section-title {{ font-size:14px!important; }}
        .section-sub {{ font-size:9px!important; }}
        .feature {{ grid-template-columns:1fr!important; min-height:0!important; }}
        .feature-image {{ height:230px!important; min-height:230px!important; }}
        .feature-copy {{ padding:17px!important; }}
        .feature-title {{ font-size:18px!important; }}
        .feature-body {{ font-size:10px!important; }}
        .activity-bars {{ height:145px!important; }}
        .bar {{ max-width:24px!important; }}
        .chat-body {{ min-height:360px!important; max-height:none!important; }}
        .chat-bubble {{ max-width:88%!important; font-size:10px!important; }}
        .product-img, .product-placeholder {{ height:170px!important; }}
        .product-name {{ font-size:11px!important; }}
        .product-desc {{ font-size:9px!important; height:auto!important; min-height:34px!important; }}
        .price {{ font-size:11px!important; }}
        .stock-ok, .stock-low {{ font-size:8px!important; }}
        .pub-image {{ max-height:360px!important; }}
    }}
    .hero {{ height:190px; border-radius:20px; overflow:hidden; position:relative; margin-bottom:17px; background-image: linear-gradient(90deg, rgba(3,57,40,.94) 0%, rgba(5,100,66,.80) 55%, rgba(4,75,51,.43) 100%), {hero}; background-size:cover; background-position:center; box-shadow:0 10px 28px rgba(13,74,49,.13); display:flex; align-items:center; }}
    .hero:after {{ content:""; position:absolute; right:-80px; top:-100px; width:330px; height:330px; border-radius:50%; background:rgba(255,255,255,.07); }}
    .hero-inner {{ padding:28px 32px; position:relative; z-index:2; }}
    .hero-kicker {{ font-size:9px; letter-spacing:.12em; text-transform:uppercase; color:#bfe1cd; font-weight:900; margin-bottom:8px; }}
    .hero-title {{ font-size:27px; color:white; font-weight:900; line-height:1.15; }}
    .hero-sub {{ font-size:10px; color:#d8eee2; margin-top:9px; line-height:1.5; max-width:760px; }}
    .hero-pill {{ display:inline-block; margin-top:15px; padding:7px 11px; border-radius:20px; background:rgba(255,255,255,.13); border:1px solid rgba(255,255,255,.18); color:#f2fbf5; font-size:8px; font-weight:800; }}
    .stat-card {{ background:white; border:1px solid #dfe8e1; border-radius:15px; padding:15px 16px; min-height:108px; box-shadow:0 5px 18px rgba(22,65,45,.045); transition:transform .16s ease,box-shadow .16s ease; }}
    .stat-card:hover {{ transform:translateY(-2px); box-shadow:0 9px 22px rgba(22,65,45,.08); }}
    .stat-head {{ display:flex; justify-content:space-between; align-items:center; }}
    .stat-icon {{ width:34px; height:34px; border-radius:10px; background:#eaf5ed; display:flex; align-items:center; justify-content:center; font-size:16px; }}
    .stat-live {{ font-size:7px; color:#278457; background:#eaf7ee; padding:5px 7px; border-radius:20px; font-weight:900; }}
    .stat-value {{ font-size:24px; font-weight:900; color:#153d2d; margin-top:10px; line-height:1; }}
    .stat-label {{ font-size:8px; color:#77857d; margin-top:6px; }}
    .section-row {{ display:flex; align-items:flex-end; justify-content:space-between; margin:20px 0 9px; }}
    .section-title {{ font-size:13px; font-weight:900; color:#173f2f; }}
    .section-sub {{ font-size:8px; color:#909b95; margin-top:3px; }}
    .section-link {{ font-size:8px; color:#27764f; font-weight:900; }}
    .card {{ background:white; border:1px solid #dfe8e1; border-radius:15px; box-shadow:0 5px 18px rgba(22,65,45,.035); }}
    .feature {{ display:grid; grid-template-columns:54% 46%; min-height:330px; overflow:hidden; }}
    .feature-image {{ width:100%; height:100%; min-height:330px; object-fit:cover; display:block; }}
    .feature-copy {{ padding:25px; display:flex; flex-direction:column; justify-content:center; }}
    .tag {{ display:inline-block; width:max-content; font-size:7px; font-weight:900; color:#287e55; background:#eaf6ee; padding:5px 8px; border-radius:20px; text-transform:uppercase; }}
    .feature-title {{ font-size:20px; line-height:1.18; color:#153f2e; font-weight:900; margin-top:11px; }}
    .feature-body {{ font-size:9px; line-height:1.65; color:#66756d; margin-top:9px; }}
    .feature-meta {{ font-size:7px; color:#9aa49f; margin-top:13px; }}
    .right-card {{ padding:16px; min-height:330px; }}
    .activity-bars {{ height:190px; display:flex; align-items:end; gap:10px; padding:18px 7px 7px; border-bottom:1px solid #edf1ee; }}
    .bar-col {{ flex:1; height:100%; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; gap:6px; }}
    .bar {{ width:100%; max-width:24px; border-radius:7px 7px 3px 3px; background:linear-gradient(180deg,#51b57c,#17724a); min-height:5px; }}
    .bar-label {{ font-size:7px; color:#909b95; }}
    .legend {{ font-size:7px; color:#849089; margin-top:8px; }}
    .conversation-card {{ padding:10px 14px; }}
    .conversation-item {{ display:flex; align-items:center; gap:10px; padding:11px 0; border-bottom:1px solid #edf1ee; }}
    .conversation-item:last-child {{ border-bottom:0; }}
    .avatar {{ width:36px; height:36px; min-width:36px; border-radius:50%; background:#e6f1e9; display:flex; align-items:center; justify-content:center; font-size:14px; }}
    .conv-main {{ flex:1; min-width:0; }}
    .conv-name {{ font-size:9px; font-weight:900; color:#244d3a; }}
    .conv-msg {{ font-size:8px; color:#7d8982; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }}
    .conv-time {{ font-size:7px; color:#9aa49f; }}
    .product-card {{ overflow:hidden; background:white; border:1px solid #dfe8e1; border-radius:14px; box-shadow:0 5px 18px rgba(22,65,45,.035); height:100%; }}
    .product-img {{ width:100%; height:155px; object-fit:cover; display:block; background:#edf5ef; }}
    .product-placeholder {{ height:155px; background:linear-gradient(135deg,#edf6ef,#dfeee4); display:flex; align-items:center; justify-content:center; font-size:34px; color:#6ca27f; }}
    .product-content {{ padding:12px; }}
    .product-name {{ font-size:10px; font-weight:900; color:#194632; }}
    .product-desc {{ font-size:8px; color:#87928c; margin-top:5px; height:30px; overflow:hidden; line-height:1.45; }}
    .product-bottom {{ display:flex; justify-content:space-between; align-items:center; margin-top:10px; gap:8px; }}
    .price {{ font-size:10px; font-weight:900; color:#19704a; }}
    .stock-ok {{ font-size:7px; color:#278457; background:#e8f6ed; padding:4px 7px; border-radius:20px; font-weight:900; white-space:nowrap; }}
    .stock-low {{ font-size:7px; color:#ad741d; background:#fff3dc; padding:4px 7px; border-radius:20px; font-weight:900; white-space:nowrap; }}
    .page-heading {{ margin:5px 0 18px; }}
    .page-heading h2 {{ font-size:22px; color:#153f2e; font-weight:900; margin:0; }}
    .page-heading p {{ font-size:9px; color:#89948e; margin:5px 0 0; }}
    .pub-card {{ background:white; border:1px solid #dfe8e1; border-radius:15px; padding:17px; margin-bottom:12px; box-shadow:0 4px 16px rgba(22,65,45,.03); }}
    .pub-title {{ font-size:15px; font-weight:900; color:#173f2e; }}
    .pub-meta {{ font-size:8px; color:#919c96; margin-top:5px; }}
    .pub-body {{ font-size:10px; color:#53635b; line-height:1.6; margin-top:9px; }}
    .pub-image {{ width:100%; max-height:430px; object-fit:cover; border-radius:11px; margin-top:12px; display:block; }}
    .chat-shell {{ background:white; border:1px solid #dfe8e1; border-radius:15px; overflow:hidden; }}
    .chat-header {{ padding:15px 17px; border-bottom:1px solid #e8ede9; display:flex; align-items:center; gap:10px; }}
    .chat-title {{ font-size:12px; font-weight:900; color:#173f2e; }}
    .chat-role {{ font-size:8px; color:#8c9891; margin-top:3px; }}
    .chat-body {{ padding:17px; background:#f6faf7; min-height:440px; max-height:540px; overflow-y:auto; }}
    .chat-bubble {{ padding:10px 12px; border-radius:14px; max-width:76%; font-size:9px; line-height:1.55; margin-bottom:10px; word-break:break-word; }}
    .chat-mine {{ margin-left:auto; background:#116641; color:white; border-bottom-right-radius:5px; }}
    .chat-other {{ margin-right:auto; background:#e4eee8; color:#29463a; border-bottom-left-radius:5px; }}
    .stButton>button {{ border:1px solid #d7e3db!important; border-radius:10px!important; background:white!important; color:#285340!important; font-size:9px!important; font-weight:800!important; min-height:34px!important; box-shadow:none!important; transition:.15s ease; }}
    .stButton>button:hover {{ border-color:#8db8a0!important; color:#0b6540!important; background:#f6fbf8!important; }}
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"]>div {{ border-radius:10px!important; border-color:#d7e3db!important; background:white!important; font-size:10px!important; }}
    div[data-testid="stForm"] {{ border:1px solid #dfe8e1!important; border-radius:13px!important; padding:12px!important; background:white!important; }}
    .stFileUploader {{ font-size:9px!important; }}
    .lang-label {{ font-size:7px; color:#718078; margin-bottom:2px; }}
    </style>
    """)
# ================================================================
# NAVIGATION — source de vérité unique
# ================================================================
NAV_ITEMS = [
    ("home",         "🏠", "Tableau de bord"),
    ("publications", "📢", "Mes publications"),
    ("products",     "🛒", "Mes produits"),
    ("messages",     "💬", "Mes messages"),
    ("farmers",      "👥", "Mes agriculteurs"),
    ("profile",      "👤", "Mon profil"),
]
VALID_SECTIONS = {s for s, _, _ in NAV_ITEMS}


def go_to_section(section):
    if section not in VALID_SECTIONS:
        section = "home"
    st.session_state.cons_section = section


def nav(username, unread):
    """Sidebar - PC uniquement."""
    with st.sidebar:
        if LOGO_URI:
            H('<div class="brand"><div class="brand-logo"></div></div>')
        else:
            H('<div class="brand"><div class="brand-fallback">🌱 SMART FILAHA</div></div>')
        H('<div class="nav-caption">Navigation</div>')
        for section, icon, label in NAV_ITEMS:
            st.button(
                f"{icon} {label}",
                key=f"desktop_nav_{section}",
                use_container_width=True,
                on_click=go_to_section,
                args=(section,),
            )


def mobile_nav():
    """Menu boutons - téléphone uniquement (caché sur PC par CSS)."""
    current = st.session_state.get("cons_section", "home")
    with st.container(key="cons_mobile_nav"):
        for i in range(0, len(NAV_ITEMS), 2):
            cols = st.columns(2, gap="small")
            for col, (section, icon, label) in zip(cols, NAV_ITEMS[i:i + 2]):
                with col:
                    st.button(
                        f"{icon} {label}",
                        key=f"mobile_nav_{section}",
                        use_container_width=True,
                        on_click=go_to_section,
                        args=(section,),
                        type="primary" if section == current else "secondary",
                    )


def topbar(username, unread):
    H(f"""
    <div class="topbar">
        <div class="top-brand"></div>
        <div class="top-search">🔎&nbsp;&nbsp; {esc(t('search'))}</div>
        <div class="notif">🔔<span class="badge">{unread if unread else 0}</span></div>
        <div class="top-user">
            <div class="top-avatar">👨‍🌾</div>
            <div>
                <div class="top-user-name">{esc(username)}</div>
                <div class="top-user-role">Conseiller agricole</div>
            </div>
        </div>
    </div>
    """)

    mobile_nav()

    lc1, lc2 = st.columns([8.6, 1.4])
    with lc2:
        options = list(LANGS.keys())
        current_language_code = current_lang()
        selected = options[[v for v in LANGS.values()].index(current_language_code)]
        new_lang = st.selectbox(
            "Langue",
            options,
            index=options.index(selected),
            key="ui_language_select",
            label_visibility="collapsed",
        )
        if LANGS[new_lang] != current_lang():
            st.session_state.ui_lang = LANGS[new_lang]
            st.rerun()


# ================================================================
# HOME HELPERS
# ================================================================
def _product_image(product):
    uri = image_data_uri(getattr(product, "image_path", None))
    if uri:
        return f'<img class="product-img" src="{uri}" alt="Produit">'
    return '<div class="product-placeholder">🌱</div>'
def _publication_bars(pubs):
    days_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    days_ar = ["اث", "ثل", "أر", "خم", "جم", "سب", "أح"]
    days = days_ar if current_lang() == "ar" else days_fr
    counts = Counter()
    for p in pubs:
        dt = getattr(p, "created_at", None)
        if dt:
            try:
                counts[dt.weekday()] += 1
            except Exception:
                pass
    values = [counts[i] for i in range(7)]
    maximum = max(values) if any(values) else 1
    return "".join(
        f'<div class="bar-col">'
        f'<div class="bar" style="height:{max(6, int((v / maximum) * 112))}px"></div>'
        f'<div class="bar-label">{d}</div>'
        f'</div>'
        for d, v in zip(days, values)
    )
def _conversation_preview(conseiller_id, farmers):
    result = []
    for farmer in farmers:
        message = get_latest_message(conseiller_id, farmer.id)
        result.append((farmer, message))
    result.sort(
        key=lambda x: getattr(x[1], "created_at", None) if x[1] else 0,
        reverse=True
    )
    return result
# ================================================================
# HOME
# ================================================================
def home(conseiller_id, username, farmers, products_list, unread, pubs):
    H(f"""
    <div class="hero">
        <div class="hero-inner">
            <div class="hero-kicker">SMART FILAHA • ESPACE CONSEILLER</div>
            <div class="hero-title">{esc(t('hello'))} {esc(username)} 👋</div>
            <div class="hero-sub">{esc(t('hero_sub'))}</div>
            <div class="hero-pill">🌱 {esc(t('live'))} · Smart Filaha</div>
        </div>
    </div>
    """)
    stats = [
        ("📢", len(pubs),          t("pubs"),           t("content")),
        ("🛒", len(products_list), t("products_short"), t("catalog_current")),
        ("💬", unread,             t("messages_short"), t("farmers_contact")),
        ("👥", len(farmers),       t("farmers_short"),  t("contact")),
    ]
    cols = st.columns(4, gap="medium")
    for col, (icon, value, label, note) in zip(cols, stats):
        with col:
            H(
                f'<div class="stat-card">'
                f'<div class="stat-head">'
                f'<div class="stat-icon">{icon}</div>'
                f'<div class="stat-live">{esc(t("active"))}</div>'
                f'</div>'
                f'<div class="stat-value">{value}</div>'
                f'<div class="stat-label">{esc(label)} · {esc(note)}</div>'
                f'</div>'
            )
    left, right = st.columns([1.65, 1], gap="medium")
    # ── recent pub
    recent = None
    if pubs:
        recent = sorted(
            pubs,
            key=lambda p: getattr(p, "created_at", None) or 0,
            reverse=True
        )[0]
    with left:
        H(
            f'<div class="section-row">'
            f'<div>'
            f'<div class="section-title">📢 {esc(t("recent_pubs"))}</div>'
            f'<div class="section-sub">{esc(t("recent_pubs_sub"))}</div>'
            f'</div>'
            f'<div class="section-link">{esc(t("all_pubs"))}</div>'
            f'</div>'
        )
        if recent:
            uri = image_data_uri(getattr(recent, "image_path", None))
            image_html = (
                f'<img class="feature-image" src="{uri}" alt="Publication">'
                if uri else
                '<div class="product-placeholder">🌱</div>'
            )
            # ── FIX: calcul date avant f-string
            recent_date = fmt_date(getattr(recent, "created_at", None))
            recent_type = esc(getattr(recent, "publication_type", t("article"))).upper()
            H(f"""
            <div class="card feature">
                {image_html}
                <div class="feature-copy">
                    <span class="tag">{recent_type}</span>
                    <div class="feature-title">{esc(recent.title)}</div>
                    <div class="feature-body">{esc(recent.content)[:320]}</div>
                    <div class="feature-meta">{esc(t('published'))} {recent_date}</div>
                </div>
            </div>
            """)
        else:
            H(
                f'<div class="card" style="padding:70px;text-align:center;color:#89948e;font-size:9px;">'
                f'📢<br><br>{esc(t("no_pub"))}'
                f'</div>'
            )
        if st.button(f"{t('all_pubs')} →", key="all_pubs_home"):
            go_to_section("publications")
            st.rerun()
    with right:
        H(
            f'<div class="section-row">'
            f'<div>'
            f'<div class="section-title">📊 {esc(t("activity"))}</div>'
            f'<div class="section-sub">{esc(t("activity_sub"))}</div>'
            f'</div>'
            f'<div class="section-link">{esc(t("week"))}</div>'
            f'</div>'
        )
        H(
            f'<div class="card right-card">'
            f'<div class="section-title" style="font-size:9px;">{esc(t("recent_pubs"))}</div>'
            f'<div class="section-sub">Données réelles de vos publications</div>'
            f'<div class="activity-bars">{_publication_bars(pubs)}</div>'
            f'<div class="legend">● Publications</div>'
            f'</div>'
        )
        H(
            f'<div class="section-row" style="margin-top:14px;">'
            f'<div>'
            f'<div class="section-title">💬 {esc(t("conversations"))}</div>'
            f'<div class="section-sub">{esc(t("conversations_sub"))}</div>'
            f'</div>'
            f'</div>'
            f'<div class="card conversation-card">'
        )
        conversations = _conversation_preview(conseiller_id, farmers)[:4]
        if conversations:
            for farmer, message in conversations:
                preview = message.content if message else t("no_messages")
                # ── FIX: calcul date avant f-string
                msg_date = fmt_date(getattr(message, "created_at", None), False) if message else ""
                H(
                    f'<div class="conversation-item">'
                    f'<div class="avatar">👨‍🌾</div>'
                    f'<div class="conv-main">'
                    f'<div class="conv-name">{esc(farmer.username)}</div>'
                    f'<div class="conv-msg">{esc(preview)[:72]}</div>'
                    f'</div>'
                    f'<div class="conv-time">{msg_date}</div>'
                    f'</div>'
                )
        else:
            H(f'<div style="padding:24px;text-align:center;color:#89948e;font-size:8px;">{esc(t("no_conv"))}</div>')
        H('</div>')
        if st.button(f"{t('open_messages')} →", key="open_msg_home"):
            go_to_section("messages")
            st.rerun()
    H(
        f'<div class="section-row" style="margin-top:20px;">'
        f'<div>'
        f'<div class="section-title">🛒 {esc(t("popular_products"))}</div>'
        f'<div class="section-sub">{esc(t("popular_products_sub"))}</div>'
        f'</div>'
        f'<div class="section-link">{esc(t("catalog"))}</div>'
        f'</div>'
    )
    if not products_list:
        H(f'<div class="card" style="padding:35px;text-align:center;color:#89948e;font-size:9px;">🛒<br><br>{esc(t("no_product"))}</div>')
    else:
        pcols = st.columns(min(4, len(products_list)), gap="medium")
        for col, product in zip(pcols, products_list[:4]):
            with col:
                stock = int(getattr(product, "stock", 0) or 0)
                stock_cls = "stock-ok" if stock > 5 else "stock-low"
                stock_text = t("stock_ok") if stock > 5 else t("stock_low")
                price_val = float(getattr(product, "price", 0) or 0)
                H(
                    f'<div class="product-card">'
                    f'{_product_image(product)}'
                    f'<div class="product-content">'
                    f'<div class="product-name">{esc(product.name)}</div>'
                    f'<div class="product-desc">{esc(getattr(product, "description", ""))}</div>'
                    f'<div class="product-bottom">'
                    f'<div class="price">{price_val:.2f} DH</div>'
                    f'<span class="{stock_cls}">{esc(stock_text)} · {stock}</span>'
                    f'</div>'
                    f'</div>'
                    f'</div>'
                )
    if st.button(f"{t('manage_products')} →", key="manage_prod_home"):
        go_to_section("products")
        st.rerun()
# ================================================================
# MESSAGES
# ================================================================
def messages(conseiller_id, farmers):
    H(
        f'<div class="page-heading">'
        f'<h2>💬 {esc(t("messages"))}</h2>'
        f'<p>{esc(t("messages_page_sub"))}</p>'
        f'</div>'
    )
    if not farmers:
        H(f'<div class="card" style="padding:70px;text-align:center;color:#89948e;font-size:9px;">💬<br><br>{esc(t("no_conv"))}</div>')
        return
    ids = {farmer.id for farmer in farmers}
    if st.session_state.get("selected_farmer") not in ids:
        st.session_state.selected_farmer = farmers[0].id
    left, right = st.columns([.9, 2], gap="medium")
    with left:
        H(
            f'<div class="section-title" style="margin:4px 0 9px;">{esc(t("conversations_page"))}</div>'
            f'<div class="card" style="padding:8px 10px;">'
        )
        for farmer in farmers:
            latest = get_latest_message(conseiller_id, farmer.id)
            preview = latest.content if latest else t("no_messages")
            if st.button(
                f"👨‍🌾 {farmer.username}\n{preview[:38]}",
                key=f"cf_{farmer.id}",
                use_container_width=True
            ):
                st.session_state.selected_farmer = farmer.id
                st.rerun()
        H('</div>')
    fid = st.session_state.selected_farmer
    selected = next((f for f in farmers if f.id == fid), farmers[0])
    mark_conversation_read(conseiller_id, fid)
    conv = get_conversation(conseiller_id, fid)
    with right:
        H(
            f'<div class="chat-shell">'
            f'<div class="chat-header">'
            f'<div class="avatar">👨‍🌾</div>'
            f'<div>'
            f'<div class="chat-title">{esc(selected.username)}</div>'
            f'<div class="chat-role">{esc(t("active_conversation"))}</div>'
            f'</div>'
            f'</div>'
            f'<div class="chat-body">'
        )
        if not conv:
            H(f'<div style="text-align:center;padding:100px 10px;color:#89948e;font-size:9px;">{esc(t("no_messages"))}</div>')
        else:
            for message in conv:
                cls = "chat-mine" if message.sender_id == conseiller_id else "chat-other"
                H(f'<div class="chat-bubble {cls}">{esc(message.content)}</div>')
        H('</div></div>')
        with st.form(f"reply_{fid}", clear_on_submit=True):
            text = st.text_input(
                "message",
                placeholder=t("write_message"),
                label_visibility="collapsed"
            )
            if st.form_submit_button(t("send"), use_container_width=True) and text.strip():
                send_message(conseiller_id, fid, text)
                st.rerun()
# ================================================================
# PRODUCTS
# ================================================================
def products(conseiller_id, items):
    H(
        f'<div class="page-heading">'
        f'<h2>🛒 {esc(t("products"))}</h2>'
        f'<p>{esc(t("products_page_sub"))}</p>'
        f'</div>'
    )
    with st.expander(f"➕ {t('add_product')}"):
        n = st.text_input(t("product_name"), key="pn")
        d = st.text_area(t("description"), key="pd")
        product_image = st.file_uploader(
            "📷 Image du produit",
            type=["jpg", "jpeg", "png", "webp"],
            key="product_image_upload"
        )
        c1, c2 = st.columns(2)
        with c1:
            price = st.number_input(t("price"), min_value=0.0, step=1.0, key="pp")
        with c2:
            stock = st.number_input(t("stock"), min_value=0, step=1, key="ps")
        if st.button(t("add"), key="addp", use_container_width=True):
            if n.strip() and price > 0:
                image_path = save_product_image(product_image) if product_image else None
                add_product(conseiller_id, n.strip(), d.strip(), float(price), int(stock), image_path=image_path)
                st.success(t("added"))
                st.rerun()
            else:
                st.warning(t("fill_name_price"))
    if not items:
        H(f'<div class="card" style="padding:45px;text-align:center;color:#89948e;font-size:9px;">🛒<br><br>{esc(t("no_product"))}</div>')
        return
    cols = st.columns(3, gap="medium")
    for i, product in enumerate(items):
        with cols[i % 3]:
            stock = int(getattr(product, "stock", 0) or 0)
            stock_cls = "stock-ok" if stock > 5 else "stock-low"
            stock_text = t("stock_ok") if stock > 5 else t("stock_low")
            price_val = float(getattr(product, "price", 0) or 0)
            H(
                f'<div class="product-card">'
                f'{_product_image(product)}'
                f'<div class="product-content">'
                f'<div class="product-name">{esc(product.name)}</div>'
                f'<div class="product-desc" style="height:auto;min-height:30px;">'
                f'{esc(getattr(product, "description", ""))}</div>'
                f'<div class="product-bottom">'
                f'<div class="price">{price_val:.2f} DH</div>'
                f'<span class="{stock_cls}">{esc(stock_text)} · {stock}</span>'
                f'</div>'
                f'</div>'
                f'</div>'
            )
            if st.button(f"📢 {t('publish')}", key=f"publish_product_{product.id}", use_container_width=True):
                product_title = str(getattr(product, "name", "") or "").strip()
                product_description = str(getattr(product, "description", "") or "").strip()
                if not product_title:
                    st.warning(t("fill_title_content"))
                else:
                    create_publication(
                        conseiller_id,
                        product_title,
                        product_description or product_title,
                        publication_type="produit",
                        image_path=getattr(product, "image_path", None),
                        product_id=product.id,
                    )
                    st.success(t("pub_created"))
                    go_to_section("publications")
                    st.rerun()
            if st.button(f"🗑️ {t('delete')}", key=f"dp_{product.id}", use_container_width=True):
                delete_product(product.id)
                st.rerun()
# ================================================================
# PUBLICATIONS
# ================================================================
def publications(conseiller_id, products_list, pubs):
    H(
        f'<div class="page-heading">'
        f'<h2>📢 {esc(t("publications"))}</h2>'
        f'<p>{esc(t("pub_page_sub"))}</p>'
        f'</div>'
    )
    with st.expander(f"➕ {t('new_pub')}"):
        title = st.text_input(t("title"), key="pt")
        typ = st.selectbox(t("type"), ["conseil", "article", "annonce", "produit"], key="pty")
        content = st.text_area(t("description"), key="pc")
        image = st.file_uploader(t("image_optional"), type=["jpg", "jpeg", "png"], key="pi")
        linked = None
        if typ == "produit" and products_list:
            mapping = {p.id: p.name for p in products_list}
            linked = st.selectbox(
                t("link_product"),
                list(mapping),
                format_func=lambda x: mapping[x],
                key="pl"
            )
        if st.button(t("publish"), key="pubbtn", use_container_width=True):
            if title.strip() and content.strip():
                path = save_publication_image(image) if image else None
                create_publication(
                    conseiller_id, title.strip(), content.strip(),
                    publication_type=typ, image_path=path, product_id=linked
                )
                st.success(t("pub_created"))
                st.rerun()
            else:
                st.warning(t("fill_title_content"))
    if not pubs:
        H(f'<div class="card" style="padding:45px;text-align:center;color:#89948e;font-size:9px;">📢<br><br>{esc(t("no_pub"))}</div>')
        return
    for publication in pubs:
        uri = image_data_uri(getattr(publication, "image_path", None))
        image_html = f'<img class="pub-image" src="{uri}" alt="Publication">' if uri else ""
        # ── FIX: calcul date avant f-string
        pub_date = fmt_date(getattr(publication, "created_at", None))
        H(
            f'<div class="pub-card">'
            f'<div class="pub-title">{esc(publication.title)}</div>'
            f'<div class="pub-meta">'
            f'{esc(publication.publication_type)} · {esc(publication.status)} · {pub_date}'
            f'</div>'
            f'<div class="pub-body">{esc(publication.content)}</div>'
            f'{image_html}'
            f'</div>'
        )
        if st.button(f"🗑️ {t('delete')}", key=f"dpub_{publication.id}"):
            delete_publication(publication.id, conseiller_id)
            st.rerun()
# ================================================================
# FARMERS
# ================================================================
def farmers_section(conseiller_id, farmers):
    H(
        f'<div class="page-heading">'
        f'<h2>👥 {esc(t("farmers"))}</h2>'
        f'<p>{esc(t("farmers_page_sub"))}</p>'
        f'</div>'
    )
    if not farmers:
        H(f'<div class="card" style="padding:45px;text-align:center;color:#89948e;font-size:9px;">{esc(t("no_conv"))}</div>')
        return
    cols = st.columns(3, gap="medium")
    for i, farmer in enumerate(farmers):
        with cols[i % 3]:
            H(
                f'<div class="card" style="padding:18px;margin-bottom:8px;text-align:center;">'
                f'<div class="avatar" style="margin:0 auto 9px;">👨‍🌾</div>'
                f'<div style="font-size:11px;font-weight:900;color:#173f2e;">{esc(farmer.username)}</div>'
                f'<div style="font-size:8px;color:#89948e;margin-top:3px;">{esc(t("farmer"))}</div>'
                f'</div>'
            )
            if st.button(f"💬 {t('open_conversation')}", key=f"fc_{farmer.id}", use_container_width=True):
                st.session_state.selected_farmer = farmer.id
                go_to_section("messages")
                st.rerun()
# ================================================================
# PROFILE
# ================================================================
def profile(conseiller_id, username):
    H(
        f'<div class="page-heading">'
        f'<h2>👤 {esc(t("profile"))}</h2>'
        f'<p>{esc(t("profile_sub"))}</p>'
        f'</div>'
        f'<div class="card" style="padding:16px;margin-bottom:12px;">'
        f'<div style="font-size:13px;font-weight:900;color:#173f2e;">{esc(username)}</div>'
        f'<div style="font-size:8px;color:#89948e;margin-top:4px;">Conseiller agricole</div>'
        f'</div>'
    )
    with st.form("profile_form"):
        p1 = st.text_input(t("new_password"), type="password")
        p2 = st.text_input(t("confirm_password"), type="password")
        if st.form_submit_button(t("save"), use_container_width=True):
            if p1 and p1 != p2:
                st.error(t("password_mismatch"))
            elif p1:
                from auth.login import hash_password
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == conseiller_id).first()
                    if user:
                        user.password = hash_password(p1)
                        db.commit()
                        st.success(t("updated"))
                finally:
                    db.close()
            else:
                st.info(t("no_change"))
# ================================================================
# ENTRY POINT
# ================================================================
def render_conseiller():
    conseiller_id = st.session_state.get("user_id")
    if not conseiller_id:
        st.error("Utilisateur non connecté.")
        return
    username = st.session_state.get("username", "")
    styles()
    set_direction()
    farmers      = get_my_farmers(conseiller_id)
    products_list = get_my_products(conseiller_id)
    pubs         = get_my_publications(conseiller_id)
    unread       = get_unread_count(conseiller_id)
    nav(username, unread)
    topbar(username, unread)
    section = st.session_state.get("cons_section", "home")
    if section == "home":
        home(conseiller_id, username, farmers, products_list, unread, pubs)
    elif section == "messages":
        messages(conseiller_id, farmers)
    elif section == "products":
        products(conseiller_id, products_list)
    elif section == "publications":
        publications(conseiller_id, products_list, pubs)
    elif section == "farmers":
        farmers_section(conseiller_id, farmers)
    elif section == "profile":
        profile(conseiller_id, username)
    else:
        go_to_section("home")
        st.rerun()