import json
import os
from dotenv import load_dotenv
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
from langchain_community.tools.json.tool import JsonSpec
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from typing import List 
from pprint import pprint
from langchain.output_parsers import PydanticOutputParser



load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class Finalres(BaseModel):
    modules: List[str]
 
    
parser = PydanticOutputParser(pydantic_object=Finalres)



# Load your JSON data
with open("aws/all_modules.json") as f:
    data = json.load(f)
with open("aws/aws_modules_params.json") as f:
    data_params = json.load(f)


# Convert list of modules to a dict with name as key
data_dict = {entry["name"]: entry for entry in data}
# Setup the spec and toolkit
json_spec = JsonSpec(dict_=data_dict, max_value_length=4000)
json_toolkit = JsonToolkit(spec=json_spec)

# json_spec_params=JsonSpec(dict_=data_params, max_value_length=4000)
# json_toolkit_params=JsonToolkit(spec=json_spec_params)
# Define approximate token counter (4 chars/token is a rough average)
def count_tokens_approx(text):
    return int(len(text) / 4)

# Create LLM and agent
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY
)

json_agent_executor = create_json_agent(
    llm=llm, toolkit=json_toolkit, verbose=True, handle_parsing_errors=True
)


# Run the agent and count tokens
# Step 1: Add JSON output format instruction to the prompt
question = parser.get_format_instructions() + "\n" + "What is the module used for Configure AWS Virtual Private Clouds?"

# Step 2: Invoke agent
response = json_agent_executor.invoke({"input": question})

# Step 3: Parse output as Pydantic model
parsed_output = parser.parse(response['output'])

# Step 4: Access params using the correct key
modules=parsed_output.modules
[data_params[module] for module in modules]
params = [data_params[module] for module in modules]



# Estimate token usage
prompt_tokens = count_tokens_approx(question)
response_tokens = count_tokens_approx(response)
total_tokens = prompt_tokens + response_tokens

# Estimate token usage
# prompt_tokens_params = count_tokens_approx(question_params)
# response_tokens_params = count_tokens_approx(response_params)
# total_tokens_params = prompt_tokens_params + response_tokens_params


# Output
print("\nResponse:\n", response)
print("\nEstimated Token Usage:")
print("  Prompt Tokens:", prompt_tokens)
print("  Response Tokens:", response_tokens)
print("  Total Tokens:", total_tokens)
print("==================================================================================")
pprint(f"params:{params.get('parameters').keys()}")
# print("\nResponse  Params:\n", response_params  )
# print("\nEstimated Token Usage:")
# print("  Prompt Tokens params:", prompt_tokens_params)
# print("  Response Tokens params:", response_tokens_params)
# print("  Total Tokens params:", total_tokens_params)