import os
import streamlit as st
from datetime import datetime
import google.generativeai as genai
import random
import time

# === API Setup ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDyv6AzhE-qjFUwUohlht4e8cCChDxa4jc"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat_session = model.start_chat(history=[])

# === Utility Functions ===
def get_time():
    return datetime.now().strftime("%I:%M %p")

def build_prompt(chat_log):
    system_prompt = (
        "You are AI-Assistant, a friendly chatbot. Use emojis and be casual like Instagram DMs, "
        "but always be factual and helpful."
    )
    conversation = "\n".join([f"{s}: {m}" for s, m, _ in chat_log[-6:]])
    return f"{system_prompt}\n{conversation}\nUser:"

def load_sticker():
    return random.choice(["✨", "💬", "🌟", "😊", "👍", "🦾", "🎉", "🤖"])

def typing_effect(text, container, delay=0.03):
    output = ""
    for char in text:
        output += char
        container.markdown(
            f"<div class='bubble bot'><span>{output}<span class='blink'>▌</span></span></div>",
            unsafe_allow_html=True
        )
        time.sleep(delay)
    container.markdown(f"<div class='bubble bot'>{output}</div>", unsafe_allow_html=True)

# === Themes ===
themes = {
    "Light": {"user_bg": "#e1f5fe", "bot_bg": "#fce4ec", "text_color": "#000", "bg_color": "#fafafa"},
    "Dark": {"user_bg": "#2c2c2c", "bot_bg": "#3a3a3a", "text_color": "#fff", "bg_color": "#1e1e1e"},
    "Sunset": {"user_bg": "#ffcccb", "bot_bg": "#ffe4b5", "text_color": "#000", "bg_color": "#fff5ee"}
}

# === Streamlit Config ===
st.set_page_config(page_title="AI-Assistant", page_icon="💬", layout="centered")

# === Session State ===
if "chat_log" not in st.session_state:
    st.session_state.chat_log = []
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# === Sidebar ===
with st.sidebar:
    st.header("🎨 Theme Settings")
    selected_theme = st.selectbox("Choose Theme", list(themes.keys()))
    st.session_state.theme = selected_theme
    theme = themes[selected_theme]

    st.markdown(f"🕒 **Time:** {datetime.now().strftime('%A, %d %B %Y %I:%M %p')}")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_log.clear()
        st.session_state.intro_done = False

    st.download_button(
        "📥 Download Chat",
        data="\n".join([f"[{t}] {s}: {m}" for s, m, t in st.session_state.chat_log]),
        file_name="chat_log.txt",
        mime="text/plain"
    )

# === CSS Styling ===
st.markdown(f"""
    <style>
        .bubble {{
            padding: 0.75rem 1rem;
            border-radius: 1.25rem;
            font-size: 1rem;
            max-width: 75%;
            width: fit-content;
            animation: fadeIn 0.25s ease-in-out;
            font-family: 'Segoe UI', sans-serif;
            word-break: break-word;
            display: inline-block;
        }}
        .user {{
            background-color: {theme['user_bg']};
            color: {theme['text_color']};
            margin-left: auto;
            margin-right: 0;
            text-align: right;
        }}
        .bot {{
            background-color: {theme['bot_bg']};
            color: {theme['text_color']};
            margin-right: auto;
            margin-left: 0;
            text-align: left;
        }}
        .timestamp {{
            font-size: 0.7rem;
            color: #888;
            margin-bottom: 1rem;
            text-align: center;
        }}
        section.main > div {{
            background-color: {theme['bg_color']};
        }}
        @keyframes fadeIn {{
            0% {{ opacity: 0; transform: translateY(5px); }}
            100% {{ opacity: 1; transform: translateY(0); }}
        }}
        .blink {{
            animation: blink 1s step-end infinite;
        }}
        @keyframes blink {{
            50% {{ opacity: 0; }}
        }}
        @media (max-width: 600px) {{
            .bubble {{
                max-width: 90%;
                font-size: 0.95rem;
            }}
        }}
    </style>
""", unsafe_allow_html=True)

# === Title ===
st.title("💬 AI-Assistant")

# === Intro Message ===
if not st.session_state.intro_done:
    intro_msg = "👋 Hey hey! I’m AI-Assistant — your chat buddy 🤖✨ Ask me anything, anytime!"
    placeholder = st.empty()
    typing_effect(intro_msg, placeholder, delay=0.02)
    st.session_state.chat_log.append(("Bot", intro_msg, get_time()))
    st.session_state.intro_done = True
    st.rerun()

# === Chat History Rendering ===
for sender, message, timestamp in st.session_state.chat_log:
    bubble_class = "user" if sender == "User" else "bot"
    st.markdown(f"<div class='bubble {bubble_class}'>{message}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='timestamp'>[{timestamp}] {sender}</div>", unsafe_allow_html=True)

# === User Input Handling ===
user_input = st.chat_input("Type your message...")

if user_input:
    timestamp = get_time()
    st.session_state.chat_log.append(("User", user_input, timestamp))

    with st.spinner("AI-Assistant is typing..."):
        prompt = build_prompt(st.session_state.chat_log)
        try:
            raw_reply = chat_session.send_message(prompt).text.strip()
        except Exception as e:
            raw_reply = "⚠️ Oops! Something went wrong. Try again later."

        sticker = load_sticker()
        reply = f"{raw_reply} {sticker}" if raw_reply else "🤖 Sorry, I didn’t get that."

        reply_placeholder = st.empty()
        typing_effect(reply, reply_placeholder, delay=0.02)
        st.session_state.chat_log.append(("Bot", reply, get_time()))

    st.rerun()
