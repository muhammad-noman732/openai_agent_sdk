from agents import Agent ,Runner , AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig, ItemHelpers ,RunContextWrapper,  function_tool
from pydantic import BaseModel
from dataclasses import dataclass
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

# here if we do not provide the user info it will not give us weather .
# @function_tool
# def fetch_weather(user: str , location: str)-> str:
#     """
#        fetch weather for the given location

#        Args:
#        location: the location to fetch weather for  
#     """
#     print(user)
#     print(f"fetch weather for the given {location}")
#     return f"weather of the {location} is sunny"

# we use local context with that the context llm does not know . this will use only by the local 

@dataclass 
class UserInfo:  
    name: str
    uid: int
@function_tool
def fetch_news(user:RunContextWrapper[UserInfo] , location: str)-> str:
    """
       fetch news for the given location

       Args:
       location: the location to fetch news  for 
    """
    # this is user is now in the local context llm does not need this 
    print(user)
    print(f"username {user.context.name} " )
    print(f"fetch news for the given {location}")
    return f"news of {location} are good"

# instance of the class 
user_info = UserInfo(name="noman", uid=123)

agent = Agent[UserInfo](
    name="You are an expert of weather ",
    instructions = "call the tool , get the weather and return ",
    model= llm_model,
    tools=[ fetch_news]
)


query = input ("enter your query")

result = Runner.run_sync(
    agent,
    input=query,
    context= user_info
   )


print(result.final_output)


