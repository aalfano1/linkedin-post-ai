import streamlit as st
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --------------------------
# CONFIGURATION
# --------------------------

st.set_page_config(page_title="AI LinkedIn Post Generator", layout="centered")
st.title("🤖 AI LinkedIn Post Generator")

# 🔐 Enter your OpenAI API key
openai_api_key = st.text_input("Enter your OpenAI API Key:", type="password")

# Upload your Google service account JSON file
creds_file = st.file_uploader("Upload your Google Service Account JSON", type=["json"])

# --------------------------
# GENERATE LINKEDIN POST
# --------------------------

def generate_linkedin_post(topic, tone, hashtags, emojis):
    style_instructions = f"Use a {tone} tone. Start with a strong hook. Write in first person."
    if hashtags:
        style_instructions += " Add 2–4 relevant professional hashtags at the end."
    if emojis:
        style_instructions += " Include 1–2 emojis if appropriate to emphasize key points."

    prompt = f"""
    Write a LinkedIn post about: "{topic}".
    {style_instructions}
    Keep it concise (1–2 paragraphs max).
    """

    try:
        openai.api_key = openai_api_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"⚠️ Error: {e}"

# --------------------------
# GOOGLE SHEETS SETUP
# --------------------------

def save_post_to_sheet(topic, post, creds_file):
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        client = gspread.authorize(creds)

        sheet = client.open("AI LinkedIn Posts").sheet1
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, topic, post])
        return "✅ Post saved to Google Sheet!"
    except Exception as e:
        return f"⚠️ Error saving to Google Sheet: {e}"

# --------------------------
# USER INPUT FORM
# --------------------------

with st.form("post_form"):
    topic = st.text_area("Enter your LinkedIn post topic:", height=100)
    tone = st.selectbox("Choose the tone for the post:", ["professional", "friendly", "inspirational", "confident", "bold"])
    add_hashtags = st.checkbox("Include hashtags", value=True)
    add_emojis = st.checkbox("Include emojis", value=False)
    submit = st.form_submit_button("Generate Post")

# --------------------------
# MAIN APP LOGIC
# --------------------------

if submit:
    if not openai_api_key or not creds_file or not topic:
        st.warning("⚠️ Please complete all required fields above.")
    else:
        with open("temp_creds.json", "wb") as f:
            f.write(creds_file.read())
        
        post = generate_linkedin_post(topic, tone, add_hashtags, add_emojis)
        st.markdown("### 📝 Generated Post:")
        st.code(post)

        result = save_post_to_sheet(topic, post, "temp_creds.json")
        st.success(result)
