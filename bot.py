import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
import time
import google.api_core.exceptions
from gtts import gTTS
import os
import playsound

# 🧠 Replace with your own API Key
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

# Use Gemini 1.5 Pro for listing
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

# 🧍 Vishal's bio
vishal_bio = """
You are speaking as Vishal Sanap, a full-stack developer from India who graduated in 2024,
specializing in frontend with React and Next.js. You're exploring Generative AI, like voice bots.
Keep responses conversational, friendly, and to-the-point.
"""

# 🎤 Listen to voice input (only on button press)
def listen_to_user(timeout=30, phrase_time_limit=40):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        with st.spinner("🎙️ Listening... (timeout: {}s, phrase limit: {}s)".format(timeout, phrase_time_limit)):
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            recognizer.adjust_for_ambient_noise(source)
    try:
        query = recognizer.recognize_google(audio)
        st.success(f"🗣️ You said: {query}")
        return query
    except Exception as e:
        st.error("❌ Could not understand audio.")
        return ""

# 🧠 Ask Gemini
@st.cache_data(show_spinner=False)
def ask_chatgpt(user_input):
    model = genai.GenerativeModel("models/gemini-1.5-flash")
    full_prompt = vishal_bio + "\n\nUser asked: " + user_input

    for _ in range(3):
        try:
            response = model.generate_content(full_prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted:
            time.sleep(60)

    return "❌ Rate limit exceeded. Please try again later."

# 🔊 Speak output using gTTS
def speak_response(text):
    tts = gTTS(text=text, lang='en', slow=False)
    tts.save("response.mp3")
    playsound.playsound("response.mp3")
    os.remove("response.mp3")

# Streamlit UI
st.set_page_config(page_title="Vishal's Voice Bot", page_icon="🧠")
st.title("🧠 Vishal's Voice Bot")
st.markdown("Speak to Vishal's assistant. Ask anything!")

if st.button("🎙️ Start Speaking"):
    user_input = listen_to_user()

    if user_input:
        reply = ask_chatgpt(user_input)
        st.markdown(f"**🤖 Vishal:** {reply}")

        speak_response(reply)

        if st.button("✅ Ask Something Else"):
            st.experimental_rerun()
