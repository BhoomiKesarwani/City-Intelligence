
from dotenv import load_dotenv
load_dotenv()

import os
import requests
import streamlit as st

from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from tavily import TavilyClient


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="City Agent | AI Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: #0b1020;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background: #11182b;
        border-right: 1px solid #26324b;
    }

    .hero {
        padding: 25px 28px;
        border: 1px solid #293653;
        border-radius: 18px;
        background: linear-gradient(120deg, #17243d, #11182b);
        margin-bottom: 24px;
    }

    .hero h1 {
        font-size: 34px;
        margin-bottom: 8px;
        color: #f8fafc;
    }

    .hero p {
        color: #aab8d0;
        font-size: 15px;
        margin-bottom: 0;
    }

    .metric-card {
        background: #131d32;
        border: 1px solid #293653;
        border-radius: 14px;
        padding: 18px;
        min-height: 110px;
    }

    .metric-label {
        color: #9caec8;
        font-size: 13px;
    }

    .metric-value {
        color: #f8fafc;
        font-size: 22px;
        font-weight: 700;
        margin-top: 8px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 650;
        margin: 25px 0 12px 0;
        color: #f1f5f9;
    }

    div[data-testid="stChatMessage"] {
        border: 1px solid #293653;
        border-radius: 14px;
        background: #11182b;
        padding: 12px;
    }

    div[data-testid="stChatInput"] {
        border-color: #344563;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #344563;
        background: #17243d;
        color: #e5e7eb;
        min-height: 42px;
    }

    .stButton > button:hover {
        border-color: #60a5fa;
        color: white;
    }

    .small-note {
        color: #91a1bb;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# WEATHER TOOL
# --------------------------------------------------

@tool
def get_weather(city: str) -> str:
    """Get current weather for a city in India."""

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "Error: OPENWEATHER_API_KEY is missing from .env."

    try:
        geo_response = requests.get(
            "https://api.openweathermap.org/geo/1.0/direct",
            params={
                "q": f"{city.strip()},IN",
                "limit": 1,
                "appid": api_key,
            },
            timeout=15,
        )

        geo_data = geo_response.json()

        if not geo_response.ok:
            return (
                f"Geocoding error ({geo_response.status_code}): "
                f"{geo_data.get('message', geo_data)}"
            )

        if not geo_data:
            return f"City '{city}' was not found. Check the spelling."

        lat = geo_data[0]["lat"]
        lon = geo_data[0]["lon"]

        weather_response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={
                "lat": lat,
                "lon": lon,
                "appid": api_key,
                "units": "metric",
            },
            timeout=15,
        )

        weather = weather_response.json()

        if not weather_response.ok:
            return (
                f"Weather error ({weather_response.status_code}): "
                f"{weather.get('message', weather)}"
            )

        return (
            f"City: {weather['name']}\n"
            f"Temperature: {weather['main']['temp']} °C\n"
            f"Feels like: {weather['main']['feels_like']} °C\n"
            f"Humidity: {weather['main']['humidity']}%\n"
            f"Condition: {weather['weather'][0]['description']}\n"
            f"Wind speed: {weather['wind'].get('speed', 'N/A')} m/s"
        )

    except requests.RequestException as exc:
        return f"Weather network error: {exc}"

    except (KeyError, IndexError, ValueError, TypeError):
        return "Error: Unexpected response from OpenWeatherMap."


# --------------------------------------------------
# TAVILY NEWS TOOL
# --------------------------------------------------

@tool
def get_news(city: str) -> str:
    """Find the three latest news results about a city."""

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Error: TAVILY_API_KEY is missing from .env."

    try:
        client = TavilyClient(api_key=api_key)

        response = client.search(
            query=f"Latest news in {city}",
            topic="news",
            time_range="week",
            max_results=3,
            search_depth="basic",
        )

        results = response.get("results", [])

        if not results:
            return f"No recent news results found for {city}."

        news_items = []

        for i, item in enumerate(results, start=1):
            title = item.get("title", "Untitled")
            content = item.get("content", "No summary available")
            url = item.get("url", "")
            published = item.get("published_date", "Date unavailable")

            news_items.append(
                f"{i}. {title}\n"
                f"Summary: {content}\n"
                f"Published: {published}\n"
                f"Source: {url}"
            )

        return "\n\n".join(news_items)

    except Exception as exc:
        return f"News search failed: {exc}"


# --------------------------------------------------
# INITIALIZE THE AI AGENT ONCE
# --------------------------------------------------

@st.cache_resource
def build_agent():
    llm = ChatOllama(
        model="gpt-oss:120b",
        base_url="https://ollama.com",
    )

    return create_agent(
        model=llm,
        tools=[get_weather, get_news],
        system_prompt="""
        You are City Agent, a helpful assistant for Indian cities.

        You can:
        1. Retrieve current weather using get_weather.
        2. Find recent city news using get_news.
        3. Answer general questions about Indian cities.

        Use the tools whenever the user requests current weather
        or recent news. Never invent live weather or news results.
        Clearly distinguish retrieved facts from general knowledge.
        Format answers in a readable way using headings and bullets.
        If a tool returns an error, explain it honestly.
        """,
    )


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌍 City Agent")
    st.caption("Your AI-powered city companion")

    st.divider()

    st.markdown("### Connected services")

    st.markdown(
        f"{'🟢' if os.getenv('OPENWEATHER_API_KEY') else '🔴'} "
        "**OpenWeatherMap**"
    )
    st.markdown(
        f"{'🟢' if os.getenv('TAVILY_API_KEY') else '🔴'} "
        "**Tavily News Search**"
    )
    st.markdown("🔵 **Ollama Cloud LLM**")
    st.caption("Cloud access must be configured correctly.")

    st.divider()

    st.markdown("### What can I do?")
    st.markdown(
        "- 🌦️ Current weather\n"
        "- 📰 Recent city news\n"
        "- 🏙️ City information\n"
        "- 💬 Follow-up questions"
    )

    st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown(
        '<p class="small-note">Built with Streamlit, LangChain, '
        'Tavily and Ollama Cloud.</p>',
        unsafe_allow_html=True,
    )


# --------------------------------------------------
# MAIN DASHBOARD HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🌍 City Intelligence Dashboard</h1>
    <p>
        Ask about weather, discover recent city news, and explore
        Indian cities with your AI assistant.
    </p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# DASHBOARD METRICS
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Assistant</div>
        <div class="metric-value">City Agent</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tools available</div>
        <div class="metric-value">2 Active Tools</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Messages this session</div>
        <div class="metric-value">{len(st.session_state.messages)}</div>
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# TABS
# --------------------------------------------------

chat_tab, tools_tab, about_tab = st.tabs(
    ["💬 AI Chat", "🧰 Tools", "ℹ️ About"]
)


# --------------------------------------------------
# CHAT TAB
# --------------------------------------------------

with chat_tab:

    st.markdown(
        '<div class="section-title">Chat with your assistant</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Ask a question below or select a sample prompt to get started."
    )

    prompt_cols = st.columns(3)

    sample_prompts = [
        "Weather in Prayagraj",
        "Latest news about Delhi",
        "Weather in Mumbai",
    ]

    for i, prompt in enumerate(sample_prompts):
        with prompt_cols[i]:
            if st.button(prompt, key=f"sample_{i}", use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

    # Display previous conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process either a selected sample prompt or typed input
    typed_prompt = st.chat_input(
        "Ask about a city's weather, news, or local information..."
    )

    user_prompt = typed_prompt

    if st.session_state.pending_prompt:
        user_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if user_prompt:
        st.session_state.messages.append(
            {"role": "user", "content": user_prompt}
        )

        with st.chat_message("user"):
            st.markdown(user_prompt)

        with st.chat_message("assistant"):
            with st.spinner("City Agent is thinking..."):
                try:
                    agent = build_agent()

                    # Include previous user/assistant messages for context.
                    result = agent.invoke({
                        "messages": [
                            {
                                "role": msg["role"],
                                "content": msg["content"],
                            }
                            for msg in st.session_state.messages
                        ]
                    })

                    answer = result["messages"][-1].content

                    if isinstance(answer, list):
                        answer = "\n".join(
                            str(part.get("text", part))
                            if isinstance(part, dict)
                            else str(part)
                            for part in answer
                        )

                    if not answer:
                        answer = "I couldn't generate a response. Please try again."

                except Exception as exc:
                    answer = (
                        "I couldn't connect to the AI agent.\n\n"
                        "Check your Ollama Cloud configuration, model "
                        "availability, API credentials, and installed "
                        "package versions.\n\n"
                        f"**Technical details:** `{exc}`"
                    )

                st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

        st.rerun()


# --------------------------------------------------
# TOOLS TAB
# --------------------------------------------------

with tools_tab:
    st.markdown("## Available tools")

    with st.container(border=True):
        st.markdown("### 🌦️ Weather Intelligence")
        st.write(
            "Retrieves current temperature, feels-like temperature, "
            "humidity, weather conditions and wind speed for Indian cities."
        )
        st.caption("Powered by OpenWeatherMap")

    with st.container(border=True):
        st.markdown("### 📰 City News Search")
        st.write(
            "Searches for up to three recent news results about a city, "
            "including summaries, publication dates when available, "
            "and source links."
        )
        st.caption("Powered by Tavily")

    with st.container(border=True):
        st.markdown("### 🧠 AI Agent")
        st.write(
            "LangChain connects the language model to the weather and "
            "news tools. The agent decides when a tool is needed."
        )
        st.caption("Model: gpt-oss:120b on Ollama Cloud")


# --------------------------------------------------
# ABOUT TAB
# --------------------------------------------------

with about_tab:
    st.markdown("## About this project")

    st.write(
        "City Agent is a tool-using AI assistant designed to answer "
        "questions about Indian cities. It combines a language model "
        "with external weather and news services."
    )

    st.markdown("### Technology stack")
    st.markdown(
        "- **Frontend:** Streamlit\n"
        "- **Agent framework:** LangChain\n"
        "- **Language model:** Ollama Cloud — `gpt-oss:120b`\n"
        "- **Weather data:** OpenWeatherMap\n"
        "- **News retrieval:** Tavily Search\n"
        "- **Configuration:** python-dotenv"
    )

    st.info(
        "Weather and news require valid API credentials and an internet "
        "connection. Results depend on the external services."
    )
