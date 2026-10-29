# 🌍 City Intelligence Dashboard

An AI-powered city assistant built with **Streamlit, LangChain, Ollama Cloud, OpenWeatherMap, and Tavily** to provide current weather information and recent city news through an interactive chat interface.

🚀 Live Demo:[ Open City Intelligence Dashboard](https://city-intelligence-cvqh8hqllhm4g2a5jar8yh.streamlit.app/)

An AI-powered dashboard for city weather, latest news, and local information, built using Streamlit, LangChain, and Ollama Cloud.

## ✨ Features

- 🌦️ Current weather, temperature, humidity, and wind speed.
- 📰 Recent city news with summaries and source links.
- 🤖 AI agent with automatic tool selection.
- 💬 Interactive chat with session-based conversation history.
- 🎨 Modern dark-themed Streamlit dashboard.

## 🛠️ Tech Stack

- Python
- Streamlit
- LangChain
- Ollama Cloud (`gpt-oss:120b`)
- OpenWeatherMap API
- Tavily Search API

## 📁 Project Structure

```text
City-Intelligence-Dashboard/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

## ⚙️ Installation

**1. Clone the repository**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
```

**2. Create and activate a virtual environment**

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure API keys**

Create a `.env` file in the project root:

```env
OPENWEATHER_API_KEY=your_openweathermap_api_key
TAVILY_API_KEY=your_tavily_api_key
OLLAMA_API_KEY=your_ollama_cloud_api_key
```

Configure Ollama Cloud authentication in your `ChatOllama` client as required by your installed version.

**5. Run the application**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

## 🔑 API Resources

- OpenWeatherMap: https://openweathermap.org/api
- Tavily: https://tavily.com/
- Ollama Cloud: https://ollama.com/

## 🔒 Security

- Never upload `.env` or API keys to GitHub.
- Add `.env` to `.gitignore`.
- Configure secrets securely when deploying.

## 🚀 Deployment

Deploy using [Streamlit Community Cloud](https://share.streamlit.io/). Connect your GitHub repository, select `app.py`, configure your secrets, and deploy.

## 👩‍💻 Author

**Bhoomi Kesarwani**  
GitHub: https://github.com/BhoomiKesarwani

---

⭐ If you find this project useful, consider starring the repository.
