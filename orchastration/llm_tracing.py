from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, handoff
import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 Load API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# 🔗 External client for Gemini
external_client = AsyncOpenAI(
    api_key=GOOGLE_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# 🎯 Choose the LLM model
llm_model = OpenAIChatCompletionsModel(
    model="gemini-2.5-flash",
    openai_client=external_client,
)

# ------------------ TOOLS ------------------

@function_tool
def fetch_info(topic: str) -> str:
    """Fetch some basic info about a topic."""
    print(f"[Tool] Fetching info on {topic}...")
    return f"Info about {topic}: It is an important and trending topic."

# ------------------ SUB-AGENT ------------------

report_writer = Agent(
    name="ReportWriterAgent",
    instructions="You are great at writing short reports. Always take input and expand into a 3-sentence report.",
    model=llm_model,
)

# ------------------ MAIN AGENT ------------------

research_agent = Agent(
    name="ResearchAgent",
    instructions=(
        "You are a research assistant. "
        "If the user asks for info, use the fetch_info tool. "
        "If they ask for a report, hand off to the ReportWriterAgent."
    ),
    model=llm_model,
    tools=[fetch_info],
    handoffs=[handoff(report_writer)]
)

# ------------------ RUN ------------------

query = input("Enter your query: ")

result = Runner.run_sync(
    research_agent,
    input=query,
)

print("\n=== FINAL OUTPUT ===")
print(result.final_output)
