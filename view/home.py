# view/home.py
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import datetime
import os
import base64

from config.settings import COLORS, MODEL_PATH, CLASS_NAMES_PATH, IMG_SIZE
from auth.login import is_admin, logout
from database.db import SessionLocal
from database.models import Analysis, User

from data.translations import TRANSLATIONS
from data.disease_data import DISEASE_DATA, GENERIC_ADVICE, PLANT_NAMES
from data.info_data import INFO_DATA
from data.season_data import SEASONS
from data.expert_data import EXPERT_INFO
from view.chat import render_chat_embedded

C = COLORS

SF = {
    "sidebar_bg": "#103326",
    "sidebar_bg_2": "#0B241A",
    "sidebar_text": "#C9D9D0",
    "sidebar_active": "#1E6246",
    "page_bg": "#F4F7F3",
    "card_bg": "#FFFFFF",
    "card_border": "#E2EAE4",
    "text_dark": "#18362A",
    "text_mid": "#6C7D73",
    "text_muted": "#91A198",
    "accent": "#1E7A46",
    "accent_light": "#E8F5EC",
    "warn": "#D99A22",
    "warn_light": "#FFF5DE",
}

@st.cache_resource
def load_model():
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASS_NAMES_PATH) as f:
        class_names = json.load(f)
    return model, class_names

def save_analysis(user_id, disease_key, disease_name, plant_type, confidence, severity, language):
    db = SessionLocal()
    try:
        analysis = Analysis(
            user_id=user_id, disease_key=disease_key, disease_name=disease_name,
            plant_type=plant_type, confidence=confidence, severity=severity,
            language=language, source="image"
        )
        db.add(analysis)
        db.commit()
    finally:
        db.close()

def _logo_path():
    for path in ("assets/logof.png", "assets/Logof.png", "assets/logo.png"):
        if os.path.exists(path):
            return path
    return None

def render_logo(width=150):
    path = _logo_path()
    if path:
        st.image(path, width=width)
    else:
        st.markdown(
            '<div style="font-size:20px;font-weight:800;color:#18362A;">🌿 Smart Filaha</div>',
            unsafe_allow_html=True
        )

def _file_data_uri(path):
    ext = path.split(".")[-1].lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
            "webp": "image/webp"}.get(ext, "image/png")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"

def _hero_bg_path():
    for p in ("assets/hero-bg.jpg", "assets/hero-bg.png",
              "assets/hero_bg.jpg", "assets/hero_bg.png",
              "assets/hero.jpg", "assets/hero.png"):
        if os.path.exists(p):
            return p
    return None

