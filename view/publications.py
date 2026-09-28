# view/publications.py
import streamlit as st
from services.publication_service import get_published_publications


def render_publications():
    st.title("📢 Conseils & Publications")
    st.caption("Découvrez les conseils et publications des conseillers agricoles.")

    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()

    rows = get_published_publications()

    if not rows:
        st.info("Aucune publication disponible pour le moment.")
        return

    for publication, conseiller in rows:
        with st.container(border=True):
            st.markdown(f"### {publication.title}")
            st.caption(f"🧑‍🌾 {conseiller.username} · {publication.publication_type}")

            if publication.image_path:
                try:
                    st.image(publication.image_path, use_container_width=True)
                except Exception:
                    pass

            st.write(publication.content)
            st.caption(publication.created_at.strftime("%d/%m/%Y %H:%M"))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💬 Contacter le conseiller", key=f"contact_{publication.id}",
                             use_container_width=True):
                    st.session_state["contact_adviser_id"] = conseiller.id
                    st.session_state["page"] = "messages"
                    st.rerun()
            with col2:
                if publication.product_id:
                    st.info("🛒 Cette publication est liée à un produit.")