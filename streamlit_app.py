import streamlit as st
from openai import OpenAI
import google.genai as genai

# Show title and description.
st.title("Sam: Tu Guía Matemática Personal")
st.write(
    "Selecciona el proveedor de IA y proporciona la clave de API correspondiente para interactuar con Sam, tu tutora experta en matemáticas y física."
)

provider = st.radio(
    "Proveedor de IA",
    ["OpenAI", "Google AI Studio"],
    help="Selecciona la API que deseas usar para la generación de texto.",
)

openai_api_key = ""
google_api_key = ""
google_model = "gemma-4-31b-it"

system_instruction = (
    "Eres Sam una tutora experta y empática de matemáticas y física. Tu objetivo principal es "
    "desmitificar conceptos complejos, haciéndolos accesibles y comprensibles sin perder el "
    "rigor científico ni matemático. Adoptas un tono paciente, alentador y estructurado, "
    "guiando al usuario hacia la comprensión profunda en lugar de simplemente darle la "
    "respuesta final."
)

if provider == "OpenAI":
    openai_api_key = st.text_input("OpenAI API Key", type="password")
else:
    google_api_key = st.text_input("Google AI Studio API Key", type="password")
    google_model = st.text_input(
        "Modelo de Google AI Studio",
        value=google_model,
        help="Modelo Gemini usado por Google AI Studio, por ejemplo gemma-4-31b-it.",
    )

if not ((provider == "OpenAI" and openai_api_key) or (provider == "Google AI Studio" and google_api_key)):
    st.info("Please provide the API key for the selected provider.", icon="🗝️")
else:
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        role = "assistant" if message["role"] == "assistant" else message["role"]
        with st.chat_message(role):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if provider == "OpenAI":
            client = OpenAI(api_key=openai_api_key)
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)

        else:
            client = genai.Client(api_key=google_api_key)
            history = [
                {
                    "role": "user" if m["role"] == "user" else "model",
                    "parts": [{"text": m["content"]}],
                }
                for m in st.session_state.messages
            ]
            config = {
                "system_instruction": system_instruction,
                "temperature": 0.2,
            }
            chat = client.chats.create(model=google_model, history=history, config=config)
            assistant_text = ""
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                for chunk in chat.send_message_stream(prompt, config=config):
                    if chunk.text:
                        assistant_text += chunk.text
                        response_placeholder.markdown(assistant_text)
            response = assistant_text

        st.session_state.messages.append({"role": "assistant", "content": response})
