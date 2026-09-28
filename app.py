import streamlit as st

from database.db import init_db
from auth.login import is_logged_in, is_admin, is_conseiller, show_login_page
from config.settings import APP_NAME, APP_ICON


st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
)

init_db()

if not is_logged_in():
    show_login_page()
    st.stop()

page = st.session_state.get("page", "home")

if page == "home":
    from view.home import render_home
    render_home()

elif page == "profile":
    from view.dashboard_user import render_user
    render_user()

elif page == "conseiller":
    if is_conseiller():
        from view.dashboard_conseiller import render_conseiller
        render_conseiller()
    else:
        st.session_state.page = "home"
        st.rerun()

elif page == "dashboard":
    if is_admin():
        from view.dashboard_admin import render_admin
        render_admin()
    else:
        st.session_state.page = "home"
        st.warning("Accès réservé aux administrateurs.")
        st.rerun()
elif page == "sensors":
       from view.sensors import render_sensors
       render_sensors()
    
elif page == "publications":
       from view.publications import render_publications
       render_publications()

elif page == "messages":
     from view.messages import render_messages
     render_messages()
else:
    st.session_state.page = "home"
    st.rerun()