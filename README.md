# 🧾 ReceiptSnap - AI Receipt & Expense Tracker / Bill Splitter

ReceiptSnap is an AI-powered receipt scanning, expense tracking, and bill-splitting Streamlit application. Built using Google Gemini 2.5 Flash Vision & Chat, it extracts itemized pricing from photos of receipts, calculates subtotal/tax/tip, splits bills across groups, and dispatches summary digests to Email (Gmail SMTP) or Telegram.

---

## 📁 Project Structure

```
receipt_snap/
├── app.py                  # Main Streamlit chat application & UI
├── prompts.py              # Gemini system prompts & message templates
├── mailer.py               # Gmail SMTP email sender module
├── telegram_bot.py         # Telegram bot message dispatcher module
├── requirements.txt        # Project dependencies
├── .gitignore              # Protects secrets from version control
├── README.md               # Setup & submission guide
└── .streamlit/
    └── secrets.toml.example # Template for secrets
```

---

## 🚀 Quick Setup & Running Locally

### 1. Create & Activate Virtual Environment
```bash
python -m venv venv

# macOS / Linux:
source venv/bin/activate

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Secrets
Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`:
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Open `.streamlit/secrets.toml` and fill in:
- `GEMINI_API_KEY`: Key from [Google AI Studio](https://aistudio.google.com)
- `GMAIL_ADDRESS`: Your Gmail email address
- `GMAIL_APP_PASSWORD`: 16-character App Password generated at [Google App Passwords](https://myaccount.google.com/apppasswords)

### 4. Run the Streamlit App
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌟 Key Features
- **Multimodal AI Scanning**: Upload receipt photos (JPG, PNG, WebP) or type expense items manually.
- **Automated Bill Splitting**: Adjust splitters and tip percentages directly from the sidebar.
- **Action Dispatcher**: Hit **"Send Summary"** to email a beautifully formatted HTML breakdown digest via Gmail SMTP or Telegram.
- **Session Memory**: Stateful conversation using `st.session_state.chat`.
