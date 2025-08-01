import streamlit as st
from langchain_openai import ChatOpenAI
import os

# ========== Setup ==========

st.set_page_config(page_title="🎮 World's Fastest Game Generator", layout="centered")
st.sidebar.image("https://github.com/pratik-gond/temp_files/blob/main/image-removebg-preview.png?raw=true", use_container_width=True)
st.sidebar.header("⚙️ Configuration")
model_name = st.sidebar.selectbox("Model", ["qwen-3-235b-a22b-instruct-2507"], index=0)

# Get API key from secrets
try:
    api_key = st.secrets["CEREBRAS_API_KEY"]
except KeyError:
    st.error("⚠️ Cerebras API Key not found in secrets. Please add CEREBRAS_API_KEY to your .streamlit/secrets.toml file.")
    api_key = None

st.sidebar.divider()
    
# About section
st.sidebar.markdown("### About Qwen Model")
st.sidebar.markdown("Powered by Qwen model from Cerebras, delivering lightning-fast AI responses at **1500 tokens per second**. Perfect for rapid game generation and real-time code creation.")
st.sidebar.divider()
st.sidebar.markdown("**Want to learn how to build this?**")
st.sidebar.markdown("Sign up for [Generative AI course by Build Fast with AI](https://buildfastwithai.com/genai-course)")   

@st.cache_resource(show_spinner=False)
def get_llm(api_key, model_name):
    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base="https://api.cerebras.ai/v1"
    )

if "messages" not in st.session_state:
    st.session_state.messages = []  # memory for chat
if "game_code" not in st.session_state:
    st.session_state.game_code = ""

st.title("🎮 World's Fastest Game Generator")
st.markdown('*Built by [Build Fast with AI](https://buildfastwithai.com/genai-course) - Learn to build AI apps like this!*', unsafe_allow_html=True)

if api_key:
    # ========== Chat UI ==========
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Describe your game or suggest an improvement...")

    if user_input:
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Check if it's the first prompt (game creation) or improvement
        is_game_creation = "<html" not in st.session_state.game_code.lower()

        # ========== Prompt Engineering ==========
        if is_game_creation:
            full_prompt = f"""
    You're an expert HTML5 game developer.

    Generate a visually appealing and playable HTML5 game based on the following idea.
    Requirements:
    - Canvas-based game
    - Retry button after losing
    - Entire game in one standalone HTML file
    - NO markdown (no triple backticks)

    Game idea: {user_input}
    """
        else:
            full_prompt = f"""
    Improve the following HTML5 game based on the user request.

    Request: "{user_input}"

    Only return a full, standalone HTML file (no explanations or markdown).

    Game code:
    {st.session_state.game_code}
    """

        with st.chat_message("assistant"):
            with st.spinner("🧠 Thinking... Generating your game..."):
                try:
                    llm = get_llm(api_key, model_name)
                    response = llm.invoke(full_prompt)
                    # response = client.chat.completions.create(
                    #     model="gpt-4o",
                    #     messages=[{"role": "user", "content": full_prompt}],
                    #     temperature=0.7,
                    # )
                    game_html = response.content.strip()

                    if "<html" not in game_html.lower():
                        st.error("❌ Invalid HTML received. Try rephrasing your request.")
                    else:
                        st.session_state.game_code = game_html
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "✅ Game updated! See below 👇",
                        })
                        st.rerun()

                except Exception as e:
                    st.error(f"Cerebras API Error: {str(e)}")

    # ========== Show Game ==========
    if st.session_state.game_code:
        st.divider()
        st.subheader("🎮 Your Game")
        st.components.v1.html(st.session_state.game_code, height=600, scrolling=False)

        st.download_button(
            label="⬇️ Download Game HTML",
            data=st.session_state.game_code,
            file_name="ai_game.html",
            mime="text/html"
        )

else:
    st.error("Please add your Cerebras API Key to .streamlit/secrets.toml to start generating games.")