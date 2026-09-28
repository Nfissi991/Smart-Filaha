import streamlit as st
import html

from services.message_service import (
    get_my_conversations,
    get_conversation,
    send_message,
    mark_messages_read,
)

from view.home import render_sidebar, render_topbar, inject_css


def render_messages():

    # =========================================================
    # GLOBAL DESIGN
    # =========================================================
    inject_css()
    render_sidebar()

    # =========================================================
    # MESSAGES CSS
    # =========================================================
    st.markdown("""
<style>
.messages-title {
    color: #18362A;
    font-size: 24px;
    font-weight: 800;
    margin-top: 5px;
    margin-bottom: 3px;
}

.messages-subtitle {
    color: #7A8B82;
    font-size: 12px;
    margin-bottom: 18px;
}

.msg-layout {
    background: white;
    border: 1px solid #E1E9E4;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 18px rgba(20,60,40,.05);
}

/* HEADER */
.msg-header {
    height: 72px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    border-bottom: 1px solid #E5EBE7;
    background: white;
}

.msg-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    background: #E7F3EB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    margin-right: 11px;
}

.msg-name {
    color: #18362A;
    font-size: 14px;
    font-weight: 800;
}

.msg-role {
    color: #8A9991;
    font-size: 10px;
    margin-top: 3px;
}

.msg-online {
    margin-left: auto;
    background: #EAF6EE;
    color: #287348;
    border-radius: 20px;
    padding: 6px 10px;
    font-size: 10px;
    font-weight: 700;
}

.msg-online-dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    background: #42A866;
    border-radius: 50%;
    margin-right: 4px;
}

/* CHAT */
.msg-chat {
    background: #F8FAF8;
    min-height: 450px;
    padding: 22px 20px;
}

.msg-row {
    display: flex;
    align-items: flex-end;
    gap: 8px;
    margin-bottom: 14px;
}

.msg-row.mine {
    justify-content: flex-end;
}

.msg-small-avatar {
    width: 30px;
    height: 30px;
    min-width: 30px;
    border-radius: 50%;
    background: #E7F3EB;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

.msg-bubble {
    max-width: 65%;
    background: white;
    border: 1px solid #DFE8E2;
    color: #294338;
    padding: 10px 14px;
    border-radius: 15px 15px 15px 4px;
    font-size: 12px;
    line-height: 1.55;
    box-shadow: 0 2px 6px rgba(20,60,40,.04);
}

.msg-bubble.mine {
    background: #1E7A46;
    border: none;
    color: white;
    border-radius: 15px 15px 4px 15px;
}

/* EMPTY */
.msg-empty {
    min-height: 420px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
}

.msg-empty-icon {
    font-size: 40px;
    margin-bottom: 8px;
}

.msg-empty-title {
    color: #53665C;
    font-size: 14px;
    font-weight: 700;
}

.msg-empty-text {
    color: #94A099;
    font-size: 11px;
    margin-top: 5px;
}

/* LEFT TITLE */
.msg-list-title {
    color: #18362A;
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 3px;
}

.msg-list-subtitle {
    color: #93A098;
    font-size: 9px;
    margin-bottom: 12px;
}

/* CONVERSATION BUTTONS */
div[data-testid="column"]:first-child .stButton > button {
    background: white !important;
    color: #294338 !important;
    border: 1px solid #E1E8E3 !important;
    border-radius: 11px !important;
    font-size: 12px !important;
    text-align: left !important;
    padding: 10px 12px !important;
    margin-bottom: 5px !important;
}

div[data-testid="column"]:first-child .stButton > button:hover {
    background: #EAF5ED !important;
    border-color: #5B8C6B !important;
    color: #1E7A46 !important;
}

/* INPUT */
div[data-testid="stChatInput"] {
    padding: 10px 15px 15px 15px;
    background: white;
}

div[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 1px solid #DCE6DF !important;
}
</style>
""", unsafe_allow_html=True)

    # =========================================================
    # TOP BAR
    # =========================================================
    render_topbar()

    # =========================================================
    # USER
    # =========================================================
    user_id = st.session_state.get("user_id")

    if not user_id:
        st.error("Utilisateur non connecté.")
        return

    # =========================================================
    # CONTACTS
    # =========================================================
    contacts = get_my_conversations(user_id)

    contact_id = st.session_state.get("contact_adviser_id")

    if contact_id is not None:
        selected_id = contact_id
    elif contacts:
        selected_id = contacts[0].id
        st.session_state["contact_adviser_id"] = selected_id
    else:
        selected_id = None

    # =========================================================
    # TITLE
    # =========================================================
    st.markdown(
        '<div class="messages-title">💬 Messages</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="messages-subtitle">Échangez avec votre conseiller agricole</div>',
        unsafe_allow_html=True
    )

    # =========================================================
    # NO CONTACTS
    # =========================================================
    if not contacts:

        st.markdown(
            '<div class="msg-layout">'
            '<div class="msg-empty">'
            '<div class="msg-empty-icon">💬</div>'
            '<div class="msg-empty-title">Aucune conversation</div>'
            '<div class="msg-empty-text">'
            'Ouvrez une publication puis cliquez sur « Contacter le conseiller ».'
            '</div>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        return

    # =========================================================
    # SELECTED CONTACT
    # =========================================================
    selected_user = next(
        (u for u in contacts if u.id == selected_id),
        None
    )

    if selected_user is None:
        selected_user = contacts[0]
        selected_id = selected_user.id
        st.session_state["contact_adviser_id"] = selected_id

    # =========================================================
    # GET MESSAGES
    # =========================================================
    conversation = get_conversation(
        user_id,
        selected_id
    )

    mark_messages_read(
        user_id,
        selected_id
    )

    # =========================================================
    # TWO COLUMNS
    # =========================================================
    left, right = st.columns(
        [3, 7],
        gap="small"
    )

    # =========================================================
    # LEFT
    # =========================================================
    with left:

        st.markdown(
            '<div class="msg-list-title">Conversations</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="msg-list-subtitle">Vos conversations récentes</div>',
            unsafe_allow_html=True
        )

        for contact in contacts:

            if st.button(
                f"👤  {contact.username}",
                key=f"conversation_{contact.id}",
                use_container_width=True
            ):
                st.session_state["contact_adviser_id"] = contact.id
                st.rerun()

    # =========================================================
    # RIGHT
    # =========================================================
    with right:

        username = html.escape(
            selected_user.username
        )

        # HEADER
        st.markdown(
            '<div class="msg-layout">'
            '<div class="msg-header">'
            '<div class="msg-avatar">👨‍🌾</div>'
            '<div>'
            f'<div class="msg-name">{username}</div>'
            '<div class="msg-role">Conseiller agricole</div>'
            '</div>'
            '<div class="msg-online">'
            '<span class="msg-online-dot"></span>'
            'En ligne'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )

        # CHAT
        st.markdown(
            '<div class="msg-chat">',
            unsafe_allow_html=True
        )

        if not conversation:

            st.markdown(
                '<div class="msg-empty">'
                '<div class="msg-empty-icon">👋</div>'
                '<div class="msg-empty-title">'
                'Commencez la conversation'
                '</div>'
                '<div class="msg-empty-text">'
                'Envoyez votre premier message.'
                '</div>'
                '</div>',
                unsafe_allow_html=True
            )

        else:

            for message in conversation:

                content = html.escape(
                    message.content
                )

                is_mine = (
                    message.sender_id == user_id
                )

                if is_mine:

                    st.markdown(
                        '<div class="msg-row mine">'
                        f'<div class="msg-bubble mine">{content}</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        '<div class="msg-row">'
                        '<div class="msg-small-avatar">👨‍🌾</div>'
                        f'<div class="msg-bubble">{content}</div>'
                        '</div>',
                        unsafe_allow_html=True
                    )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        # =====================================================
        # SEND MESSAGE
        # =====================================================
        message_text = st.chat_input(
            "Écrivez votre message..."
        )

        if message_text:

            send_message(
                sender_id=user_id,
                receiver_id=selected_id,
                content=message_text
            )

            st.rerun()

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )