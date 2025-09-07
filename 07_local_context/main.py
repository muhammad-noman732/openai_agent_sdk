from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool , RunContextWrapper
from dotenv import load_dotenv
from openai.types.responses.tool import WebSearchToolFilters
import os

load_dotenv()

# Load Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# External Gemini client
externel_client: AsyncOpenAI = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# LLM model wrapper
llm_model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=externel_client,
)

# Tools
@function_tool
def fetch_weather(location: str) -> str:
    """Fetch weather for the given location."""
    print(f"fetch weather for the given {location}")
    return f"weather of the {location} is sunny"

@function_tool
def fetch_news(location: str) -> str:
    """Fetch news for the given location."""
    print(f"fetch news for the given {location}")
    return f"news of {location} are good"

# Agent
agent = Agent(
    name="WeatherAgent",
    instructions="You are an expert of weather. Call the tool, get the data, and return.",
    model=llm_model,
    tools=[fetch_weather, fetch_news],
)

# Run agent
query = input("Enter your query: ")
result = Runner.run_sync(agent, input=query)
print(result.final_output)
