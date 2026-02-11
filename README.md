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