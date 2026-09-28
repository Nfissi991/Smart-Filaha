# view/chat.py
import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

PROMPT = """أنت خبير فلاحة مغربي. جاوب بالدارجة/العربية بشكل بسيط وعملي
عن: الأمراض، السقي، التسميد، المواسم. كن مختصر ومفيد."""

# ── auto-detect model ──
def get_groq_model(api_key: str) -> str:
    """kayshuf awl model available u kaysta3mlo - ghir mn PREFERRED
       (llama-3.1-8b-instant w llama-3.3-70b-versatile tmsaw mn Groq f 16/08/2026)"""
    PREFERRED = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b",
    ]
    try:
        client = Groq(api_key=api_key)
        models = client.models.list()
        available = {m.id for m in models.data}
        for m in PREFERRED:
            if m in available:
                return m
    except:
        pass
    # fallback tabit
    return "openai/gpt-oss-20b"

@st.cache_data(ttl=300)
def get_model_cached(api_key: str) -> str:
    return get_groq_model(api_key)

def _get_client_and_model():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key or api_key.startswith("gsk_xxx"):
        return None, None, "⚠️ GROQ_API_KEY ناقصة — حط API key l7qi9iya f fichier .env"
    model = get_model_cached(api_key)
    client = Groq(api_key=api_key)
    return client, model, None

def render_chat_embedded():
    C_light = "#E6F4EB"

    if "chat" not in st.session_state:
        st.session_state.chat = []
    if "chat_input_counter" not in st.session_state:
        st.session_state.chat_input_counter = 0

    # 3rd rasa'il
    for role, msg in st.session_state.chat[-6:]:
        if role == "user":
            st.markdown(
                f'<div style="background:#F0F0F0;border-radius:10px;'
                f'padding:8px 12px;font-size:13px;margin-bottom:6px;">'
                f'👤 {msg}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div style="background:{C_light};border-radius:10px;'
                f'padding:8px 12px;font-size:13px;margin-bottom:6px;'
                f'color:#1C2B22;">{msg}</div>',
                unsafe_allow_html=True
            )

    input_key = f"chat_embed_input_{st.session_state.chat_input_counter}"

    col_in, col_btn = st.columns([5, 1])
    with col_in:
        user_input = st.text_input(
            "msg", placeholder="سول على أي حاجة فالفلاحة...",
            label_visibility="collapsed", key=input_key
        )
    with col_btn:
        send = st.button("إرسال", key="chat_embed_send",
                         use_container_width=True)

    if send and user_input.strip():
        msg = user_input.strip()
        # nzido counter bach l widget li jay ykon fer3a jdida (khawya)
        st.session_state.chat_input_counter += 1
        _send_message(msg)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🌿 أمراض شائعة", key="q1", use_container_width=True):
            _send_message("ما هي أكثر أمراض النباتات شيوعاً في المغرب؟")
    with c2:
        if st.button("💧 نصائح السقي", key="q2", use_container_width=True):
            _send_message("كيفاش نسقي مزيان؟")

def render_chat():
    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: #F4F6F4; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding: 24px 32px !important; max-width: 860px !important; margin: auto; }
    .stButton > button { background: #1E7A46 !important; color: white !important;
        border: none !important; border-radius: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🤖 المستشار الفلاحي")

    if st.button("⬅️ رجوع"):
        st.session_state.page = "home"
        st.rerun()

    if "chat" not in st.session_state:
        st.session_state.chat = []

    for role, msg in st.session_state.chat:
        with st.chat_message(role):
            st.write(msg)

    q = st.chat_input("سول على أي حاجة فالفلاحة...")
    if q:
        _send_message_chat(q)
        st.rerun()

def _send_message(text: str):
    if (st.session_state.chat and
            st.session_state.chat[-1] == ("user", text)):
        return

    st.session_state.chat.append(("user", text))
    client, model, error = _get_client_and_model()

    if error:
        st.session_state.chat.append(("assistant", error))
        st.rerun()
        return

    try:
        r = client.chat.completions.create(
            model=model,
            max_tokens=400,
            messages=[{"role": "system", "content": PROMPT}]
                     + [{"role": m, "content": c}
                        for m, c in st.session_state.chat]
        )
        answer = r.choices[0].message.content
    except Exception as e:
        answer = f"خطأ: {e}"

    st.session_state.chat.append(("assistant", answer))
    st.rerun()

def _send_message_chat(text: str):
    st.session_state.chat.append(("user", text))

    with st.chat_message("user"):
        st.write(text)

    client, model, error = _get_client_and_model()

    if error:
        with st.chat_message("assistant"):
            st.error(error)
        st.session_state.chat.append(("assistant", error))
        return

    with st.chat_message("assistant"):
        with st.spinner("كيفكر..."):
            try:
                r = client.chat.completions.create(
                    model=model,
                    max_tokens=400,
                    messages=[{"role": "system", "content": PROMPT}]
                             + [{"role": m, "content": c}
                                for m, c in st.session_state.chat]
                )
                answer = r.choices[0].message.content
            except Exception as e:
                answer = f"خطأ: {e}"
            st.write(answer)

    st.session_state.chat.append(("assistant", answer))