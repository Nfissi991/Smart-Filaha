# view/publications.py
import html
import os

import streamlit as st

from database.db import SessionLocal
from database.models import Product
from services.publication_service import get_published_publications

TYPE_STYLES = {
    "conseil": ("💡 Conseil", "#e8f5ee", "#116641"),
    "article": ("📰 Article", "#eaf1fb", "#1d5fa8"),
    "annonce": ("📣 Annonce", "#fff4e0", "#a86a0a"),
    "produit": ("🛒 Produit", "#f3ebfb", "#6b3fa0"),
}

CSS = """
<style>
.pub-img {
    width: 100%;
    height: 260px;
    border-radius: 14px;
    background: #f4f7f5;
    border: 1px solid #e3ebe6;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden;
}
.pub-img .pub-noimg { font-size: 54px; opacity: .35; }
[class*="st-key-pubimg_"] [data-testid="stImage"] { width: 100% !important; }
[class*="st-key-pubimg_"] img {
    width: 100% !important;
    height: 260px !important;
    object-fit: contain !important;
    background: #f4f7f5;
    border: 1px solid #e3ebe6;
    border-radius: 14px;
}
.pub-title { font-size: 22px; font-weight: 800; color: #18362A; margin: 2px 0 8px; line-height: 1.25; }
.pub-meta { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.pub-author { display: flex; align-items: center; gap: 8px; }
.pub-avatar { width: 32px; height: 32px; border-radius: 50%; background: #e8f5ee;
              display: flex; align-items: center; justify-content: center; font-size: 17px; }
.pub-author-name { font-size: 13px; font-weight: 800; color: #18362A; line-height: 1.1; }
.pub-author-role { font-size: 11px; color: #7A8B82; }
.pub-chip { font-size: 11px; font-weight: 800; padding: 4px 10px; border-radius: 999px; }
.pub-price { background: #116641; color: #fff; }
.pub-content { color: #2f4a3c; font-size: 14px; line-height: 1.6; white-space: pre-line;
               margin: 4px 0 10px; }
.pub-date { color: #93a29a; font-size: 12px; }
@media (max-width: 900px) {
    .pub-img, [class*="st-key-pubimg_"] img { height: 220px !important; }
    .pub-title { font-size: 19px; }
}
</style>
"""


def _valid_image(path):
    """Retourne le chemin/URL si l'image est utilisable, sinon None."""
    if not path:
        return None
    path = str(path)
    if path.startswith(("http://", "https://")):
        return path
    return path if os.path.exists(path) else None


def _get_product(product_id):
    if not product_id:
        return None
    db = SessionLocal()
    try:
        return db.query(Product).filter(Product.id == product_id).first()
    except Exception:
        return None
    finally:
        db.close()


def render_publications():
    st.markdown(CSS, unsafe_allow_html=True)
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
        label, bg, fg = TYPE_STYLES.get(
            (publication.publication_type or "conseil").lower(),
            ("📌 Publication", "#eef2ef", "#3b5a4a"),
        )
        product = _get_product(publication.product_id)
        img = _valid_image(publication.image_path) or (
            _valid_image(product.image_path) if product else None
        )

        with st.container(border=True):
            col_img, col_txt = st.columns([1, 1.6], gap="medium")

            with col_img:
                if img:
                    with st.container(key=f"pubimg_{publication.id}"):
                        try:
                            st.image(img, use_container_width=True)
                        except Exception:
                            st.markdown(
                                '<div class="pub-img"><span class="pub-noimg">🌿</span></div>',
                                unsafe_allow_html=True,
                            )
                else:
                    st.markdown(
                        '<div class="pub-img"><span class="pub-noimg">🌿</span></div>',
                        unsafe_allow_html=True,
                    )

            with col_txt:
                price_chip = ""
                if product is not None and product.price is not None:
                    price_chip = f'<span class="pub-chip pub-price">{product.price:g} MAD</span>'
                st.markdown(
                    f'<div class="pub-title" dir="auto">{html.escape(publication.title or "")}</div>'
                    '<div class="pub-meta">'
                    '<div class="pub-author">'
                    '<div class="pub-avatar">👨‍🌾</div>'
                    '<div>'
                    f'<div class="pub-author-name">{html.escape(conseiller.username)}</div>'
                    '<div class="pub-author-role">Conseiller agricole</div>'
                    '</div></div>'
                    f'<span class="pub-chip" style="background:{bg};color:{fg};">{label}</span>'
                    f'{price_chip}'
                    '</div>'
                    f'<div class="pub-content" dir="auto">{html.escape(publication.content or "")}</div>'
                    f'<div class="pub-date">{publication.created_at.strftime("%d/%m/%Y %H:%M")}</div>',
                    unsafe_allow_html=True,
                )
                if st.button(
                    "💬 Contacter le conseiller",
                    key=f"contact_{publication.id}",
                    use_container_width=True,
                ):
                    st.session_state["contact_adviser_id"] = conseiller.id
                    st.session_state["page"] = "messages"
                    st.rerun()