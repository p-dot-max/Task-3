import os
import getpass
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from tools.weather_tool import get_weather
from tools.doc_tool import get_doc_tool
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_agent

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if "GROQ_API_KEY" not in os.environ:
    os.environ["GROQ_API_KEY"] = getpass.getpass("Enter you groq API key: ")


def initialize():

    tools = [get_weather, get_doc_tool()]

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        max_tokens=None,
        reasoning_format="parsed",
        timeout=None,
        max_retries=2,
        api_key=api_key
    )

    prompt = (
        "You are an assistant with access to two tools: "
        "1. Technical Knowledge Base (VectorDB) for AI and RAG questions, "
        "History and about Archimedes. "
        "2. Weather Lookup for city-specific weather. "
        "Always use those tools when relevant. Answer general questions normally."
        "If the question is general, answer normally."
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=prompt
    )

    return agent


def response(user_query: str):
    executor = initialize()
    result = executor.invoke({"messages": [{"role": "user", "content": user_query}]})
    
    messages = result["messages"]
    final_message = messages[-1].content if messages else ""
    
    return {
        "output": final_message,
        "intermediate_steps": []
    }


if __name__ == "__main__":
    pass