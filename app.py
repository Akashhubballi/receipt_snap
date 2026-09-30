import streamlit as st
import os
from google import genai
from google.genai import types
from prompts import SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE, SUMMARY_REQUEST_PROMPT
from mailer import send_email
from telegram_bot import send_telegram

MODEL_NAME = "gemini-3.8-flash"

st.set_page_config(page_title="ReceiptSnap - AI Bill Splitter", page_icon="🧾", layout="wide")

# Read Secrets safely from Streamlit secrets
# Read credentials from Render Environment Variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

@st.cache_resource
def get_gemini_client():
    if not GEMINI_API_KEY:
        st.error("Missing GEMINI_API_KEY in secrets.toml. Please add it to test Gemini AI.")
        st.stop()
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.markdown(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"], use_container_width=True)

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"

# Onboarding screen pattern
if "onboarded" not in st.session_state:
    st.title("🧾 ReceiptSnap")
    st.caption("Snap receipts. Track expenses. Send bill splits automatically.")
    
    with st.form("onboarding_form"):
        name = st.text_input("Your Name", placeholder="e.g. Alex")
        action_channel = st.radio("Choose Action Tool", ["Email (Gmail)", "Telegram Bot"])
        
        recipient = st.text_input(
            "Recipient Email / Telegram Chat ID",
            placeholder="you@gmail.com or 123456789",
            help="Where your bill summaries will be dispatched."
        )
        
        submitted = st.form_submit_button("Let's Go 🚀")
        
        if submitted:
            if not name.strip() or not recipient.strip():
                st.warning("Please fill in both your name and recipient contact.")
            else:
                st.session_state.name = name.strip()
                st.session_state.action_channel = action_channel
                st.session_state.recipient = recipient.strip()
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
                st.stop()

# Main Application Interface
header_col, button_col = st.columns([4, 2], vertical_alignment="center")

with header_col:
    st.title("🧾 ReceiptSnap")

with button_col:
    send_disabled = len(st.session_state.messages) <= 1
    action_label = "📤 Send Email Summary" if st.session_state.action_channel == "Email (Gmail)" else "📤 Send Telegram Digest"
    
    if st.button(action_label, disabled=send_disabled, use_container_width=True):
        with st.spinner("Generating expense breakdown..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            
            if st.session_state.action_channel == "Email (Gmail)":
                success, info = send_email(GMAIL_ADDRESS, GMAIL_APP_PASSWORD, st.session_state.recipient, st.session_state.name, summary)
            else:
                success, info = send_telegram(TELEGRAM_BOT_TOKEN, st.session_state.recipient, st.session_state.name, summary)
                
            if success:
                st.success(f"Dispatched successfully to {st.session_state.recipient}! 📲")
            else:
                st.error(f"Dispatch failed: {info}")

st.caption(f"Logged in as **{st.session_state.name}** | Channel: **{st.session_state.action_channel}** → `{st.session_state.recipient}`")

# Sidebar for Split Calculator controls
with st.sidebar:
    st.header("⚙️ Split Calculator Controls")
    num_people = st.number_input("Number of People Splitting", min_value=1, max_value=50, value=2)
    tip_percent = st.slider("Tip Percentage (%)", min_value=0, max_value=30, value=15)
    st.markdown("---")
    st.markdown("**Instructions:**")
    st.markdown("- Upload a photo of a receipt or type your item list below.")
    st.markdown(f"- Ask Gemini: *'Split this bill among {num_people} people with a {tip_percent}% tip.'*")

# Display message history
if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

# Chat Input with File Attachment support
user_input = st.chat_input(
    "Ask a question, type items, or attach a photo of a receipt...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        prompt_text = f"Extract all items, totals, subtotal, tax, and tip from this receipt. Split the total evenly among {num_people} people with a {tip_percent}% tip included."
        parts.append(prompt_text)

    with st.spinner("Analyzing receipt & calculating split..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)
