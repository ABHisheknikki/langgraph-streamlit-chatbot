# 🤖 LangGraph & Streamlit Conversational Chatbot

A fully-featured conversational AI chatbot built with a **LangGraph** backend for robust, stateful logic and a **Streamlit** frontend for a real-time, interactive user interface.

This project demonstrates how to build a stateful chatbot that can use tools, stream responses, and manage persistent, multi-threaded conversations with automatic title generation.

## 🎥 Demo

<video width="100%" autoplay loop muted playsinline>
  <source src="chatbot_demo.mp4" type="video/mp4">
</video>

*(This shows the chatbot streaming responses, using tools (calculator, search), and saving conversation history in the sidebar)*

## ✨ Key Features

* **Stateful Conversations:** Uses LangGraph's `SqliteSaver` to persist conversation state, allowing users to return to previous chats.
* **Tool Usage:** The agent can dynamically decide to use tools like:
    * `DuckDuckGoSearch` for live web searches.
    * `Calculator` for math operations.
    * `Alpha Vantage` for real-time stock prices.
* **Streaming Responses:** Uses Streamlit's `st.write_stream` for a smooth, token-by-token response, just like ChatGPT.
* **Multi-Thread Management:** Users can create new chats or select previous conversations from the sidebar.
* **Automatic Title Generation:** The first user message is automatically summarized by an LLM call to create a short, descriptive title for the conversation.
* **Clean UI:** Tool-call messages are hidden from the final chat history for a cleaner user experience.

## 🛠️ Tech Stack

* **Backend:** LangGraph, LangChain, OpenAI
* **Frontend:** Streamlit
* **Database:** SQLite (for graph checkpointing & chat titles)
* **Tools:** DuckDuckGo Search, Alpha Vantage

## 🚀 Getting Started

### Prerequisites

* Python 3.9+
* An OpenAI API Key
* An Alpha Vantage API Key

### 1. Clone the Repository

```bash
git clone [https://github.com/YourUsername/langgraph-streamlit-chatbot.git](https://github.com/YourUsername/langgraph-streamlit-chatbot.git)
cd langgraph-streamlit-chatbot