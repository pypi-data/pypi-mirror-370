
# import asyncio
# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic
# from langchain_google_genai import ChatGoogleGenerativeAI

# from mcp_use import MCPAgent, MCPClient

# anthropic_key = os.getenv("ANTHROPIC_API_KEY")
# gemeini_key = os.getenv("GEMINI_API_KEY")

# async def main():
#     """Run the example using a configuration file."""
#     # Load environment variables
#     load_dotenv()

#     config ={
#   "mcpServers": {
#     "awslabs.aws-documentation-mcp-server": {
#       "command": "docker",
#       "args": [
#         "run",
#         "--rm",
#         "--interactive",
#         "--env",
#         "FASTMCP_LOG_LEVEL=ERROR",
#         "--env",
#         "AWS_DOCUMENTATION_PARTITION=aws",
#         "mcp/aws-documentation:latest"
#       ],
#       "env": {},
#       "disabled": False,
#       "autoApprove": []
#     }
#   }
# }

#     # Create MCPClient from config file
#     client = MCPClient.from_dict(config)

#     # Create LLM
#     # llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROCK_API_KEY"))
#     llm = ChatGoogleGenerativeAI(
#                     model="gemini-2.5-flash",
#                 temperature=0.2,
#                 google_api_key=os.getenv("GEMINI_API_KEY")
#                 )
    
#     # llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")


#     # Create agent with the client
#     agent = MCPAgent(llm=llm, client=client, max_steps=30,use_server_manager=False)

#     # Run the query
#     result = await agent.run(
#         "What Ansible modules are used for creating AWS VPC, Subnet, and Route Table?",
#         max_steps=30,
#     )

#     print(f"\n🔍 Result:\n{result}")

# import asyncio
# import os
# from dotenv import load_dotenv

# from langchain_google_genai import ChatGoogleGenerativeAI
# from mcp_use import MCPAgent, MCPClient

# # ✅ Load .env file before accessing keys
# load_dotenv()

# async def main():
#     """Query AWS documentation MCP server for Ansible integration details."""
    
#     # ✅ MCP server config using Docker to run the AWS documentation server
#     config = {
#         "mcpServers": {
#             "awslabs.aws-documentation-mcp-server": {
#                 "command": "docker",
#                 "args": [
#                     "run",
#                     "--rm",
#                     "--interactive",
#                     "--env", "FASTMCP_LOG_LEVEL=ERROR",
#                     "--env", "AWS_DOCUMENTATION_PARTITION=aws",
#                     "mcp/aws-documentation:latest"
#                 ],
#                 "env": {},
#                 "disabled": False,
#                 "autoApprove": []
#             }
#         }
#     }

#     # ✅ Initialize MCP Client from config
#     client = MCPClient.from_dict(config)

#     # ✅ Create LLM (Gemini 2.5 Flash)
#     llm = ChatGoogleGenerativeAI(
#         model="gemini-2.5-flash",
#         temperature=0.2,
#         google_api_key=os.getenv("GEMINI_API_KEY")
#     )

#     # ✅ Create MCP agent
#     agent = MCPAgent(
#         llm=llm,
#         client=client,
#         max_steps=30,
#         use_server_manager=False
#     )

#     # ✅ Run a query about Ansible AWS integrations
#     query = "What Ansible modules are used for creating AWS VPC, Subnet, and Route Table?"
#     result = await agent.run(query, max_steps=30)

#     # ✅ Output the result
#     print("\n🔍 Query:")
#     print(query)
#     print("\n📄 Result:")
#     print(result)

# if __name__ == "__main__":
#     asyncio.run(main())


import asyncio
import os
import subprocess
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key
load_dotenv()

def estimate_token_count(text: str) -> int:
    # Approximate estimation: average of 0.75 words/token for English
    return int(len(text.split()) / 0.75)

async def main():
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", "ansible-doc-list"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        modules_output = result.stdout
    except subprocess.CalledProcessError as e:
        print("🚨 Docker error:", e.stderr)
        return

    # Filter only relevant Ansible modules
    relevant_lines = [
        line for line in modules_output.splitlines()
        if any(keyword in line.lower() for keyword in ['amazon.aws'])
    ]
    filtered_output = "\n".join(relevant_lines)

    # Build the prompt
    query = f"""
Which of these Ansible modules are related to AWS VPCs, Subnets, or Route Tables?
List only module names.

Modules:
{filtered_output}
"""

    # Estimate input token usage
    input_tokens = estimate_token_count(query)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    # Get response
    response = await llm.ainvoke(query)

    output_text = response.content
    output_tokens = estimate_token_count(output_text)
    total_tokens = input_tokens + output_tokens

    print("\n🔍 Prompted query:\n")
    print(query)

    print("\n📄 Gemini Response:\n")
    print(output_text)

    print("\n📊 Estimated Token Usage:")
    print(f"Input Tokens: {input_tokens}")
    print(f"Output Tokens: {output_tokens}")
    print(f"Total Tokens: {total_tokens}")

if __name__ == "__main__":
    asyncio.run(main())
