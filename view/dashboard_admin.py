# view/dashboard_admin.py
import streamlit as st
import pandas as pd
from database.db import SessionLocal
from database.models import User, Analysis
from components.navbar import render_navbar
from config.settings import COLORS
from services.publication_service import (
    get_all_publications,
    set_publication_status,
    delete_publication,
)

C = COLORS

def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).order_by(User.created_at.desc()).all()
    finally:
        db.close()

def get_all_analyses():
    db = SessionLocal()
    try:
        return db.query(Analysis).order_by(Analysis.created_at.desc()).all()
    finally:
        db.close()

def toggle_user_status(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_active = not user.is_active
            db.commit()
    finally:
        db.close()

def approve_conseiller(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_approved = True
            db.commit()
    finally:
        db.close()

def reject_conseiller(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)   # كنمسحو الحساب المرفوض بالكامل
            db.commit()
    finally:
        db.close()

def revoke_conseiller(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_approved = False
            db.commit()
    finally:
        db.close()

def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
    finally:
        db.close()

def render_admin():
    render_navbar()

    # sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px;">
            <div style="font-size:13px;font-weight:600;color:{C['primary_dark']};
                        margin-bottom:12px;padding-bottom:8px;
                        border-bottom:1px solid {C['border']};">Administration</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🌿 Analyse",       use_container_width=True):
            st.session_state.home_view = "accueil"
            st.session_state.page = "home";      st.rerun()
        if st.button("👤 Mon profil",    use_container_width=True):
            st.session_state.page = "profile";   st.rerun()
        if st.button("⚙️ Dashboard",     use_container_width=True):
            st.session_state.page = "dashboard"; st.rerun()

    # header
    st.markdown(f"""
    <div style="padding:28px 40px 0;">
        <div style="font-size:22px;font-weight:600;color:{C['primary_dark']};
                    margin-bottom:4px;">⚙️ Dashboard Admin</div>
        <div style="font-size:14px;color:{C['text_mid']};">
            Gestion complète de l'application
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    users    = get_all_users()
    analyses = get_all_analyses()

    # ── stats globales ──
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label in [
        (c1, "👥", len(users),                             "Utilisateurs"),
        (c2, "🔍", len(analyses),                          "Analyses totales"),
        (c3, "⚠️", sum(1 for a in analyses if a.severity == "high"), "Cas graves"),
        (c4, "✅", sum(1 for u in users if u.is_active),   "Comptes actifs"),
    ]:
        with col:
            st.markdown(f"""
            <div style="background:{C['bg_card']};border:1px solid {C['border']};
                        border-radius:12px;padding:20px;text-align:center;">
                <div style="font-size:28px;margin-bottom:4px;">{icon}</div>
                <div style="font-size:26px;font-weight:600;
                            color:{C['primary_dark']};">{val}</div>
                <div style="font-size:12px;color:{C['text_mid']};
                            margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ── tabs ──
    tab_users, tab_pubs_admin, tab_analyses, tab_model, tab_system = st.tabs([
        "👥 Utilisateurs", "📢 Publications", "📊 Analyses", "🤖 Modèle IA", "🖥️ Système"
    ])

    # ── UTILISATEURS ──
    with tab_users:
        st.markdown(f"""
        <div style="font-size:14px;font-weight:600;color:{C['primary_dark']};
                    margin-bottom:16px;">{len(users)} utilisateurs enregistrés</div>
        """, unsafe_allow_html=True)

        # créer admin
        with st.expander("➕ Créer un compte admin"):
            a_user  = st.text_input("Nom d'utilisateur", key="new_admin_user")
            a_email = st.text_input("Email",              key="new_admin_email")
            a_pass  = st.text_input("Mot de passe", type="password", key="new_admin_pass")
            if st.button("Créer admin", key="btn_create_admin"):
                if a_user and a_email and a_pass:
                    from auth.login import create_user, get_user_by_username
                    if get_user_by_username(a_user):
                        st.error("Nom d'utilisateur déjà utilisé")
                    else:
                        create_user(a_user, a_email, a_pass, role="admin")
                        st.success("Compte admin créé !")
                        st.rerun()

        # liste users
        for u in users:
            status_color = "#D4EDDA" if u.is_active else "#FDDCDC"
            status_text  = "Actif"   if u.is_active else "Désactivé"
            role_color   = C["primary_mid"] if u.role == "admin" else "#5A8A6A"
            date_str     = u.created_at.strftime("%d/%m/%Y") if u.created_at else ""

            col_info, col_btns = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div style="background:{C['bg_card']};border:1px solid {C['border']};
                            border-radius:10px;padding:12px 16px;margin-bottom:8px;">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
                        <span style="font-size:13px;font-weight:600;
                                     color:{C['primary_dark']};">
                            👤 {u.username}
                        </span>
                        <span style="background:{role_color};color:white;font-size:10px;
                                     font-weight:600;padding:2px 8px;border-radius:10px;">
                            {u.role.upper()}
                        </span>
                        <span style="background:{status_color};font-size:10px;
                                     padding:2px 8px;border-radius:10px;">
                            {status_text}
                        </span>
                    </div>
                    <div style="font-size:12px;color:{C['text_mid']};">
                        ✉️ {u.email} &nbsp;·&nbsp; 🗓 {date_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # ✅ actions par ligne
            with col_btns:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                is_pending = (u.role == "conseiller" and not u.is_approved)

                if is_pending:
                    c_ok, c_no = st.columns(2)
                    with c_ok:
                        if st.button("✅", key=f"approve_{u.id}", help="Approuver"):
                            approve_conseiller(u.id)
                            st.rerun()
                    with c_no:
                        if st.button("❌", key=f"reject_{u.id}", help="Rejeter"):
                            reject_conseiller(u.id)
                            st.rerun()

                elif u.id != st.session_state.get("user_id"):
                    if u.role == "conseiller":
                        c_lock, c_revoke = st.columns(2)
                        with c_lock:
                            if st.button("🔒" if u.is_active else "🔓",
                                         key=f"toggle_{u.id}", help="Activer/Désactiver"):
                                toggle_user_status(u.id)
                                st.rerun()
                        with c_revoke:
                            if st.button("🚫", key=f"revoke_{u.id}",
                                         help="Révoquer le statut conseiller"):
                                revoke_conseiller(u.id)
                                st.rerun()
                    else:
                        if st.button("🔒" if u.is_active else "🔓",
                                     key=f"toggle_{u.id}", help="Activer/Désactiver"):
                            toggle_user_status(u.id)
                            st.rerun()

    # ── PUBLICATIONS ──
    with tab_pubs_admin:
        pubs = get_all_publications()

        st.markdown(f"""
        <div style="font-size:14px;font-weight:600;color:{C['primary_dark']};
                    margin-bottom:16px;">{len(pubs)} publications au total</div>
        """, unsafe_allow_html=True)

        if not pubs:
            st.info("Aucune publication dans la base.")
        else:
            for pub, conseiller in pubs:
                pending_flag = " ⏳ conseiller non approuvé" if not conseiller.is_approved else ""
                inactive_flag = " 🔒 conseiller désactivé" if not conseiller.is_active else ""
                with st.container(border=True):
                    st.markdown(
                        f"**{pub.title}** — {pub.publication_type} · statut: `{pub.status}`"
                        f"{pending_flag}{inactive_flag}"
                    )
                    st.caption(f"🧑‍🌾 {conseiller.username} · {pub.created_at.strftime('%d/%m/%Y %H:%M')}")
                    st.write(pub.content)

                    if pub.image_path:
                        try:
                            st.image(pub.image_path, width=200)
                        except Exception:
                            pass

                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if pub.status != "published" and st.button("✅ Publier", key=f"pub_show_{pub.id}"):
                            set_publication_status(pub.id, "published")
                            st.rerun()
                    with c2:
                        if pub.status != "hidden" and st.button("🚫 Masquer", key=f"pub_hide_{pub.id}"):
                            set_publication_status(pub.id, "hidden")
                            st.rerun()
                    with c3:
                        if st.button("🗑️ Supprimer", key=f"pub_del_{pub.id}"):
                            delete_publication(pub.id)
                            st.rerun()

    # ── ANALYSES ──
    with tab_analyses:
        if not analyses:
            st.info("Aucune analyse enregistrée")
        else:
            # graphique maladies
            st.markdown(f"""
            <div style="font-size:14px;font-weight:600;color:{C['primary_dark']};
                        margin-bottom:12px;">Top 10 maladies détectées</div>
            """, unsafe_allow_html=True)

            disease_counts = {}
            for a in analyses:
                name = a.disease_name or "Inconnu"
                disease_counts[name] = disease_counts.get(name, 0) + 1

            df = pd.DataFrame(
                sorted(disease_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                columns=["Maladie", "Nombre"]
            )
            st.bar_chart(df.set_index("Maladie"))

            # tableau récent
            st.markdown(f"""
            <div style="font-size:14px;font-weight:600;color:{C['primary_dark']};
                        margin:20px 0 12px;">20 dernières analyses</div>
            """, unsafe_allow_html=True)

            for a in analyses[:20]:
                date_str = a.created_at.strftime("%d/%m/%Y %H:%M") if a.created_at else ""
                sev_colors = {
                    "none": ("#D4EDDA","#1A5C2A"), "low": ("#DFF0C8","#3B6D11"),
                    "medium": ("#FFF0CC","#7A5000"), "high": ("#FDDCDC","#8B1A1A"),
                }
                bg, fg = sev_colors.get(a.severity, ("#FFF0CC","#7A5000"))
                st.markdown(f"""
                <div style="background:{C['bg_card']};border:1px solid {C['border']};
                            border-radius:8px;padding:10px 14px;margin-bottom:6px;
                            display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:13px;font-weight:500;
                                    color:{C['primary_dark']};">{a.disease_name}</div>
                        <div style="font-size:11px;color:{C['text_mid']};">
                            🌿 {a.plant_type} · 🎯 {round(a.confidence,1)}% · 🗓 {date_str}
                        </div>
                    </div>
                    <span style="background:{bg};color:{fg};font-size:11px;
                                 font-weight:600;padding:3px 10px;border-radius:10px;">
                        {a.severity}
                    </span>
                </div>
                """, unsafe_allow_html=True)

    # ── MODÈLE IA ──
    with tab_model:
        st.markdown(f"""
        <div style="background:{C['bg_card']};border:1px solid {C['border']};
                    border-radius:12px;padding:24px;margin-bottom:16px;">
            <div style="font-size:15px;font-weight:600;color:{C['primary_dark']};
                        margin-bottom:16px;">🤖 Informations du modèle</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="font-size:13px;color:{C['text_mid']};">Fichier</div>
                <div style="font-size:13px;color:{C['text_dark']};">archive_best_model.h5</div>
                <div style="font-size:13px;color:{C['text_mid']};">Architecture</div>
                <div style="font-size:13px;color:{C['text_dark']};">MobileNetV2 — CNN</div>
                <div style="font-size:13px;color:{C['text_mid']};">Classes</div>
                <div style="font-size:13px;color:{C['text_dark']};">38 maladies</div>
                <div style="font-size:13px;color:{C['text_mid']};">Précision</div>
                <div style="font-size:13px;font-weight:600;color:#1D9E75;">96.4%</div>
                <div style="font-size:13px;color:{C['text_mid']};">Dataset</div>
                <div style="font-size:13px;color:{C['text_dark']};">PlantVillage — 3.5M images</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="font-size:14px;font-weight:600;color:{C['primary_dark']};
                    margin-bottom:12px;">🔄 Mettre à jour le modèle</div>
        """, unsafe_allow_html=True)

        new_model = st.file_uploader(
            "Importer un nouveau modèle (.h5)",
            type=["h5"],
            key="new_model_upload"
        )
        if new_model:
            if st.button("💾 Remplacer le modèle actuel", type="primary"):
                with open("archive_best_model.h5", "wb") as f:
                    f.write(new_model.getbuffer())
                st.cache_resource.clear()
                st.success("Modèle mis à jour ! Redémarrez l'application.")

    # ── SYSTÈME ──
    with tab_system:
        import platform, sys, os

        st.markdown(f"""
        <div style="background:{C['bg_card']};border:1px solid {C['border']};
                    border-radius:12px;padding:24px;">
            <div style="font-size:15px;font-weight:600;color:{C['primary_dark']};
                        margin-bottom:16px;">🖥️ Informations système</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div style="font-size:13px;color:{C['text_mid']};">OS</div>
                <div style="font-size:13px;color:{C['text_dark']};">{platform.system()} {platform.release()}</div>
                <div style="font-size:13px;color:{C['text_mid']};">Python</div>
                <div style="font-size:13px;color:{C['text_dark']};">{sys.version.split()[0]}</div>
                <div style="font-size:13px;color:{C['text_mid']};">Répertoire</div>
                <div style="font-size:13px;color:{C['text_dark']};">{os.getcwd()}</div>
                <div style="font-size:13px;color:{C['text_mid']};">DB</div>
                <div style="font-size:13px;color:{C['text_dark']};">SQLite (local)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        col_r, col_c = st.columns(2)
        with col_r:
            if st.button("🔄 Redémarrer l'app", use_container_width=True):
                st.cache_resource.clear()
                st.rerun()
        with col_c:
            if st.button("🗑️ Vider le cache", use_container_width=True):
                st.cache_resource.clear()
                st.cache_data.clear()
                st.success("Cache vidé !")