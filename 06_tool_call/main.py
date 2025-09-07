from agents import Agent ,Runner , AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ItemHelpers ,  function_tool
from pydantic import BaseModel
from dotenv import load_dotenv
import os


load_dotenv()

# Load Gemini API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

externel_client : AsyncOpenAI= AsyncOpenAI(
     api_key= GOOGLE_API_KEY,
     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
) 


llm_model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
       model="gemini-2.5-flash",
      openai_client= externel_client
)

@function_tool
def fetch_weather(location: str)-> str:
    """
       fetch weather for the given location

       Args:
       location: the location to fetch weather for 
    """
    print(f"fetch weather for the given {location}")
    return f"weather of the {location} is sunny"



@function_tool
def fetch_news(location: str)-> str:
    """
       fetch news for the given location

       Args:
       location: the location to fetch news  for 
    """
    print(f"fetch news for the given {location}")
    return f"news of {location} are good"



agent = Agent(
    name="You are an expert of weather ",
    instructions = "call the tool , get the weather and return ",
    model= llm_model,
    tools=[fetch_weather, fetch_news]
)


query = input ("enter your query")

result = Runner.run_sync(
    agent,
    input=query,
   )


print(result.final_output)