def inject_css():
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{ background:{SF["page_bg"]}; }}
    [data-testid="stHeader"] {{ background:transparent; }}
    .block-container {{ padding:8px 28px 34px !important; max-width:100% !important; }}
    /* Header spacing: keep the existing design, only remove the excessive empty space above it. */
    [data-testid="stSelectbox"] {{ margin-bottom:-6px !important; }}

    [data-testid="stSidebar"] {{
        background:linear-gradient(180deg,{SF["sidebar_bg"]} 0%,{SF["sidebar_bg_2"]} 100%) !important;
        border-right:0 !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        background:transparent !important;
        color:{SF["sidebar_text"]} !important;
        border:1px solid transparent !important;
        border-radius:12px !important;
        text-align:left !important;
        font-size:14px !important;
        font-weight:500 !important;
        padding:11px 13px !important;
        margin:3px 0 !important;
        box-shadow:none !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{
        background:rgba(255,255,255,.08) !important;
        color:#FFFFFF !important;
    }}

    .stButton > button {{
        border-radius:11px !important;
        border:0 !important;
        font-weight:600 !important;
    }}

    .sf-hero {{
        position:relative;overflow:hidden;
        background:
            radial-gradient(circle at 85% 20%,rgba(129,194,148,.28),transparent 25%),
            linear-gradient(120deg,#123E2C 0%,#1D5A3F 58%,#2A7650 100%);
        border-radius:22px;padding:28px 30px;color:white;min-height:170px;
        box-shadow:0 12px 28px rgba(20,72,48,.13);
    }}
    .sf-hero:after {{
        content:"🌱";position:absolute;right:42px;bottom:-14px;
        font-size:118px;opacity:.11;transform:rotate(-10deg);
    }}
    .sf-hero-kicker {{
        color:#BFE2CB;font-size:11px;font-weight:700;
        letter-spacing:.08em;text-transform:uppercase;margin-bottom:7px;
    }}
    .sf-hero h2 {{ margin:0 0 8px 0;font-size:27px;font-weight:800;letter-spacing:-.02em; }}
    .sf-hero p {{ margin:0;max-width:620px;font-size:13px;line-height:1.6;color:#E0EEE5; }}
    .sf-hero-badge {{
        position:absolute;right:28px;top:26px;background:rgba(255,255,255,.12);
        border:1px solid rgba(255,255,255,.16);border-radius:13px;
        padding:9px 13px;font-size:11px;color:#F4FBF6;
    }}

    .sf-stat {{
        background:{SF["card_bg"]};border:1px solid {SF["card_border"]};
        border-radius:15px;padding:15px 16px;min-height:105px;
        box-shadow:0 4px 16px rgba(22,61,42,.035);
    }}
    .sf-stat-top {{ display:flex;align-items:center;justify-content:space-between;margin-bottom:12px; }}
    .sf-stat-icon {{
        width:34px;height:34px;border-radius:10px;
        display:flex;align-items:center;justify-content:center;font-size:17px;
    }}
    .sf-stat-val {{ font-size:25px;font-weight:800;color:{SF["text_dark"]};line-height:1; }}
    .sf-stat-label {{ font-size:11px;color:{SF["text_mid"]};margin-top:7px; }}

    .sf-card {{
        background:{SF["card_bg"]};border:1px solid {SF["card_border"]};
        border-radius:17px;padding:18px 19px;
        box-shadow:0 5px 20px rgba(22,61,42,.045);
    }}
    .sf-section-title {{ color:{SF["text_dark"]};font-size:15px;font-weight:750;margin-bottom:4px; }}
    .sf-section-sub {{ color:{SF["text_mid"]};font-size:11px;margin-bottom:14px; }}

    .sf-map {{
        height:305px;border-radius:14px;overflow:hidden;position:relative;
        border:1px solid #D9E4DB;
        background:
            linear-gradient(135deg,rgba(255,255,255,.16) 25%,transparent 25%) 0 0/24px 24px,
            linear-gradient(45deg,rgba(255,255,255,.11) 25%,transparent 25%) 0 0/24px 24px,
            #BFD6C3;
    }}
    .sf-map-road {{
        position:absolute;left:8%;top:50%;width:85%;height:9px;
        background:#E9E2C9;transform:rotate(-13deg);border-radius:99px;opacity:.9;
    }}
    .sf-field {{
        position:absolute;border:3px solid rgba(29,105,63,.72);
        background:rgba(76,157,101,.28);border-radius:12px;
    }}
    .sf-pin {{
        position:absolute;width:13px;height:13px;border-radius:50%;
        border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,.22);
    }}
    .sf-map-legend {{
        position:absolute;top:12px;right:12px;background:rgba(255,255,255,.91);
        border:1px solid rgba(255,255,255,.8);border-radius:11px;padding:9px 11px;
        font-size:10px;color:{SF["text_dark"]};box-shadow:0 5px 14px rgba(0,0,0,.08);
    }}
    .sf-legend-row {{ margin:4px 0;display:flex;align-items:center;gap:6px; }}
    .sf-dot {{ width:8px;height:8px;border-radius:50%;display:inline-block; }}

    .sf-ai {{
        background:linear-gradient(180deg,#F3FAF5 0%,#FFFFFF 100%);
        border:1px solid #DCEBE0;border-radius:17px;padding:18px;min-height:385px;
        box-shadow:0 5px 20px rgba(22,61,42,.045);
    }}
    .sf-ai-head {{ display:flex;justify-content:space-between;align-items:center;margin-bottom:14px; }}
    .sf-ai-title {{ color:{SF["text_dark"]};font-size:15px;font-weight:800; }}
    .sf-online {{ background:#E4F6E9;color:#287347;border-radius:20px;padding:5px 9px;font-size:10px;font-weight:700; }}
    .sf-chat-msg {{
        background:white;border:1px solid #E3ECE6;border-radius:13px 13px 13px 4px;
        padding:12px 13px;font-size:12px;color:{SF["text_dark"]};line-height:1.55;margin-bottom:12px;
    }}
    .sf-chip {{
        display:inline-block;background:white;border:1px solid #DDE8E0;border-radius:20px;
        padding:7px 11px;font-size:10px;color:{SF["text_dark"]};margin:3px 3px 3px 0;
    }}
    .sf-ai-status {{
        margin-top:18px;padding:11px 12px;border-radius:12px;background:#F5F9F6;
        border:1px solid #E1EAE4;font-size:10px;color:{SF["text_mid"]};
    }}

    .stTextInput > div > div > input {{
        background:#FFFFFF !important;border:1px solid {SF["card_border"]} !important;
        border-radius:11px !important;color:{SF["text_dark"]} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

UI_TEXT = {
    "Français": {
        "nav_home":"Accueil","nav_analysis":"IA & Analyse","nav_map":"Cartographie","nav_doc":"Documentation","nav_chat":"Chatbot IA","nav_images":"Mes images","nav_settings":"Paramètres","nav_sensors":"Mes capteurs","nav_publications":"Publications","nav_messages":"Messages","nav_profile":"Mon profil","nav_logout":"Déconnexion","nav_admin":"Administration",
        "nav_desc":"Analyse des plantes, suivi agricole et informations utiles.","language":"Langue","search":"Rechercher une culture, une maladie, une information...","user":"Utilisateur",
        "hero_kicker":"SMART FILAHA • ESPACE AGRICULTEUR","hero_title":"Bonjour {user}, prêt à analyser vos cultures ?","hero_desc":"Utilisez l'intelligence artificielle pour analyser une photo de plante, identifier une maladie et consulter les informations agricoles disponibles.","smart_agri":"Agriculture intelligente",
        "stat_crops":"Cultures suivies","stat_images":"Images analysées","stat_alerts":"Alertes détectées","stat_fields":"Parcelles surveillées",
        "map_title":"Ma carte agricole","map_sub":"Vue de vos parcelles et état général des cultures","map_health":"Bonne santé","map_watch":"Surveillance","map_alert":"Alerte","map_note":"Carte interactive — emplacement à connecter à votre API","zones":"zones",
        "ai_title":"Assistant IA agricole","available":"Disponible","ai_msg":"Bonjour 👋<br>Je peux vous aider à comprendre les maladies des plantes, les cultures, les saisons et les informations agricoles.","quick_questions":"QUESTIONS RAPIDES","common":"Maladies fréquentes","yield":"Améliorer le rendement","season":"Saison idéale","consult_doc":"Consulter la documentation","ai_status":"L'interface est prête à accueillir vos connexions IA et capteurs, sans modifier la logique actuelle de l'application.","ai_analysis":"Analyse IA",
        "quick":"Accès rapide","take_photo":"Prendre une photo","import_image":"Importer une image","quick_doc":"Documentation","assistant":"Assistant IA","camera_hint":"Analyser une plante avec la caméra","gallery_hint":"Depuis votre galerie","doc_hint":"Fiches, guides et conseils","question_hint":"Poser une question",
        "source":"Source de l'image","camera":"Prendre une photo","upload":"Importer une image","camera_prompt":"Prenez une photo de la plante","search_results":"Résultats pour","no_search":"Aucun résultat correspondant — essayez un autre mot.","healthy":"Saine ✓","mild":"Légère","moderate":"Modérée","severe":"Grave",
        "upload_or_camera":"Prenez une photo ou importez une image pour lancer l'analyse.","status":"Utilisateur"
    },
    "English": {
        "nav_home":"Home","nav_analysis":"AI & Analysis","nav_map":"Mapping","nav_doc":"Documentation","nav_chat":"AI Chatbot","nav_images":"My images","nav_settings":"Settings","nav_sensors":"My sensors","nav_publications":"Publications","nav_messages":"Messages","nav_profile":"My profile","nav_logout":"Log out","nav_admin":"Administration",
        "nav_desc":"Plant analysis, agricultural monitoring and useful information.","language":"Language","search":"Search for a crop, disease, or information...","user":"User",
        "hero_kicker":"SMART FILAHA • FARMER AREA","hero_title":"Hello {user}, ready to analyze your crops?","hero_desc":"Use artificial intelligence to analyze a plant photo, identify a disease, and access available agricultural information.","smart_agri":"Smart agriculture",
        "stat_crops":"Crops tracked","stat_images":"Images analyzed","stat_alerts":"Alerts detected","stat_fields":"Fields monitored",
        "map_title":"My agricultural map","map_sub":"View of your fields and overall crop status","map_health":"Healthy","map_watch":"Monitoring","map_alert":"Alert","map_note":"Interactive map — location to connect to your API","zones":"zones",
        "ai_title":"AI Agricultural Assistant","available":"Available","ai_msg":"Hello 👋<br>I can help you understand plant diseases, crops, seasons and agricultural information.","quick_questions":"QUICK QUESTIONS","common":"Common diseases","yield":"Improve yield","season":"Ideal season","consult_doc":"View documentation","ai_status":"The interface is ready for your AI and sensor connections without changing the current application logic.","ai_analysis":"AI analysis",
        "quick":"Quick access","take_photo":"Take a photo","import_image":"Import an image","quick_doc":"Documentation","assistant":"AI Assistant","camera_hint":"Analyze a plant with the camera","gallery_hint":"From your gallery","doc_hint":"Guides, sheets and advice","question_hint":"Ask a question",
        "source":"Image source","camera":"Take a photo","upload":"Import an image","camera_prompt":"Take a photo of the plant","search_results":"Results for","no_search":"No matching result — try another word.","healthy":"Healthy ✓","mild":"Mild","moderate":"Moderate","severe":"Severe",
        "upload_or_camera":"Take a photo or import an image to start the analysis.","status":"User"
    },
    "العربية": {
        "nav_home":"الرئيسية","nav_analysis":"الذكاء الاصطناعي والتحليل","nav_map":"الخريطة","nav_doc":"التوثيق","nav_chat":"المساعد الذكي","nav_images":"صوري","nav_settings":"الإعدادات","nav_sensors":"مستشعراتي","nav_publications":"المنشورات","nav_messages":"الرسائل","nav_profile":"ملفي الشخصي","nav_logout":"تسجيل الخروج","nav_admin":"الإدارة",
        "nav_desc":"تحليل النباتات، المتابعة الزراعية والمعلومات المفيدة.","language":"اللغة","search":"ابحث عن محصول أو مرض أو معلومة...","user":"مستخدم",
        "hero_kicker":"سمارت فلاح • مساحة الفلاح","hero_title":"مرحباً {user}، هل أنت مستعد لتحليل محاصيلك؟","hero_desc":"استخدم الذكاء الاصطناعي لتحليل صورة نبات، تحديد المرض والاطلاع على المعلومات الزراعية المتاحة.","smart_agri":"الزراعة الذكية",
        "stat_crops":"المحاصيل المتابعة","stat_images":"الصور المحللة","stat_alerts":"التنبيهات المكتشفة","stat_fields":"القطع المراقبة",
        "map_title":"خريطتي الزراعية","map_sub":"عرض القطع وحالة المحاصيل بشكل عام","map_health":"حالة جيدة","map_watch":"مراقبة","map_alert":"تنبيه","map_note":"خريطة تفاعلية — سيتم ربط الموقع بواجهة API","zones":"مناطق",
        "ai_title":"المساعد الزراعي بالذكاء الاصطناعي","available":"متاح","ai_msg":"مرحباً 👋<br>يمكنني مساعدتك في فهم أمراض النباتات والمحاصيل والمواسم والمعلومات الزراعية.","quick_questions":"أسئلة سريعة","common":"الأمراض الشائعة","yield":"تحسين الإنتاجية","season":"الموسم المناسب","consult_doc":"استعراض التوثيق","ai_status":"الواجهة جاهزة لربط الذكاء الاصطناعي والمستشعرات دون تغيير منطق التطبيق الحالي.","ai_analysis":"تحليل بالذكاء الاصطناعي",
        "quick":"الوصول السريع","take_photo":"التقاط صورة","import_image":"استيراد صورة","quick_doc":"التوثيق","assistant":"المساعد الذكي","camera_hint":"حلل نباتاً بالكاميرا","gallery_hint":"من معرض الصور","doc_hint":"بطاقات وأدلة ونصائح","question_hint":"اطرح سؤالاً",
        "source":"مصدر الصورة","camera":"التقاط صورة","upload":"استيراد صورة","camera_prompt":"التقط صورة للنبات","search_results":"نتائج البحث عن","no_search":"لا توجد نتيجة مطابقة — جرّب كلمة أخرى.","healthy":"سليم ✓","mild":"خفيفة","moderate":"متوسطة","severe":"خطيرة",
        "upload_or_camera":"التقط صورة أو استورد صورة لبدء التحليل.","status":"مستخدم"
    },
    "دارجة": {
        "nav_home":"الرئيسية","nav_analysis":"IA والتحليل","nav_map":"الخريطة","nav_doc":"التوثيق","nav_chat":"Chatbot IA","nav_images":"تصاوري","nav_settings":"الإعدادات","nav_sensors":"الكابتورات ديالي","nav_publications":"المنشورات","nav_messages":"الميساجات","nav_profile":"البروفايل ديالي","nav_logout":"تسجيل الخروج","nav_admin":"الإدارة",
        "nav_desc":"تحليل النباتات، التتبع الفلاحي والمعلومات المفيدة.","language":"اللغة","search":"قلب على زرع، مرض ولا معلومة...","user":"مستعمل",
        "hero_kicker":"SMART FILAHA • فضاء الفلاح","hero_title":"سلام {user}، واجد تحلل الزرع ديالك؟","hero_desc":"استعمل الذكاء الاصطناعي باش تحلل تصويرة ديال النبتة، تعرف المرض وتشوف المعلومات الفلاحية المتوفرة.","smart_agri":"الفلاحة الذكية",
        "stat_crops":"الزراعات المتبعة","stat_images":"التصاور المحللة","stat_alerts":"التنبيهات المكتاشفة","stat_fields":"القطع المراقبة",
        "map_title":"الخريطة الفلاحية ديالي","map_sub":"شوف القطع ديالك والحالة العامة ديال الزرع","map_health":"صحة مزيانة","map_watch":"مراقبة","map_alert":"تنبيه","map_note":"خريطة تفاعلية — الموقع غادي يتربط مع API","zones":"مناطق",
        "ai_title":"المساعد الفلاحي IA","available":"متوفر","ai_msg":"سلام 👋<br>نقدر نعاونك تفهم أمراض النباتات، الزراعات، المواسم والمعلومات الفلاحية.","quick_questions":"أسئلة سريعة","common":"الأمراض اللي كيتعاودو بزاف","yield":"حسن المردودية","season":"الموسم المناسب","consult_doc":"شوف التوثيق","ai_status":"الواجهة واجدة باش نربطو IA والكابتورات بلا ما نبدلو المنطق الحالي ديال التطبيق.","ai_analysis":"تحليل IA",
        "quick":"ولوج سريع","take_photo":"صور تصويرة","import_image":"دخل تصويرة","quick_doc":"التوثيق","assistant":"المساعد IA","camera_hint":"حلل النبتة بالكاميرا","gallery_hint":"من الغاليري","doc_hint":"معلومات وأدلة ونصائح","question_hint":"طرح سؤال",
        "source":"مصدر التصويرة","camera":"صور تصويرة","upload":"دخل تصويرة","camera_prompt":"صور تصويرة ديال النبتة","search_results":"نتائج البحث على","no_search":"ما لقيت والو مطابق — جرب كلمة أخرى.","healthy":"سليمة ✓","mild":"خفيفة","moderate":"متوسطة","severe":"خطيرة",
        "upload_or_camera":"صور تصويرة ولا دخل صورة باش تبدا التحليل.","status":"مستعمل"
    }
}

def U(lang, key, default=None, **kwargs):
    value = UI_TEXT.get(lang, UI_TEXT["Français"]).get(key, default if default is not None else key)
    try:
        return value.format(**kwargs)
    except Exception:
        return value

def apply_language_direction(lang):
    direction = TRANSLATIONS.get(lang, {}).get("dir", "ltr")
    st.markdown(f"""<style>
    .language-{direction} {{ direction:{direction}; }}
    [data-testid=stAppViewContainer] {{ direction:{direction}; }}
    .sf-hero, .sf-card, .sf-ai, .sf-stat {{ direction:{direction}; }}
    </style>""", unsafe_allow_html=True)

def render_sidebar(lang="Français"):
    with st.sidebar:
        logo = _logo_path()
        if logo:
            st.image(logo, width=185)
        else:
            st.markdown(
                '<div style="color:white;font-size:18px;font-weight:800;padding:12px 4px;">🌿 Smart Filaha</div>',
                unsafe_allow_html=True
            )

        st.markdown(
            f'<div style="height:1px;background:rgba(255,255,255,.10);margin:8px 4px 14px;"></div>'
            f'<div style="color:#87B49A;font-size:10px;font-weight:700;letter-spacing:.08em;'
            f'text-transform:uppercase;padding:0 12px 7px;">{U(lang, "nav_home")}</div>',
            unsafe_allow_html=True
        )

        current = st.session_state.get("home_view", "accueil")
        nav_items = [
            ("accueil", f"🏠  {U(lang, 'nav_home')}"),
            ("analyse", f"🔬  {U(lang, 'nav_analysis')}"),
            ("carto", f"🗺️  {U(lang, 'nav_map')}"),
            ("doc", f"📚  {U(lang, 'nav_doc')}"),
            ("chatbot", f"🤖  {U(lang, 'nav_chat')}"),
            ("images", f"🖼️  {U(lang, 'nav_images')}"),
            ("profil", f"⚙️  {U(lang, 'nav_settings')}"),
        ]

        for key, label in nav_items:
            active = key == current
            if st.button(
                label,
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.home_view = key
                st.rerun()

        # ── pages mostaqilin (page=..., machi home_view) ──
        st.markdown("<div style='height:2px'></div>", unsafe_allow_html=True)
        if st.button(f"📡  {U(lang, 'nav_sensors')}", key="nav_sensors", use_container_width=True):
            st.session_state.page = "sensors"
            st.rerun()
        if st.button(f"📢  {U(lang, 'nav_publications')}", key="nav_publications", use_container_width=True):
            st.session_state.page = "publications"
            st.rerun()
        if st.button(f"💬  {U(lang, 'nav_messages')}", key="nav_messages", use_container_width=True):
            st.session_state.page = "messages"
            st.rerun()

        if is_admin():
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button(f"🛠️  {U(lang, 'nav_admin')}", key="nav_admin", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()

        st.markdown(
            f'<div style="margin-top:24px;padding:14px;border-radius:14px;'
            f'background:rgba(255,255,255,.055);border:1px solid rgba(255,255,255,.07);'>
            f'<div style="font-size:18px;margin-bottom:7px;">🌱</div>'
            f'<div style="color:#E7F1EA;font-size:11px;font-weight:700;">{U(lang, "smart_agri")}</div>'
            f'<div style="color:#91ADA0;font-size:9px;line-height:1.5;margin-top:4px;">'
            f'{U(lang, "nav_desc")}</div></div>',
            unsafe_allow_html=True
        )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button(f"🚪  {U(lang, 'nav_logout')}", key="nav_logout", use_container_width=True):
            logout()
            st.rerun()


def render_mobile_user_menu(lang="Français"):
    """Mobile navigation for the user area.

    IMPORTANT:
    The complete menu (header + buttons) is inside the same keyed
    Streamlit container. This is what makes the PC/mobile CSS reliable.

    Desktop / PC: completely hidden.
    Phone / small screens: visible as a 2-column menu.
    """

    st.markdown(
        """
        <style>
        /* =========================================================
           SMART FILAHA - MOBILE USER MENU
           The whole Streamlit container is hidden on PC.
           ========================================================= */

        /* PC / desktop */
        .st-key-user_mobile_menu {
            display: none !important;
        }

        /* Phone / tablet */
        @media (max-width: 768px) {

            .st-key-user_mobile_menu {
                display: block !important;
                width: 100% !important;
                margin: 0 0 14px 0 !important;
                padding: 0 !important;
            }

            .st-key-user_mobile_menu [data-testid="stVerticalBlock"] {
                gap: 0.45rem !important;
            }

            .st-key-user_mobile_menu .mobile-user-brand {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 10px;
                padding: 11px 13px;
                border-radius: 14px;
                background: linear-gradient(135deg, #103326, #1E6246);
                box-shadow: 0 6px 18px rgba(16, 51, 38, .14);
                margin-bottom: 8px;
            }

            .st-key-user_mobile_menu .mobile-user-brand-left {
                display: flex;
                align-items: center;
                gap: 9px;
                min-width: 0;
            }

            .st-key-user_mobile_menu .mobile-user-logo {
                width: 35px;
                height: 35px;
                object-fit: contain;
                background: #fff;
                border-radius: 9px;
                padding: 3px;
                flex: 0 0 auto;
            }

            .st-key-user_mobile_menu .mobile-user-title {
                color: #fff;
                font-size: 13px;
                font-weight: 800;
                line-height: 1.1;
            }

            .st-key-user_mobile_menu .mobile-user-sub {
                color: #C9D9D0;
                font-size: 9px;
                margin-top: 3px;
            }

            .st-key-user_mobile_menu .mobile-user-menu-icon {
                color: #fff;
                font-size: 19px;
                line-height: 1;
            }

            .st-key-user_mobile_menu [data-testid="column"] {
                padding: 0 !important;
            }

            .st-key-user_mobile_menu .stButton {
                margin: 0 !important;
            }

            .st-key-user_mobile_menu .stButton > button {
                width: 100% !important;
                min-height: 43px !important;
                padding: 7px 5px !important;
                border-radius: 10px !important;
                border: 1px solid #DCE8E1 !important;
                background: #FFFFFF !important;
                color: #18362A !important;
                font-size: 11px !important;
                font-weight: 750 !important;
                box-shadow: none !important;
                white-space: normal !important;
                line-height: 1.2 !important;
            }

            .st-key-user_mobile_menu .stButton > button:hover {
                background: #E8F5EC !important;
                border-color: #9AC6A9 !important;
                color: #145337 !important;
            }

            .st-key-user_mobile_menu .stButton > button:focus {
                box-shadow: 0 0 0 2px rgba(30, 122, 70, .12) !important;
            }

            /* Mobile page width only. Desktop is untouched. */
            .block-container {
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-top: 10px !important;
                padding-bottom: 30px !important;
                max-width: 100% !important;
            }

            /* The desktop sidebar should not be forced open on phones. */
            [data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    current = st.session_state.get("home_view", "accueil")
    page = st.session_state.get("page", "home")

    items = [
        ("home", "accueil", "🏠", U(lang, "nav_home")),
        ("home", "analyse", "🔬", U(lang, "nav_analysis")),
        ("home", "carto", "🗺️", U(lang, "nav_map")),
        ("home", "doc", "📚", U(lang, "nav_doc")),
        ("home", "chatbot", "🤖", U(lang, "nav_chat")),
        ("home", "images", "🖼️", U(lang, "nav_images")),
        ("sensors", None, "📡", U(lang, "nav_sensors")),
        ("publications", None, "📢", U(lang, "nav_publications")),
        ("messages", None, "💬", U(lang, "nav_messages")),
        ("profile", None, "⚙️", U(lang, "nav_profile")),
    ]

    # IMPORTANT: header AND buttons are all inside this container.
    # Therefore display:none really hides the complete menu on PC.
    with st.container(key="user_mobile_menu"):

        logo_path = _logo_path()
        if logo_path:
            logo_html = f'<img class="mobile-user-logo" src="{_file_data_uri(logo_path)}">'
        else:
            logo_html = '<div class="mobile-user-logo" style="display:flex;align-items:center;justify-content:center;">🌿</div>'

        st.markdown(
            f"""
            <div class="mobile-user-brand">
                <div class="mobile-user-brand-left">
                    {logo_html}
                    <div>
                        <div class="mobile-user-title">Smart Filaha</div>
                        <div class="mobile-user-sub">{U(lang, "nav_home")}</div>
                    </div>
                </div>
                <div class="mobile-user-menu-icon">☰</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = [items[i:i + 2] for i in range(0, len(items), 2)]

        for row_index, row in enumerate(rows):
            cols = st.columns(2, gap="small")

            for col_index, (target_page, target_view, icon, label) in enumerate(row):
                with cols[col_index]:
                    button_key = f"mobile_user_nav_{row_index}_{col_index}"

                    if st.button(
                        f"{icon}  {label}",
                        key=button_key,
                        use_container_width=True,
                    ):
                        if target_page == "home":
                            st.session_state.page = "home"
                            st.session_state.home_view = target_view
                        else:
                            st.session_state.page = target_page

                        st.rerun()

def render_language_selector():
    """Global language selector for the user interface."""
    languages = ["Français", "العربية", "دارجة", "English"]

    if "language" not in st.session_state:
        st.session_state.language = "Français"

    st.markdown(
        """
        <style>
        .language-label {
            color:#18362A;
            font-size:11px;
            font-weight:700;
            margin-bottom:4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    current = st.session_state.language
    index = languages.index(current) if current in languages else 0
    lang = st.selectbox(
        f"🌐 {U(st.session_state.language, 'language')}",
        languages,
        index=index,
        key="user_language_selector",
    )
    st.session_state.language = lang
    user_id = st.session_state.get("user_id")
    if user_id:
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.language != lang:
                user.language = lang
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()
    apply_language_direction(lang)
    return lang

def render_topbar(lang=None):
    username = st.session_state.get("username", "Utilisateur")
    col_logo, col_search, col_user = st.columns([2.1, 5.2, 2.0], vertical_alignment="center")

    with col_logo:
        logo = "assets/logo2.png"
        if os.path.exists(logo):
            st.image(logo, width=170)
        else:
            st.markdown(
                '<div style="font-size:18px;font-weight:800;color:#18362A;">🌿 Smart Filaha</div>',
                unsafe_allow_html=True
            )

    with col_search:
        st.text_input(
            "search", placeholder=U(lang or st.session_state.get("language", "Français"), "search"),
            label_visibility="collapsed", key="global_search"
        )

    with col_user:
        st.markdown(
            f'<div style="text-align:right;color:#18362A;font-size:12px;font-weight:700;">'
            f'👤 {username}<div style="color:#91A198;font-size:9px;font-weight:400;">{U(lang or st.session_state.get("language", "Français"), "user")}</div></div>',
            unsafe_allow_html=True
        )

def render_search_results(query, lang):
    q = query.strip().lower()
    if len(q) < 2:
        return
    st.markdown(f'<div class="sf-card"><div class="sf-section-title">🔎 {U(lang, "search_results")} "{query}"</div>', unsafe_allow_html=True)

    found = False

    nk = {"دارجة": "dar_name", "العربية": "ar_name", "Français": "fr_name", "English": "en_name"}
    for d_key, d_info in DISEASE_DATA.items():
        name = d_info.get(nk[lang], d_key)
        if q in name.lower() or q in d_key.lower():
            found = True
            st.markdown(f"🦠 **{name}** — gravité : `{d_info.get('severity','—')}`")

    for name, desc in INFO_DATA.get(lang, []):
        if q in name.lower() or q in desc.lower():
            found = True
            st.markdown(f"ℹ️ **{name}**  \n{desc}")

    for title, desc in SEASONS.get(lang, []):
        if q in title.lower() or q in desc.lower():
            found = True
            st.markdown(f"🌱 **{title}**  \n{desc}")

    ei = EXPERT_INFO.get(lang, {})
    for t, d in ei.get("items", []):
        if q in t.lower() or q in d.lower():
            found = True
            st.markdown(f"👨‍🌾 **{t}** — {d}")

    if not found:
        st.caption(U(lang, "no_search"))

    st.markdown('</div>', unsafe_allow_html=True)

def render_hero(lang, T):
    username = st.session_state.get("username", "")
    bg_path = _hero_bg_path()

    if bg_path:
        bg_style = (
            f"background-image: linear-gradient(120deg, rgba(18,62,44,.86), "
            f"rgba(42,118,80,.78)), url('{_file_data_uri(bg_path)}');"
            f"background-size:cover; background-position:center;"
        )
    else:
        bg_style = ""

    st.markdown(f"""
    <div class="sf-hero" style="{bg_style}">
        <div class="sf-hero-kicker">{U(lang, "hero_kicker")}</div>
        <h2>{U(lang, "hero_title", user=username)}</h2>
        <p>{U(lang, "hero_desc")}</p>
        <div class="sf-hero-badge">🌱 {U(lang, "smart_agri")}</div>
    </div>
    """, unsafe_allow_html=True)

def render_stats(total, alerts, plants_count, lang="Français"):
    cols = st.columns(4, gap="medium")
    stats = [
        ("🌾", "#E7F5EB", "#247B49", plants_count, U(lang, "stat_crops")),
        ("🖼️", "#EDF3FF", "#4674C7", total, U(lang, "stat_images")),
        ("⚠️", SF["warn_light"], SF["warn"], alerts, U(lang, "stat_alerts")),
        ("📍", "#F2ECFA", "#7951A6", plants_count, U(lang, "stat_fields")),
    ]
    for col, (icon, bg, fg, val, label) in zip(cols, stats):
        with col:
            st.markdown(f"""
            <div class="sf-stat">
                <div class="sf-stat-top">
                    <div class="sf-stat-icon" style="background:{bg};color:{fg};">{icon}</div>
                    <span style="font-size:10px;color:#9AA69F;">Smart Filaha</span>
                </div>
                <div class="sf-stat-val">{val}</div>
                <div class="sf-stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

def render_map_card(lang="Français"):
    st.markdown(f"""
    <div class="sf-card">
        <div class="sf-section-title">🗺️ {U(lang, "map_title")}</div>
        <div class="sf-section-sub">{U(lang, "map_sub")}</div>
        <div class="sf-map">
            <div class="sf-map-road"></div>
            <div class="sf-field" style="left:9%;top:24%;width:25%;height:28%;transform:rotate(-8deg);"></div>
            <div class="sf-field" style="left:35%;top:17%;width:22%;height:31%;transform:rotate(7deg);"></div>
            <div class="sf-field" style="left:58%;top:30%;width:28%;height:25%;transform:rotate(-5deg);"></div>
            <div class="sf-field" style="left:22%;top:57%;width:30%;height:27%;transform:rotate(6deg);"></div>
            <div class="sf-field" style="left:54%;top:58%;width:27%;height:25%;transform:rotate(-8deg);"></div>
            <div class="sf-pin" style="left:23%;top:37%;background:#2BA05A;"></div>
            <div class="sf-pin" style="left:48%;top:28%;background:#E0A62A;"></div>
            <div class="sf-pin" style="left:70%;top:44%;background:#2BA05A;"></div>
            <div class="sf-pin" style="left:38%;top:70%;background:#E0A62A;"></div>
            <div class="sf-pin" style="left:68%;top:68%;background:#D95C4F;"></div>
            <div class="sf-map-legend">
                <div style="font-weight:800;margin-bottom:5px;">{U(lang, "map_sub")}</div>
                <div class="sf-legend-row"><span class="sf-dot" style="background:#2BA05A;"></span> {U(lang, "map_health")}</div>
                <div class="sf-legend-row"><span class="sf-dot" style="background:#E0A62A;"></span> {U(lang, "map_watch")}</div>
                <div class="sf-legend-row"><span class="sf-dot" style="background:#D95C4F;"></span> {U(lang, "map_alert")}</div>
            </div>
        </div>
        <div style="display:flex;justify-content:space-between;margin-top:10px;color:#718078;font-size:10px;">
            <span>{U(lang, "map_note")}</span>
            <span style="font-weight:700;color:#2A7650;">5 {U(lang, "zones")}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_assistant_panel(lang="Français"):
    st.markdown(f"""
    <div class="sf-ai">
        <div class="sf-ai-head">
            <div class="sf-ai-title">🤖 {U(lang, "ai_title")}</div>
            <div class="sf-online">● {U(lang, "available")}</div>
        </div>
        <div class="sf-chat-msg">
            {U(lang, "ai_msg")}
        </div>
        <div style="color:#6C7D73;font-size:10px;font-weight:700;margin:13px 0 5px;">
            {U(lang, "quick_questions")}
        </div>
        <span class="sf-chip">🌾 {U(lang, "common")}</span>
        <span class="sf-chip">💧 {U(lang, "yield")}</span>
        <span class="sf-chip">🌱 {U(lang, "season")}</span>
        <span class="sf-chip">📖 {U(lang, "consult_doc")}</span>
        <div class="sf-ai-status">
            <b style="color:#315C43;">🌿 {U(lang, "ai_analysis")}</b><br>{U(lang, "ai_status")}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_quick_actions(lang="Français"):
    cols = st.columns(4, gap="medium")

    with cols[0]:
        if st.button(f"📸  {U(lang, 'take_photo')}", use_container_width=True, key="quick_camera"):
            st.session_state.home_view = "analyse"
            st.session_state.analysis_mode = "camera"
            st.rerun()
        st.caption(U(lang, "camera_hint"))

    with cols[1]:
        if st.button(f"📁  {U(lang, 'import_image')}", use_container_width=True, key="quick_upload"):
            st.session_state.home_view = "analyse"
            st.session_state.analysis_mode = "upload"
            st.rerun()
        st.caption(U(lang, "gallery_hint"))

    with cols[2]:
        if st.button(f"📚  {U(lang, 'quick_doc')}", use_container_width=True, key="quick_doc"):
            st.session_state.home_view = "doc"
            st.rerun()
        st.caption(U(lang, "doc_hint"))

    with cols[3]:
        if st.button(f"🤖  {U(lang, 'assistant')}", use_container_width=True, key="quick_chat"):
            st.session_state.home_view = "chatbot"
            st.rerun()
        st.caption(U(lang, "question_hint"))

def render_analyse_section(model, class_names, lang, T):
    col_left, col_right = st.columns([5, 7], gap="large")

    with col_left:
        st.markdown('<div class="sf-card">', unsafe_allow_html=True)
        st.markdown(f"**📷 {T['title']}**")

        upload_label = f"📁 {U(lang, 'upload')}"
        camera_label = f"📸 {U(lang, 'camera')}"
        mode = st.radio(
            U(lang, "source"),
            [upload_label, camera_label],
            horizontal=True,
            index=1 if st.session_state.get("analysis_mode") == "camera" else 0,
            label_visibility="collapsed",
        )

        uploaded = None
        image = None

        if mode == camera_label:
            camera_file = st.camera_input(
                U(lang, "camera_prompt"),
                key="plant_camera",
            )
            if camera_file is not None:
                uploaded = camera_file
                image = Image.open(camera_file).convert("RGB")
        else:
            uploaded = st.file_uploader(
                T["upload_label"],
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
                key="plant_upload",
            )
            if uploaded:
                image = Image.open(uploaded).convert("RGB")

        if image is not None:
            st.image(image, use_container_width=True)

        analyze_clicked = st.button(
            f"🔍 {T['analyze_btn']}",
            disabled=image is None,
            use_container_width=True,
            key="analyze_plant_button",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        tab_result, tab_hist, tab_info, tab_season, tab_expert = st.tabs([
            f"🔍 {T['result_title']}",
            f"📋 {T['history_tab']}",
            f"ℹ️ {T['info_tab']}",
            f"🌱 {T['season_tab']}",
            f"👨‍🌾 {T['expert_tab']}",
        ])

        with tab_result:
            if analyze_clicked and image is not None:
                with st.spinner(T["analyzing"]):
                    img_r = image.resize(IMG_SIZE)
                    arr = np.expand_dims(np.array(img_r) / 255.0, axis=0)
                    preds = model.predict(arr)
                    idx = int(np.argmax(preds[0]))
                    conf = float(preds[0][idx]) * 100
                    d_key = class_names[str(idx)]

                    st.session_state.total_analyzed += 1
                    d_info = DISEASE_DATA.get(d_key)
                    severity = d_info["severity"] if d_info else "medium"

                    nk = {
                        "دارجة": "dar_name",
                        "العربية": "ar_name",
                        "Français": "fr_name",
                        "English": "en_name",
                    }
                    d_name = d_info[nk[lang]] if d_info else d_key.replace("_", " ")
                    p_raw = d_key.split("___")[0] if "___" in d_key else d_key
                    p_name = PLANT_NAMES.get(p_raw, {}).get(lang, p_raw)
                    advice = (
                        d_info["advice"].get(lang, GENERIC_ADVICE[lang])
                        if d_info else GENERIC_ADVICE[lang]
                    )

                    user_id = st.session_state.get("user_id")
                    save_analysis(
                        user_id, d_key, d_name, p_name,
                        conf, severity, lang
                    )

                    st.session_state.history.append({
                        "time": datetime.datetime.now().strftime("%d/%m %H:%M"),
                        "disease": d_name,
                        "plant": p_name,
                        "confidence": f"{conf:.1f}%",
                        "severity": severity,
                    })

                    if severity == "high":
                        st.session_state.alerts += 1

                    st.success(f"**{d_name}** — {p_name} · {conf:.1f}%")
                    st.markdown(f"**{T['advice_title']}**")
                    for a in advice:
                        st.markdown(f"- {a}")
            else:
                st.info(U(lang, "upload_or_camera"))

        with tab_hist:
            if st.session_state.history:
                for item in reversed(st.session_state.history[-15:]):
                    st.markdown(
                        f"**{item['disease']}** — {item['plant']} · "
                        f"{item['confidence']} · {item['severity']} \n"
                        f"<span style='color:{SF['text_mid']};font-size:12px;'>{item['time']}</span>",
                        unsafe_allow_html=True,
                    )
            else:
                st.info(T["no_result"])

        with tab_info:
            for name, desc in INFO_DATA[lang]:
                st.markdown(f"**{name}** \n{desc}")

        with tab_season:
            for title, desc in SEASONS[lang]:
                st.markdown(f"**{title}** \n{desc}")

        with tab_expert:
            ei = EXPERT_INFO[lang]
            st.markdown(f"**{ei['title']}**")
            for t, d in ei["items"]:
                st.markdown(f"- **{t}** — {d}")

def render_home():
    model, class_names = load_model()

    if "history" not in st.session_state: st.session_state.history = []
    if "total_analyzed" not in st.session_state: st.session_state.total_analyzed = 0
    if "alerts" not in st.session_state: st.session_state.alerts = 0
    if "home_view" not in st.session_state: st.session_state.home_view = "accueil"

    inject_css()
    lang0 = st.session_state.get("language", "Français")
    render_sidebar(lang0)
    render_mobile_user_menu(lang0)

    # Language chosen by the user is kept in session_state, so it stays
    # active while navigating between the user pages.
    lang = render_language_selector()
    T = TRANSLATIONS[lang]

    plants_count = len(set(h["plant"] for h in st.session_state.history)) if st.session_state.history else 0
    view = st.session_state.home_view

    if view == "accueil":
        query = st.session_state.get("global_search", "")
        if len(query.strip()) >= 2:
            render_topbar(lang)
            render_search_results(query, lang)
        else:
            # Keep the existing hero/design, but place the greeting banner in the page header area.
            # No functionality or component styling is changed.
            render_hero(lang, T)
            render_topbar(lang)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            render_stats(st.session_state.total_analyzed, st.session_state.alerts, plants_count, lang)
            st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
            col_map, col_chat = st.columns([7, 5], gap="large")
            with col_map:
                render_map_card(lang)
            with col_chat:
                render_assistant_panel(lang)
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="sf-section-title">⚡ Accès rapide</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            render_quick_actions(lang)

    elif view == "analyse":
        render_analyse_section(model, class_names, lang, T)

    elif view == "carto":
        render_map_card(lang)

    elif view == "doc":
        tab_info, tab_season, tab_expert = st.tabs(
            [f"ℹ️ {T['info_tab']}", f"🌱 {T['season_tab']}", f"👨‍🌾 {T['expert_tab']}"])
        with tab_info:
            for name, desc in INFO_DATA[lang]:
                st.markdown(f"**{name}**  \n{desc}")
        with tab_season:
            for title, desc in SEASONS[lang]:
                st.markdown(f"**{title}**  \n{desc}")
        with tab_expert:
            ei = EXPERT_INFO[lang]
            for t, d in ei["items"]:
                st.markdown(f"- **{t}** — {d}")

    elif view == "chatbot":
        st.markdown('<div class="sf-ai-title" style="margin-bottom:10px;">🤖 Assistant IA agricole</div>', unsafe_allow_html=True)
        render_chat_embedded()

    elif view == "images":
        if st.session_state.history:
            for item in reversed(st.session_state.history[-15:]):
                st.markdown(f"**{item['disease']}** — {item['plant']} · {item['confidence']}")
        else:
            st.info(T["no_result"])

    elif view == "profil":
        st.session_state.home_view = "accueil"
        st.session_state.page = "profile"
        st.rerun()
        
        



        