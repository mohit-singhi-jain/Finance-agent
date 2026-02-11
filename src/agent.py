import os
import sys
import requests
from typing import Annotated
from typing_extensions import TypedDict

# LangChain / LangGraph Imports
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import ToolNode, tools_condition

# --- 1. CONFIGURATION & SETUP ---
# Load environment variables from .env file
load_dotenv()

# Verify API Keys
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
TAVILY_KEY = os.getenv("TAVILY_API_KEY")
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

if not all([GOOGLE_KEY, TAVILY_KEY, ALPHA_KEY]):
    print("❌ Error: Missing API Keys in .env file.")
    print("Please ensure GOOGLE_API_KEY, TAVILY_API_KEY, and ALPHA_VANTAGE_KEY are set.")
    sys.exit(1)


# --- 2. DEFINE TOOLS ---

@tool
def get_stock_price(symbol: str):
    """
    Retrieves the latest stock price.
    IMPORTANT: For Indian stocks (NSE/BSE), try appending '.BSE' or '.TRV' to the symbol.
    Example: 'TATASTEEL.BSE' or 'RELIANCE.BSE'.
    """
    base_url = "https://www.alphavantage.co/query"
    params = {"function": "GLOBAL_QUOTE", "symbol": symbol, "apikey": ALPHA_KEY}
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        price = data.get("Global Quote", {}).get("05. price")
        if price:
            return f"The current price of {symbol} is ${float(price):.2f}"
        return f"Error: No price found for {symbol}. Try adding .BSE or .TRV suffix for Indian stocks."
    except Exception as e:
        return f"API Error: {e}"


@tool
def get_rsi(symbol: str):
    """Retrieves RSI (Relative Strength Index). For Indian stocks, append .BSE or .TRV."""
    base_url = "https://www.alphavantage.co/query"
    params = {"function": "RSI", "symbol": symbol, "interval": "daily", "time_period": "14", "series_type": "close",
              "apikey": ALPHA_KEY}
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
        rsi_data = data.get("Technical Analysis: RSI")
        if rsi_data:
            latest_date = list(rsi_data.keys())[0]
            rsi_val = rsi_data[latest_date]["RSI"]
            return f"The current RSI for {symbol} is {float(rsi_val):.2f} (as of {latest_date})"
        return f"Error: No RSI data found for {symbol}."
    except Exception as e:
        return f"API Error: {e}"


@tool
def web_search(query: str):
    """
    Use this for ANY news, market trends, or if stock price tool fails.
    Essential for 'Latest news', 'Why is market moving', or specific Indian market queries.
    """
    print(f"   [DEBUG: Searching web for '{query}']")

    # Direct API Call to Tavily
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": TAVILY_KEY,
        "query": query,
        "search_depth": "basic",
        "max_results": 3
    }

    try:
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            results = response.json().get("results", [])
            context = "\n".join([f"- {r['title']}: {r['content']}" for r in results])
            return context if context else "No relevant news found."
        else:
            return f"Search Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Search Connection Error: {e}"


# --- 3. INITIALIZE AI MODEL ---
tools = [get_stock_price, get_rsi, web_search]

try:
    # Using the generic alias "gemini-flash-latest" to bypass version issues
    llm = init_chat_model("gemini-flash-latest", model_provider="google_genai")
    llm_with_tools = llm.bind_tools(tools)
except Exception as e:
    print(f"❌ CRITICAL MODEL ERROR: {e}")
    sys.exit(1)


# --- 4. DEFINE GRAPH WORKFLOW ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


SYSTEM_PROMPT = """You are a Financial Analyst AI. 
1. For Indian Stocks: Always try appending '.BSE' to the ticker first (e.g., TATASTEEL -> TATASTEEL.BSE) when using price tools.
2. If Price/RSI tools fail, IMMEDIATELY use 'web_search' to find the data.
3. For News: Always use 'web_search'.
4. Keep answers clean, concise, and professional. Do not show internal metadata."""


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


builder = StateGraph(State)
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools=tools))
builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")
graph = builder.compile()


# --- 5. HELPER: CLEAN OUTPUT ---
def clean_response(raw_content):
    if isinstance(raw_content, list):
        text_parts = []
        for item in raw_content:
            if isinstance(item, dict) and item.get('type') == 'text':
                text_parts.append(item.get('text', ''))
        return "".join(text_parts)
    return str(raw_content)


# --- 6. MAIN LOOP ---
if __name__ == "__main__":
    print("--- 🚀 Financial AI Agent Ready ---")
    print("(Type 'exit', 'quit', or 'q' to stop)")

    memory = [SystemMessage(content=SYSTEM_PROMPT)]

    while True:
        try:
            user_input = input("\nYou: ")

            if user_input.lower() in ["quit", "exit", "q"]:
                print("Thank you for using the Financial Agent!")
                break

            memory.append(HumanMessage(content=user_input))
            events = graph.invoke({"messages": memory})

            last_message = events["messages"][-1]
            final_text = clean_response(last_message.content)

            print(f"Agent: {final_text}")
            memory.append(AIMessage(content=final_text))

        except KeyboardInterrupt:
            print("\nThank you for using the Financial Agent!")
            break
        except Exception as e:
            print(f"⚠️ An error occurred: {e}")