# view/dashboard_user.py
# Smart Filaha - User dashboard
# Mobile navigation added without changing the existing user logic.

import streamlit as st
import pandas as pd
from sqlalchemy.orm import selectinload

from database.db import SessionLocal
from database.models import Analysis, Feedback
from components.navbar import render_navbar
from config.settings import COLORS

C = COLORS


# ================================================================
# DATA / EXISTING LOGIC
# ================================================================

def get_user_analyses(user_id: int):
    db = SessionLocal()
    try:
        return (
            db.query(Analysis)
            .options(selectinload(Analysis.feedbacks))
            .filter(Analysis.user_id == user_id)
            .order_by(Analysis.created_at.desc())
            .limit(50)
            .all()
        )
    finally:
        db.close()


def save_feedback(
    analysis_id: int,
    is_correct: bool,
    correct_label: str = None
):
    db = SessionLocal()
    try:
        fb = Feedback(
            analysis_id=analysis_id,
            is_correct=is_correct,
            correct_label=correct_label,
        )
        db.add(fb)
        db.commit()
    finally:
        db.close()


# ================================================================
# MOBILE NAVIGATION
# ================================================================

def render_user_mobile_nav():
    """
    Mobile navigation only.

    IMPORTANT:
    The whole navigation is inside one Streamlit keyed container.
    This makes it possible to hide/show the complete menu with CSS.
    PC: hidden.
    Phone/tablet: visible.
    """

    st.markdown(
        """
        <style>
        /* ==========================================================
           USER MOBILE MENU
           Hidden on PC
           ========================================================== */

        .st-key-user_mobile_nav {
            display: none;
        }

        @media (max-width: 768px) {

            .st-key-user_mobile_nav {
                display: block !important;
                margin-bottom: 14px;
            }

            .st-key-user_mobile_nav .user-mobile-head {
                background: linear-gradient(
                    135deg,
                    #103326 0%,
                    #1E6246 100%
                );
                border-radius: 15px;
                padding: 10px 13px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                box-shadow: 0 5px 18px rgba(16, 51, 38, .14);
                margin-bottom: 9px;
            }

            .st-key-user_mobile_nav .user-mobile-brand {
                display: flex;
                align-items: center;
                gap: 9px;
            }

            .st-key-user_mobile_nav .user-mobile-logo {
                width: 36px;
                height: 36px;
                object-fit: contain;
                background: white;
                border-radius: 9px;
                padding: 3px;
            }

            .st-key-user_mobile_nav .user-mobile-title {
                color: white;
                font-size: 13px;
                font-weight: 850;
                line-height: 1.1;
            }

            .st-key-user_mobile_nav .user-mobile-sub {
                color: rgba(255,255,255,.72);
                font-size: 9px;
                margin-top: 3px;
            }

            .st-key-user_mobile_nav .user-mobile-icon {
                color: white;
                font-size: 20px;
                line-height: 1;
            }

            .st-key-user_mobile_nav [data-testid="column"] {
                padding: 0 !important;
            }

            .st-key-user_mobile_nav .stButton {
                margin-bottom: 7px !important;
            }

            .st-key-user_mobile_nav .stButton > button {
                min-height: 43px !important;
                padding: 7px 5px !important;
                border-radius: 10px !important;
                border: 1px solid #DCE8E1 !important;
                background: white !important;
                color: #18362A !important;
                font-size: 10px !important;
                font-weight: 750 !important;
                box-shadow: none !important;
                white-space: normal !important;
            }

            .st-key-user_mobile_nav .stButton > button:hover {
                background: #E8F5EC !important;
                border-color: #76AE8C !important;
                color: #145337 !important;
            }

            .st-key-user_mobile_nav .stButton > button:focus {
                box-shadow: 0 0 0 2px rgba(30,122,70,.12) !important;
            }

            [data-testid="stSidebarCollapsedControl"] {
                display: none !important;
            }

            .block-container {
                padding-left: 10px !important;
                padding-right: 10px !important;
                padding-top: 10px !important;
                padding-bottom: 28px !important;
                max-width: 100% !important;
            }

            .user-page-title {
                font-size: 20px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    items = [
        ("home", "accueil", "🏠", "Accueil"),
        ("home", "analyse", "🔬", "IA & Analyse"),
        ("home", "carto", "🗺️", "Cartographie"),
        ("home", "doc", "📚", "Documentation"),
        ("home", "chatbot", "🤖", "Chatbot IA"),
        ("home", "images", "🖼️", "Mes images"),
        ("sensors", None, "📡", "Mes capteurs"),
        ("publications", None, "📢", "Publications"),
        ("messages", None, "💬", "Messages"),
        ("profile", None, "👤", "Mon profil"),
    ]

    # The HTML and all Streamlit buttons are now genuinely inside
    # the same keyed Streamlit container.
    with st.container(key="user_mobile_nav"):

        st.markdown(
            """
            <div class="user-mobile-head">
                <div class="user-mobile-brand">
                    <img
                        class="user-mobile-logo"
                        src="assets/logof.png"
                        alt="Smart Filaha"
                    >
                    <div>
                        <div class="user-mobile-title">Smart Filaha</div>
                        <div class="user-mobile-sub">Navigation</div>
                    </div>
                </div>
                <div class="user-mobile-icon">☰</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        rows = [
            items[0:2],
            items[2:4],
            items[4:6],
            items[6:8],
            items[8:10],
        ]

        for row_index, row in enumerate(rows):
            cols = st.columns(2, gap="small")

            for col_index, (page, home_view, icon, label) in enumerate(row):
                with cols[col_index]:

                    if st.button(
                        f"{icon}  {label}",
                        key=(
                            f"user_mobile_btn_"
                            f"{page}_{home_view}_{row_index}_{col_index}"
                        ),
                        use_container_width=True,
                    ):
                        if page == "home":
                            st.session_state.page = "home"
                            st.session_state.home_view = home_view
                        else:
                            st.session_state.page = page

                        st.rerun()


# ================================================================
# USER DASHBOARD
# ================================================================

def render_user():

    # Existing global navbar remains untouched.
    render_navbar()

    # New mobile navigation only.
    render_user_mobile_nav()

    user_id = st.session_state.get("user_id")
    username = st.session_state.get("username", "")

    # ============================================================
    # EXISTING SIDEBAR - KEEP FOR PC
    # ============================================================

    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding:16px 0 8px;">
                <div style="
                    font-size:13px;
                    font-weight:600;
                    color:{C['primary_dark']};
                    margin-bottom:12px;
                    padding-bottom:8px;
                    border-bottom:1px solid {C['border']};
                ">
                    Navigation
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🌿 Analyse",
            use_container_width=True,
            key="user_sidebar_analyse",
        ):
            st.session_state.home_view = "accueil"
            st.session_state.page = "home"
            st.rerun()

        if st.button(
            "👤 Mon profil",
            use_container_width=True,
            key="user_sidebar_profile",
        ):
            st.session_state.page = "profile"
            st.rerun()

    # ============================================================
    # HEADER - EXISTING DESIGN
    # ============================================================

    st.markdown(
        f"""
        <div style="padding:28px 40px 0;">
            <div
                class="user-page-title"
                style="
                    font-size:22px;
                    font-weight:600;
                    color:{C['primary_dark']};
                    margin-bottom:4px;
                "
            >
                👤 Mon espace
            </div>

            <div style="
                font-size:14px;
                color:{C['text_mid']};
            ">
                Bienvenue, <strong>{username}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='height:20px'></div>",
        unsafe_allow_html=True,
    )

    # ============================================================
    # EXISTING DATA LOGIC
    # ============================================================

    analyses = get_user_analyses(user_id)

    # ============================================================
    # STATS
    # ============================================================

    total = len(analyses)

    correct_fb = sum(
        1
        for a in analyses
        if a.feedbacks and a.feedbacks[0].is_correct
    )

    high_sev = sum(
        1
        for a in analyses
        if a.severity == "high"
    )

    plants_set = set(
        a.plant_type
        for a in analyses
        if a.plant_type
    )

    c1, c2, c3, c4 = st.columns(4)

    for col, icon, val, label in [
        (c1, "🔍", total, "Analyses totales"),
        (c2, "✅", correct_fb, "Diagnostics validés"),
        (c3, "⚠️", high_sev, "Sévérité grave"),
        (c4, "🌿", len(plants_set), "Cultures analysées"),
    ]:
        with col:
            st.markdown(
                f"""
                <div style="
                    background:{C['bg_card']};
                    border:1px solid {C['border']};
                    border-radius:12px;
                    padding:20px;
                    text-align:center;
                ">
                    <div style="
                        font-size:28px;
                        margin-bottom:4px;
                    ">
                        {icon}
                    </div>

                    <div style="
                        font-size:26px;
                        font-weight:600;
                        color:{C['primary_dark']};
                    ">
                        {val}
                    </div>

                    <div style="
                        font-size:12px;
                        color:{C['text_mid']};
                        margin-top:4px;
                    ">
                        {label}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        "<div style='height:24px'></div>",
        unsafe_allow_html=True,
    )

    # ============================================================
    # TABS
    # ============================================================

    tab_hist, tab_stats, tab_settings = st.tabs(
        [
            "📋 Historique",
            "📊 Statistiques",
            "⚙️ Paramètres",
        ]
    )

    # ============================================================
    # HISTORIQUE
    # ============================================================

    with tab_hist:

        if not analyses:
            st.markdown(
                f"""
                <div style="
                    text-align:center;
                    padding:60px;
                    color:{C['text_muted']};
                ">
                    <div style="
                        font-size:48px;
                        margin-bottom:12px;
                    ">
                        📋
                    </div>

                    <div>
                        Aucune analyse pour le moment
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            for a in analyses:

                sev_colors = {
                    "none": ("#D4EDDA", "#1A5C2A"),
                    "low": ("#DFF0C8", "#3B6D11"),
                    "medium": ("#FFF0CC", "#7A5000"),
                    "high": ("#FDDCDC", "#8B1A1A"),
                }

                bg, fg = sev_colors.get(
                    a.severity,
                    ("#FFF0CC", "#7A5000"),
                )

                date_str = (
                    a.created_at.strftime("%d/%m/%Y %H:%M")
                    if a.created_at
                    else ""
                )

                st.markdown(
                    f"""
                    <div style="
                        background:{C['bg_card']};
                        border:1px solid {C['border']};
                        border-radius:10px;
                        padding:14px 18px;
                        margin-bottom:10px;
                        display:flex;
                        justify-content:space-between;
                        align-items:center;
                    ">
                        <div>
                            <div style="
                                font-size:14px;
                                font-weight:600;
                                color:{C['primary_dark']};
                                margin-bottom:4px;
                            ">
                                {a.disease_name}
                            </div>

                            <div style="
                                font-size:12px;
                                color:{C['text_mid']};
                            ">
                                🌿 {a.plant_type}
                                &nbsp;·&nbsp;
                                🎯 {round(a.confidence, 1)}%
                                &nbsp;·&nbsp;
                                🗓 {date_str}
                            </div>
                        </div>

                        <span style="
                            background:{bg};
                            color:{fg};
                            font-size:11px;
                            font-weight:600;
                            padding:4px 12px;
                            border-radius:12px;
                        ">
                            {a.severity}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # ============================================================
    # STATISTICS
    # ============================================================

    with tab_stats:

        if not analyses:
            st.info("Pas encore de données à afficher")

        else:

            st.markdown(
                f"""
                <div style="
                    font-size:14px;
                    font-weight:600;
                    color:{C['primary_dark']};
                    margin-bottom:12px;
                ">
                    Distribution par sévérité
                </div>
                """,
                unsafe_allow_html=True,
            )

            sev_counts = {
                "Saine": 0,
                "Légère": 0,
                "Modérée": 0,
                "Grave": 0,
            }

            sev_map = {
                "none": "Saine",
                "low": "Légère",
                "medium": "Modérée",
                "high": "Grave",
            }

            for a in analyses:
                key = sev_map.get(
                    a.severity,
                    "Modérée",
                )
                sev_counts[key] += 1

            df_sev = pd.DataFrame(
                list(sev_counts.items()),
                columns=["Sévérité", "Nombre"],
            )

            st.bar_chart(
                df_sev.set_index("Sévérité")
            )

            st.markdown(
                f"""
                <div style="
                    font-size:14px;
                    font-weight:600;
                    color:{C['primary_dark']};
                    margin:20px 0 12px;
                ">
                    Top maladies détectées
                </div>
                """,
                unsafe_allow_html=True,
            )

            disease_counts = {}

            for a in analyses:
                name = a.disease_name or "Inconnu"
                disease_counts[name] = (
                    disease_counts.get(name, 0) + 1
                )

            df_dis = pd.DataFrame(
                sorted(
                    disease_counts.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:5],
                columns=["Maladie", "Nombre"],
            )

            st.bar_chart(
                df_dis.set_index("Maladie")
            )

    # ============================================================
    # SETTINGS
    # ============================================================

    with tab_settings:

        st.markdown(
            f"""
            <div style="
                font-size:14px;
                font-weight:600;
                color:{C['primary_dark']};
                margin-bottom:16px;
            ">
                Informations du compte
            </div>
            """,
            unsafe_allow_html=True,
        )

        new_lang = st.selectbox(
            "Langue préférée",
            ["English", "Français", "دارجة", "العربية"],
            index=2,
            key="user_preferred_language",
        )

        st.markdown(
            "<div style='height:8px'></div>",
            unsafe_allow_html=True,
        )

        new_pass = st.text_input(
            "Nouveau mot de passe",
            type="password",
            key="user_new_password",
        )

        new_pass2 = st.text_input(
            "Confirmer mot de passe",
            type="password",
            key="user_new_password_confirm",
        )

        if st.button(
            "💾 Enregistrer les modifications",
            use_container_width=True,
            key="user_save_settings",
        ):

            if new_pass and new_pass != new_pass2:
                st.error(
                    "Les mots de passe ne correspondent pas"
                )

            else:
                db = SessionLocal()

                try:
                    from database.models import User
                    from auth.login import hash_password

                    user = (
                        db.query(User)
                        .filter(User.id == user_id)
                        .first()
                    )

                    if user:
                        user.language = new_lang

                        if new_pass:
                            user.password = hash_password(
                                new_pass
                            )

                    db.commit()

                    st.success(
                        "Modifications enregistrées !"
                    )

                finally:
                    db.close()
