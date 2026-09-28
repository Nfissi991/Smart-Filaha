# auth/login.py
import base64
import glob
import os
import streamlit as st
import bcrypt
from datetime import datetime
from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import User


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def get_user_by_username(username: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


def create_user(username: str, email: str, password: str, role: str = "user"):
    db = SessionLocal()
    try:
        user = User(
            username=username,
            email=email,
            password=hash_password(password),
            role=role,
            is_approved=(role != "conseiller"),  # conseiller khaso mwafa9a mn admin
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def login_user(username: str, password: str):
    user = get_user_by_username(username)
    if not user:
        return None, "Utilisateur introuvable"
    if not user.is_active:
        return None, "Compte désactivé"
    if not verify_password(password, user.password):
        return None, "Mot de passe incorrect"
    if user.role == "conseiller" and not user.is_approved:
        return None, "Votre compte conseiller est en attente de validation."
    return user, None


def init_session(user):
    st.session_state.logged_in = True
    st.session_state.user_id = user.id
    st.session_state.username = user.username
    st.session_state.role = user.role
    st.session_state.language = user.language
    st.session_state.page = "conseiller" if user.role == "conseiller" else "home"


def logout():
    for key in ["logged_in", "user_id", "username", "role", "language", "page"]:
        st.session_state.pop(key, None)


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def is_admin() -> bool:
    return st.session_state.get("role") == "admin"


def is_conseiller() -> bool:
    return st.session_state.get("role") == "conseiller"


def require_login():
    if not is_logged_in():
        show_login_page()
        st.stop()


# ────────────────────────── helpers image ──────────────────────────
def _find_asset(patterns):
    """kayqleb 3la l'image f 3 blayes (cwd, racine mchrou3, jnb had l fichier)
    b des patterns (glob) bach ykhdem hta ila bdlti smiya (login1.jpg, login11.jpg...)."""
    here = os.path.dirname(os.path.abspath(__file__))          # .../myapp/auth
    project_root = os.path.dirname(here)                        # .../myapp
    for base in (os.getcwd(), project_root, here):
        assets_dir = os.path.join(base, "assets")
        if not os.path.isdir(assets_dir):
            continue
        for pattern in patterns:
            matches = sorted(glob.glob(os.path.join(assets_dir, pattern)))
            if matches:
                return matches[0]
    return None


def _b64_image(path):
    if not path:
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except (FileNotFoundError, OSError):
        return None


# ────────────────────────── page de login (design Smart Filaha) ──────────────────────────
def show_login_page():
    from config.settings import COLORS
    C = COLORS

    # ============================================================
    # IMAGE / LOGO
    # ============================================================
    # Priorité à login11.jpg comme demandé.
    hero_path = _find_asset([
        "login11.jpg", "login11.jpeg", "login11.png",
        "login1.jpg", "login1.jpeg", "login1.png",
        "hero-bg.*", "hero_bg.*"
    ])
    # Logo requested for the hero: use logof.png first.
    logo_path = _find_asset(["logof.png", "Logof.png", "logo2.png", "Logo2.png", "logo.png", "logo*.png"])

    hero_b64 = _b64_image(hero_path)
    logo_b64 = _b64_image(logo_path)

    # ============================================================
    # LANGUE
    # ============================================================
    LANGUAGES = {
        "🇫🇷 Français": {
            "dir": "ltr",
            "welcome": "Bienvenue !",
            "welcome_sub": "Connectez-vous à votre compte pour continuer",
            "login_tab": "Connexion",
            "register_tab": "Inscription",
            "user_email": "Nom d'utilisateur ou email",
            "username": "Nom d'utilisateur",
            "email": "Email",
            "password": "Mot de passe",
            "confirm_password": "Confirmer mot de passe",
            "remember": "Se souvenir de moi",
            "forgot": "Mot de passe oublié ?",
            "login": "Se connecter →",
            "create": "Créer un compte",
            "already": "J'ai déjà un compte",
            "register": "S'inscrire",
            "or": "Ou",
            "language": "Langue",
            "farmer": "🌾 Agriculteur",
            "advisor": "🧑‍🔬 Conseiller agricole",
            "hero_title": "Des plantes en bonne santé,<br>une meilleure récolte",
            "hero_sub": "Détectez les maladies des plantes et recevez des conseils personnalisés grâce à l'intelligence artificielle.",
            "feature1": "Identifier les maladies",
            "feature2": "Obtenir des conseils",
            "feature3": "Améliorer vos récoltes",
            "tagline": "IA au service de l'agriculture",
            "fill": "Remplissez tous les champs",
            "wrong_pass": "Les mots de passe ne correspondent pas",
            "user_exists": "Nom d'utilisateur déjà utilisé",
            "account_created": "Compte créé ! Connectez-vous maintenant",
            "advisor_wait": "Compte créé ! Votre demande de conseiller est en attente de validation par l'administrateur.",
        },
        "🇬🇧 English": {
            "dir": "ltr",
            "welcome": "Welcome!",
            "welcome_sub": "Sign in to your account to continue",
            "login_tab": "Login",
            "register_tab": "Register",
            "user_email": "Username or email",
            "username": "Username",
            "email": "Email",
            "password": "Password",
            "confirm_password": "Confirm password",
            "remember": "Remember me",
            "forgot": "Forgot password?",
            "login": "Sign in →",
            "create": "Create an account",
            "already": "I already have an account",
            "register": "Sign up",
            "or": "Or",
            "language": "Language",
            "farmer": "🌾 Farmer",
            "advisor": "🧑‍🔬 Agricultural advisor",
            "hero_title": "Healthy plants,<br>a better harvest",
            "hero_sub": "Detect plant diseases and receive personalized advice using artificial intelligence.",
            "feature1": "Identify diseases",
            "feature2": "Get advice",
            "feature3": "Improve your harvests",
            "tagline": "AI for agriculture",
            "fill": "Please fill in all fields",
            "wrong_pass": "Passwords do not match",
            "user_exists": "Username already in use",
            "account_created": "Account created! You can now log in",
            "advisor_wait": "Account created! Your advisor request is waiting for administrator approval.",
        },
        "🇲🇦 العربية": {
            "dir": "rtl",
            "welcome": "مرحباً!",
            "welcome_sub": "سجّل الدخول إلى حسابك للمتابعة",
            "login_tab": "تسجيل الدخول",
            "register_tab": "إنشاء حساب",
            "user_email": "اسم المستخدم أو البريد الإلكتروني",
            "username": "اسم المستخدم",
            "email": "البريد الإلكتروني",
            "password": "كلمة المرور",
            "confirm_password": "تأكيد كلمة المرور",
            "remember": "تذكّرني",
            "forgot": "هل نسيت كلمة المرور؟",
            "login": "تسجيل الدخول ←",
            "create": "إنشاء حساب",
            "already": "لدي حساب بالفعل",
            "register": "إنشاء الحساب",
            "or": "أو",
            "language": "اللغة",
            "farmer": "🌾 فلاح",
            "advisor": "🧑‍🔬 مستشار فلاحي",
            "hero_title": "نباتات صحية،<br>محصول أفضل",
            "hero_sub": "اكتشف أمراض النباتات واحصل على نصائح مخصصة بفضل الذكاء الاصطناعي.",
            "feature1": "تحديد الأمراض",
            "feature2": "الحصول على النصائح",
            "feature3": "تحسين المحاصيل",
            "tagline": "الذكاء الاصطناعي في خدمة الفلاحة",
            "fill": "يرجى ملء جميع الحقول",
            "wrong_pass": "كلمتا المرور غير متطابقتين",
            "user_exists": "اسم المستخدم مستعمل بالفعل",
            "account_created": "تم إنشاء الحساب! يمكنك تسجيل الدخول الآن",
            "advisor_wait": "تم إنشاء الحساب! طلبك كمستشار في انتظار موافقة المسؤول.",
        },
        "🇲🇦 دارجة": {
            "dir": "rtl",
            "welcome": "مرحبا!",
            "welcome_sub": "دخل للحساب ديالك باش تكمل",
            "login_tab": "الدخول",
            "register_tab": "التسجيل",
            "user_email": "اسم المستخدم ولا الإيميل",
            "username": "اسم المستخدم",
            "email": "الإيميل",
            "password": "كلمة السر",
            "confirm_password": "أكد كلمة السر",
            "remember": "تذكرني",
            "forgot": "نسيت كلمة السر؟",
            "login": "دخل للحساب ←",
            "create": "صايب حساب",
            "already": "عندي حساب من قبل",
            "register": "سجل",
            "or": "ولا",
            "language": "اللغة",
            "farmer": "🌾 فلاح",
            "advisor": "🧑‍🔬 مستشار فلاحي",
            "hero_title": "نباتات بصحة مزيانة،<br>محصول أحسن",
            "hero_sub": "اكتاشف أمراض النباتات وخد نصائح مناسبة باستعمال الذكاء الاصطناعي.",
            "feature1": "عرف الأمراض",
            "feature2": "خد النصائح",
            "feature3": "حسن المحاصيل",
            "tagline": "الذكاء الاصطناعي فخدمة الفلاحة",
            "fill": "عمر جميع الخانات",
            "wrong_pass": "كلمتا السر ما متطابقاش",
            "user_exists": "اسم المستخدم مستعمل من قبل",
            "account_created": "تدار الحساب! تقدر دابا تدخل",
            "advisor_wait": "تدار الحساب! طلب ديالك كمستشار كيتسنى موافقة المسؤول.",
        },
    }

    if "login_lang_select" not in st.session_state:
        st.session_state.login_lang_select = "🇫🇷 Français"

    selected_language = st.session_state.login_lang_select
    T = LANGUAGES.get(selected_language, LANGUAGES["🇫🇷 Français"])
    direction = T["dir"]

    # ============================================================
    # LOGIN / REGISTER STATE
    # ============================================================
    if "login_view" not in st.session_state:
        st.session_state.login_view = "login"
    view = st.session_state.login_view

    # ============================================================
    # HERO IMAGE
    # ============================================================
    if hero_b64:
        ext = os.path.splitext(hero_path)[1].lstrip(".").lower()
        mime = "image/png" if ext == "png" else "image/jpeg"
        hero_bg_css = (
            f"background-image: linear-gradient(180deg, rgba(14,46,34,.22), "
            f"rgba(10,32,23,.62)), url('data:{mime};base64,{hero_b64}');"
            f"background-size: cover; background-position: center center;"
        )
    else:
        hero_bg_css = "background: linear-gradient(160deg, #123E2C 0%, #2A7650 100%);"

    active_login = "st-key-tabwrap_login" if view == "login" else "st-key-tabwrap_register"

    # ============================================================
    # DESIGN
    # ============================================================
    st.markdown(f"""
    <style>
    #MainMenu, header, footer {{ visibility: hidden; }}
    [data-testid="stAppViewContainer"] {{ background: #FDFAF4; }}
    [data-testid="stHeader"] {{ background: transparent; }}
    [data-testid="stSidebar"] {{ display: none; }}

    .block-container {{
        padding: 0 !important;
        max-width: 100% !important;
    }}

    div[data-testid="stHorizontalBlock"] {{
        gap: 0 !important;
        align-items: stretch;
    }}

    /* ================= LEFT PANEL ================= */
    .st-key-hero_panel {{
        {hero_bg_css}
        min-height: 100vh;
        height: 100%;
        position: sticky;
        top: 0;
        align-self: flex-start;
        padding: 42px 58px 48px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        direction: ltr;
    }}

    .hero-content {{
        min-height: calc(100vh - 94px);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 100%;
    }}

    .hero-top {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        flex: 0 0 auto;
    }}

    .hero-center {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        width: 100%;
        max-width: 780px;
        flex: 1 1 auto;
        margin: 0 auto;
        padding: 32px 0;
        box-sizing: border-box;
    }}

    .hero-bottom {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        flex: 0 0 auto;
        padding-top: 18px;
    }}

    .brand-logo {{
        height: 250px;
        width: auto;
        max-width: min(560px, 92%);
        object-fit: contain;
        margin-bottom: 20px;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,.28));
    }}

    .brand-name {{
        color: #FFFFFF;
        font-size: 20px;
        font-weight: 800;
        text-shadow: 0 2px 8px rgba(0,0,0,.35);
        margin-bottom: 2px;
    }}

    .brand-tagline {{
        color: #DCEAE0;
        font-size: 12px;
        font-weight: 500;
        text-shadow: 0 1px 6px rgba(0,0,0,.35);
    }}

    .hero-title {{
        color: #FFFFFF;
        font-size: 40px;
        font-weight: 800;
        line-height: 1.28;
        margin-bottom: 26px;
        text-shadow: 0 2px 10px rgba(0,0,0,.35);
        text-align: center;
    }}

    .hero-sub {{
        color: #EAF3EC;
        font-size: 15px;
        line-height: 1.65;
        max-width: 680px;
        margin-bottom: 0;
        text-shadow: 0 1px 6px rgba(0,0,0,.35);
        text-align: center;
    }}

    .features-row {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 40px;
        direction: ltr;
        width: 100%;
        margin-top: 24px;
    }}

    .feature {{
        text-align: center;
        color: #F1F7F2;
        font-size: 14px;
        line-height: 1.45;
        width: 31%;
        max-width: 220px;
    }}

    .feature-icon {{
        font-size: 20px;
        margin-bottom: 8px;
        width: 42px;
        height: 42px;
        line-height: 42px;
        background: rgba(255,255,255,.14);
        border: 1px solid rgba(255,255,255,.22);
        border-radius: 50%;
        margin-inline: auto;
    }}

    /* ================= RIGHT PANEL ================= */
    .st-key-login_panel {{
        background: #FDFAF4;
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 48px 56px;
        box-sizing: border-box;
    }}

    .st-key-login_card {{
        max-width: 470px;
        width: 100%;
        background: {C['bg_card']};
        border: 1px solid {C['border']};
        border-radius: 20px;
        padding: 34px 36px 26px;
        box-shadow: 0 18px 40px rgba(28,58,47,.10);
        direction: {direction};
    }}

    .welcome-title {{
        font-size: 22px;
        font-weight: 800;
        color: {C['primary_dark']};
        margin-bottom: 4px;
    }}

    .welcome-sub {{
        font-size: 13px;
        color: {C['text_mid']};
        margin-bottom: 20px;
    }}

    /* Inputs */
    .stTextInput label {{
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: {C['text_dark']} !important;
    }}

    .stTextInput > div > div > input {{
        background: {C['bg_input']} !important;
        border: 1px solid {C['border']} !important;
        border-radius: 9px !important;
        color: {C['text_dark']} !important;
        min-height: 42px !important;
        direction: {direction} !important;
        text-align: {"right" if direction == "rtl" else "left"} !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: {C['primary_mid']} !important;
        box-shadow: 0 0 0 2px rgba(45,82,64,.12) !important;
    }}

    /* ================= MAIN LOGIN BUTTON ================= */
    .st-key-btn_login button {{
        background: #1E8A4C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 46px !important;
        padding: 11px 20px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: none !important;
        transition: all .15s ease !important;
    }}

    .st-key-btn_login button:hover {{
        background: #16723E !important;
        transform: translateY(-1px);
    }}

    /* Other filled button */
    .st-key-btn_register button {{
        background: #1E8A4C !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        min-height: 46px !important;
        font-weight: 700 !important;
    }}

    /* Outline buttons */
    .st-key-btn_create_wrap button,
    .st-key-btn_backlogin_wrap button {{
        background: transparent !important;
        color: {C['primary_dark']} !important;
        border: 1px solid {C['border']} !important;
        border-radius: 10px !important;
        min-height: 44px !important;
        font-weight: 600 !important;
    }}

    .st-key-btn_create_wrap button:hover,
    .st-key-btn_backlogin_wrap button:hover {{
        background: {C['bg_input']} !important;
    }}

    /* ================= TABS ================= */
    .st-key-tabwrap_login button,
    .st-key-tabwrap_register button {{
        background: transparent !important;
        color: {C['text_mid']} !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        border-radius: 0 !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        padding: 0 0 10px 0 !important;
        width: auto !important;
        min-height: 35px !important;
        box-shadow: none !important;
    }}

    .{active_login} button {{
        color: {C['primary_mid']} !important;
        border-bottom: 2px solid {C['primary_mid']} !important;
    }}

    /* Divider */
    .divider-row {{
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 16px 0;
        color: {C['text_muted']};
        font-size: 12px;
    }}

    .divider-row hr {{
        flex: 1;
        border: none;
        border-top: 1px solid {C['border']};
        margin: 0;
    }}

    /* Language select */
    .st-key-login_lang_select {{
        margin-top: 4px;
    }}

    .st-key-login_lang_select [data-baseweb="select"] > div {{
        border: 1px solid {C['border']} !important;
        border-radius: 9px !important;
        background: {C['bg_input']} !important;
        min-height: 38px !important;
        box-shadow: none !important;
    }}

    .st-key-login_lang_select {{
        direction: ltr !important;
        text-align: center !important;
    }}

    .st-key-login_lang_select [data-baseweb="select"] {{
        width: 125px !important;
        direction: ltr !important;
        margin: 0 auto !important;
    }}

    .st-key-login_lang_select [data-baseweb="select"] > div {{
        direction: ltr !important;
        text-align: left !important;
    }}

    /* ================= LANGUAGE DIRECTION ================= */
    .st-key-login_card {{
        direction: {direction} !important;
    }}

    .st-key-login_card label,
    .st-key-login_card [data-testid="stMarkdownContainer"] {{
        direction: {direction};
        text-align: {"right" if direction == "rtl" else "left"};
    }}

    .st-key-login_card [data-testid="stCheckbox"] {{
        direction: {direction};
    }}

    .st-key-login_card [data-testid="stRadio"] {{
        direction: {direction};
    }}

    .st-key-login_card [data-baseweb="select"] {{
        direction: {direction} !important;
    }}

    /* RTL */
    .rtl-text {{
        direction: rtl;
        text-align: right;
    }}

    @media (max-width: 900px) {{
        .st-key-hero_panel {{
            min-height: 720px;
            position: relative;
            padding: 30px 24px;
        }}
        .hero-content {{ min-height: 660px; }}
        .brand-logo {{ height: 180px; max-width: 90%; }}
        .hero-title {{ font-size: 30px; }}
        .features-row {{ gap: 12px; }}
        .feature {{ font-size: 12px; }}

        .st-key-login_panel {{
            min-height: auto;
            padding: 30px 18px;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

    # ============================================================
    # TWO COLUMNS
    # ============================================================
    col_left, col_right = st.columns([1, 1])

    # ============================================================
    # LEFT: IMAGE + TEXT
    # ============================================================
    with col_left:
        with st.container(key="hero_panel"):
            if logo_b64:
                logo_html = (
                    f'<img src="data:image/png;base64,{logo_b64}" '
                    f'class="brand-logo" alt="Smart Filaha">'
                )
                brand_text_html = ""
            else:
                logo_html = '<div style="font-size:34px;">🌿</div>'
                brand_text_html = (
                    '<div class="brand-name">Smart Filaha</div>'
                    f'<div class="brand-tagline">{T["tagline"]}</div>'
                )

            # Build HTML as one continuous string (no Markdown code-block indentation).
            hero_html = (
                '<div class="hero-content">'
                + '<div class="hero-top">'
                + logo_html
                + brand_text_html
                + '</div>'
                + '<div class="hero-center">'
                + f'<div class="hero-title">{T["hero_title"]}</div>'
                + f'<div class="hero-sub">{T["hero_sub"]}</div>'
                + '</div>'
                + '<div class="hero-bottom">'
                + '<div class="features-row">'
                + f'<div class="feature"><div class="feature-icon">🎯</div>{T["feature1"]}</div>'
                + f'<div class="feature"><div class="feature-icon">💡</div>{T["feature2"]}</div>'
                + f'<div class="feature"><div class="feature-icon">📈</div>{T["feature3"]}</div>'
                + '</div>'
                + '</div>'
                + '</div>'
            )
            st.markdown(hero_html, unsafe_allow_html=True)

    # ============================================================
    # RIGHT: LOGIN / REGISTER
    # ============================================================
    with col_right:
        with st.container(key="login_panel"):
            with st.container(key="login_card"):

                st.markdown(
                    f'<div class="welcome-title">{T["welcome"]}</div>',
                    unsafe_allow_html=True
                )
                st.markdown(
                    f'<div class="welcome-sub">{T["welcome_sub"]}</div>',
                    unsafe_allow_html=True
                )

                # Tabs
                tab_col1, tab_col2, _sp = st.columns([1.2, 1.4, 3])

                with tab_col1:
                    with st.container(key="tabwrap_login"):
                        if st.button(
                            T["login_tab"],
                            key="tab_btn_login",
                            use_container_width=True
                        ):
                            st.session_state.login_view = "login"
                            st.rerun()

                with tab_col2:
                    with st.container(key="tabwrap_register"):
                        if st.button(
                            T["register_tab"],
                            key="tab_btn_register",
                            use_container_width=True
                        ):
                            st.session_state.login_view = "register"
                            st.rerun()

                st.markdown(
                    f'<hr style="margin:0 0 20px;border-color:{C["border"]};">',
                    unsafe_allow_html=True
                )

                # ========================================================
                # LOGIN
                # ========================================================
                if view == "login":
                    username = st.text_input(
                        T["user_email"],
                        key="login_user"
                    )

                    password = st.text_input(
                        T["password"],
                        type="password",
                        key="login_pass"
                    )

                    col_remember, col_forgot = st.columns([1, 1])

                    with col_remember:
                        st.checkbox(
                            T["remember"],
                            key="login_remember"
                        )

                    with col_forgot:
                        st.markdown(
                            f'<div style="text-align:right;padding-top:8px;'
                            f'font-size:12px;color:{C["primary_mid"]};">'
                            f'{T["forgot"]}</div>',
                            unsafe_allow_html=True
                        )

                    if st.button(
                        T["login"],
                        key="btn_login",
                        use_container_width=True
                    ):
                        if username and password:
                            user, error = login_user(username, password)

                            if user:
                                init_session(user)
                                st.rerun()
                            else:
                                # Backend errors remain unchanged so the
                                # authentication functionality is preserved.
                                st.error(error)
                        else:
                            st.warning(T["fill"])

                    st.markdown(
                        f'<div class="divider-row"><hr>{T["or"]}<hr></div>',
                        unsafe_allow_html=True
                    )

                    with st.container(key="btn_create_wrap"):
                        if st.button(
                            T["create"],
                            key="btn_goto_register",
                            use_container_width=True
                        ):
                            st.session_state.login_view = "register"
                            st.rerun()

                # ========================================================
                # REGISTER
                # ========================================================
                else:
                    reg_user = st.text_input(
                        T["username"],
                        key="reg_user"
                    )

                    reg_email = st.text_input(
                        T["email"],
                        key="reg_email"
                    )

                    reg_pass = st.text_input(
                        T["password"],
                        type="password",
                        key="reg_pass"
                    )

                    reg_pass2 = st.text_input(
                        T["confirm_password"],
                        type="password",
                        key="reg_pass2"
                    )

                    reg_type = st.radio(
                        "Type de compte" if selected_language == "🇫🇷 Français"
                        else "Account type" if selected_language == "🇬🇧 English"
                        else "نوع الحساب" if selected_language == "🇲🇦 العربية"
                        else "نوع الحساب",
                        [T["farmer"], T["advisor"]],
                        key="reg_type",
                        horizontal=True,
                    )

                    if st.button(
                        T["register"],
                        key="btn_register",
                        use_container_width=True
                    ):
                        if reg_user and reg_email and reg_pass and reg_pass2:

                            if reg_pass != reg_pass2:
                                st.error(T["wrong_pass"])

                            elif get_user_by_username(reg_user):
                                st.error(T["user_exists"])

                            else:
                                # Nbdlo ghir l'affichage dyal langue;
                                # role mapping kaybqa nafsou.
                                role = "conseiller" if reg_type == T["advisor"] else "user"

                                create_user(
                                    reg_user,
                                    reg_email,
                                    reg_pass,
                                    role=role
                                )

                                if role == "conseiller":
                                    st.success(T["advisor_wait"])
                                else:
                                    st.success(T["account_created"])
                                    st.session_state.login_view = "login"
                        else:
                            st.warning(T["fill"])

                    st.markdown(
                        f'<div class="divider-row"><hr>{T["or"]}<hr></div>',
                        unsafe_allow_html=True
                    )

                    with st.container(key="btn_backlogin_wrap"):
                        if st.button(
                            T["already"],
                            key="btn_goto_login",
                            use_container_width=True
                        ):
                            st.session_state.login_view = "login"
                            st.rerun()

                # ========================================================
                # LANGUAGE
                # ========================================================
                st.markdown(
                    '<div style="height:18px;"></div>',
                    unsafe_allow_html=True
                )

                _lang_left, lang_col, _lang_right = st.columns([1, 1, 1])

                with lang_col:
                    st.selectbox(
                        T["language"],
                        list(LANGUAGES.keys()),
                        key="login_lang_select",
                        label_visibility="collapsed",
                    )
