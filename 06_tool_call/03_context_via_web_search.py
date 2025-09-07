from tavily import TavilyClient
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool
import os
from dotenv import load_dotenv

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

# Keys from your .env file
gemini_api_key = os.getenv("GOOGLE_API_KEY")   # Gemini API key
tavily_api_key = os.getenv("TAVILY_API_KEY")  # Tavily API key

# Gemini client
gemini_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Tavily client
tavily_client = TavilyClient(api_key=tavily_api_key)


# ------------------------------
# Define Tavily search as a tool
# ------------------------------
@function_tool
def web_search(query: str, max_results: int = 5) -> list:
    """
    Tool to perform a web search using Tavily API.
    
    Args:
        query (str): The search query.
        max_results (int): Number of results to retrieve.

    Returns:
        list: A list of search result dictionaries.
    """
    print(f"🔍 Searching web for: {query}")
    results = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results
    )
    return results.get("results", [])



agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant. Use the web_search tool if needed.",
    model=OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=gemini_client
    ),
    tools=[web_search],
)




query = input("Enter your query: ")

result = Runner.run_sync(
        agent,
        query,
    )

print("\n================= FINAL ANSWER =================")
print(result.final_output)
