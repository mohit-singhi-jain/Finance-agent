# 💰 Finance Agent

**A comprehensive AI-powered financial agent designed to bridge the gap between personal finance management and real-time stock market intelligence.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![Focus](https://img.shields.io/badge/Focus-Finance%20%26%20Data-orange)

## 📖 Overview
The **Finance agent** is a conversational agent built with Python that helps users make informed financial decisions. Unlike standard expense trackers, this agent can actively search the web for live market data, analyze financial news, and provide technical analysis (like support & resistance levels) alongside personal budgeting advice.

## ✨ Key Features
* **📉 Smart Budgeting:** Creates personalized budget plans and tracks expenses.
* **📰 Real-Time Market Intelligence:** Fetches the latest news and sentiment for specific indices (e.g., Nifty 50) and stocks.
* **📊 Technical Analysis:** Identifies key market drivers, support/resistance zones, and FII/DII trends.
* **🔍 Web Search Capability:** Uses live web search to find the most up-to-date financial information, ensuring data is never stale.

## 🚀 Sample Output
*Here is an example of the agent analyzing the Nifty 50 index:*

> **User:** latest news on Nifty 50
>
> **Agent:** The Nifty 50 has recently shown significant volatility, influenced by a mix of domestic earnings reports and global macroeconomic factors.
>
> **### Market Performance & Key Levels**
> * **Current Trend:** Under pressure due to sustained Foreign Institutional Investor (FII) selling.
> * **Support Levels:** Immediate support seen around **23,800 – 24,000**.
> * **Resistance Levels:** Key hurdles at **24,450** and **24,700**.
>
> **### Key Drivers**
> 1.  **Q3 Earnings Season:** Mixed results from heavyweights like Reliance and HDFC Bank.
> 2.  **Global Cues:** Investors monitoring US Fed commentary and geopolitical tensions.

## 🛠️ Tech Stack
* **Language:** Python
* **AI & Agents:** [Langgraph / LangChain / GeminiAI]
* **API's used:** [Alpha Vantage API, Tavily API, Google API]

## ⚙️ Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone (https://github.com/mohit-singhi-jain/Finance-agent.git)
    cd Finance-agent
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file and add your API keys:
    ```bash
    GOOGLE_API_KEY="your_key_here"
    TAVILY_API_KEY="your_key_here"
    ALPHA_VANTAGE_KEY="your_key_here"
    ```

4.  **Run the agent:**
    ```bash
    python src/agent.py
    ```

## 🤝 Contribution
Feel free to fork this repository and submit pull requests. Suggestions for adding new financial data sources are welcome!

---
*Created by Mohit Singhi Jain*

## 🏗️ Architecture

```mermaid
graph TD
    User(User Input) -->|Query| Agent[Financial Agent & LLM]
    
    subgraph "Reasoning Engine (LangGraph)"
        Agent -->|Decide Tool| Router{Router}
        Router -->|Stock Price?| Tool1[Alpha Vantage API]
        Router -->|RSI?| Tool2[Technical Analysis]
        Router -->|News/Context?| Tool3[Tavily Search API]
        
        Tool1 -->|Data| Context[Context Window]
        Tool2 -->|Data| Context
        Tool3 -->|News| Context
    end
    
    Context -->|Synthesize| Agent
    Agent -->|Final Answer| User
