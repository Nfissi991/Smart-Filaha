# components/navbar.py
import streamlit as st
import datetime
from config.settings import COLORS, APP_NAME, APP_ICON
from auth.login import is_logged_in, is_admin, logout

def render_navbar(lang_label: str = ""):
    C   = COLORS
    now = datetime.datetime.now().strftime("%d %b %Y  %H:%M")

    # badge role
    if is_logged_in():
        username = st.session_state.get("username", "")
        role     = st.session_state.get("role", "user")
        badge_color = C["primary_mid"] if role == "admin" else "#5A8A6A"
        badge_label = "Admin" if role == "admin" else "User"
        user_html = (
            '<div style="display:flex;align-items:center;gap:10px;">'
            f'<span style="background:{badge_color};color:{C["accent_beige"]};'
            f'font-size:11px;font-weight:600;padding:3px 10px;border-radius:12px;">'
            f'{badge_label}</span>'
            f'<span style="color:{C["accent_green"]};font-size:13px;">👤 {username}</span>'
            '</div>'
        )
    else:
        user_html = ""

    st.markdown(f"""
    <div style="background:{C['primary_dark']};padding:14px 40px;
                display:flex;align-items:center;justify-content:space-between;">
        <div style="display:flex;align-items:center;gap:10px;
                    color:{C['accent_green']};font-size:17px;font-weight:600;">
            {APP_ICON}
            <span style="color:{C['accent_beige']};">{APP_NAME}</span>
        </div>
        <div style="display:flex;align-items:center;gap:20px;">
            {user_html}
            <span style="color:#6B9E7A;font-size:12px;">{now}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # bouton logout en dehors du markdown
    if is_logged_in():
        col1, col2, col3 = st.columns([8, 1, 1])
        with col3:
            if st.button("🚪", help="Déconnexion", key="btn_logout"):
                logout()
                st.rerun()

def render_stats_bar(total: int, last_disease: str,
                     last_plant: str, T: dict):
    C = COLORS
    st.markdown(f"""
    <div style="background:{C['primary_light']};padding:14px 40px;
                display:flex;border-bottom:1px solid {C['primary_dark']};">
        <div style="flex:1;text-align:center;border-right:1px solid #2E4F3E;padding:0 20px;">
            <div style="font-size:22px;font-weight:600;color:{C['accent_green']};">{total}</div>
            <div style="font-size:11px;color:#6B9E7A;text-transform:uppercase;
                        letter-spacing:0.06em;margin-top:2px;">{T['stat_analyzed']}</div>
        </div>
        <div style="flex:1;text-align:center;border-right:1px solid #2E4F3E;padding:0 20px;">
            <div style="font-size:22px;font-weight:600;color:{C['accent_green']};">{last_disease}</div>
            <div style="font-size:11px;color:#6B9E7A;text-transform:uppercase;
                        letter-spacing:0.06em;margin-top:2px;">{T['stat_diseases']}</div>
        </div>
        <div style="flex:1;text-align:center;border-right:1px solid #2E4F3E;padding:0 20px;">
            <div style="font-size:22px;font-weight:600;color:{C['accent_green']};">{last_plant}</div>
            <div style="font-size:11px;color:#6B9E7A;text-transform:uppercase;
                        letter-spacing:0.06em;margin-top:2px;">{T['stat_plants']}</div>
        </div>
        <div style="flex:1;text-align:center;padding:0 20px;">
            <div style="font-size:22px;font-weight:600;color:{C['accent_green']};">96.4%</div>
            <div style="font-size:11px;color:#6B9E7A;text-transform:uppercase;
                        letter-spacing:0.06em;margin-top:2px;">{T['stat_accuracy']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)