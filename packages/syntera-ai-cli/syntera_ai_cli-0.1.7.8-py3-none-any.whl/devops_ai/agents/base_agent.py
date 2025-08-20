

import os
from typing import List, Union, Dict
from dotenv import load_dotenv
from gitingest import ingest, ingest_from_query, clone_repo, parse_query
import urllib3
import ssl
import httpx
import csv
from datetime import datetime
from pathlib import Path

# LLM clients
# from langchain_openai import ChatOpenAI
# from langchain_anthropic import ChatAnthropic # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from devops_ai.env_loader import gemini_key
# Disable SSL warnings – not recommended for production
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""
os.environ["SSL_CERT_FILE"] = ""



class BaseAgent:
    """Base agent class that supports OpenAI or Anthropic as backend LLM."""
    
    def __init__(self):
        try:
            # Create httpx client with SSL verification disabled
            http_client = httpx.Client(verify=False)

            # Check which LLM provider is available
            # openai_key = os.getenv("OPENAI_API_KEY")
            # anthropic_key = os.getenv("ANTHROPIC_API_KEY")
            
            # print(f"Using LLM API key: {anthropic_key if anthropic_key else 'None'}")

            # if openai_key:
            #     # Initialize OpenAI LLM
            #     self.llm = ChatOpenAI(
            #         temperature=0,
            #         model_name="gpt-4-turbo-preview",
            #         openai_api_key=openai_key,
            #         http_client=http_client,
            #     )
            #     print("Using OpenAI (ChatOpenAI)")
            if gemini_key:
                # Initialize Google Gemini LLM
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=gemini_key
                )
                print("Using Google Gemini (ChatGoogleGenerativeAI)")

            # if anthropic_key:
            #     # Initialize Anthropic LLM
            #     self.llm = ChatAnthropic(
            #         temperature=0,
            #         model="claude-sonnet-4-20250514",
            #         anthropic_api_key=anthropic_key,
            #         # http_client=http_client,
            #     )
                # print("Using Anthropic (ChatAnthropic)")
               
            else:
                raise ValueError("No LLM API key found. Please set GEMINI_API_KEY.")
            
            if self.llm:
                self.model_name = self.model_name = getattr(self.llm, "model", "gemini-2.5-flash")
                self.total_tokens_used = 0
                self.total_cost_usd = 0.0
                self.budget_usd = float(os.getenv("LLM_BUDGET", 5.0))  # Default $5 budget
                
            print("LLM Provider:", type(self.llm).__name__)

        except ssl.SSLError as e:
            print(f"SSL error initializing LLM: {str(e)}")
            raise
        except Exception as e:
            print(f"Error initializing LLM: {str(e)}")
            raise

    def analyze_repository(self, repo_path: str, max_file_size: int = 10485760, 
                        include_patterns: Union[List[str], str] = None, 
                        exclude_patterns: Union[List[str], str] = None,
                        output: str = None) -> dict:
        try:
            
            if repo_path.startswith(('http://', 'https://', 'git@')):
                query = {"url": repo_path}
                print(f"Cloning repository {repo_path}...")
                local_path = self.clone_repository(query)
                print(f"Repository cloned to {local_path}")
                repo_path = local_path

            summary, tree, content = ingest(
                source=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
            print(f"tree: {tree}")

            return {
                "summary": summary,
                "tree": tree,
                "content": content,
                "repo_info": f"""Repository Summary: {summary}
                
Repository Structure:
{tree}

Key Content Insights:
{content}"""
            }
            
        except Exception as e:
            raise Exception(f"Error analyzing repository: {str(e)}")

    def clone_repository(self, query: dict) -> str:
        try:
            import asyncio
            return asyncio.run(clone_repo(query))
        except Exception as e:
            raise Exception(f"Error cloning repository: {str(e)}")

    def analyze_from_query(self, query: dict) -> Dict:
        try:
            return ingest_from_query(query)
        except Exception as e:
            raise Exception(f"Error analyzing repository from query: {str(e)}")

    def parse_repository_query(self, source: str, max_file_size: int = 10485760, 
                             from_web: bool = False,
                             include_patterns: Union[List[str], str] = None, 
                             ignore_patterns: Union[List[str], str] = None) -> dict:
        try:
            return parse_query(
                source=source,
                max_file_size=max_file_size,
                from_web=from_web,
                include_patterns=include_patterns,
                ignore_patterns=ignore_patterns
            )
        except Exception as e:
            raise Exception(f"Error parsing repository query: {str(e)}")
        
    
    # helper method to moinitor costs and tokens
    def get_model_cost_per_1k_tokens(self) -> float:
        """Get the cost per 1k tokens for the current model."""
        # model_name = getattr(self.llm, "model", "").lower()
        model_name="models/gemini-2.5-flash"

        # Normalize known aliases
        if "claude" in model_name:
            if "sonnet" in model_name:
                return 0.003  # $0.003 per 1k tokens for Claude Sonnet
            elif "haiku" in model_name:
                return 0.00025  # $0.00025 per 1k tokens for Claude Haiku
            elif "opus" in model_name:
                return 0.015  # $0.015 per 1k tokens for Claude Opus
        elif "gemini" in model_name:
            print(f"model_name:{model_name}")
            return 0.01

        if "gpt-4" in model_name:
            return 0.01  # $0.01 per 1k tokens (adjust for gpt-4-turbo if needed)

        # Fallback
        return 0.0

    import csv


    def run_llm(self, messages: Union[str, List[Dict[str, str]]]) -> str:
        """Call the LLM, return response, and track token usage + cost + log to CSV."""
        try:
            

            # Normalize message format
            if isinstance(messages, str):
                messages = [HumanMessage(content=messages)]

            # Invoke LLM
            response = self.llm.invoke(messages)

            # Extract token usage from response metadata
            print(f"Response metadata: {response.response_metadata}")
            # print("===============================================================")
            # usage = response.response_metadata.get("usage", {})
            # print(f"usage: {usage}")
            # print("===============================================================")
            # input_tokens = usage.get("input_tokens", 0)
            # print(f"input_tokens: {input_tokens}")  
            # print("===============================================================")
            # output_tokens = usage.get("output_tokens", 0)
            # print(f"output_tokens: {output_tokens}")
            # print("===============================================================")
            # total_tokens = input_tokens + output_tokens
            # print(f"total_tokens: {total_tokens}")
            # print("===============================================================")

            # Calculate cost
            # cost = (total_tokens / 1000) * self.get_model_cost_per_1k_tokens()

            # # Track totals
            # self.total_tokens_used += total_tokens
            # self.total_cost_usd += cost
            # self.budget_usd -= cost

            # Print usage summary
            print("==============agent monitoring costs and tokens==============")
            # print(f"🔢 Input tokens: {input_tokens}")
            # print(f"🔢 Output tokens: {output_tokens}")
            # print(f"🔢 Total tokens: {total_tokens}")
            # print(f"💰 Cost this call: ${cost:.4f}")
            # print(f"📊 Total cost so far: ${self.total_cost_usd:.4f}")
            # print(f"💼 Remaining budget: ${self.budget_usd:.2f}")
            print("=============================================================")

            # ✅ Log to CSV
            # csv_path = Path("llm_usage_log.csv")
            # file_exists = csv_path.exists()

            # with csv_path.open("a", newline='', encoding="utf-8") as csvfile:
            #     writer = csv.writer(csvfile)
            #     if not file_exists:
            #         writer.writerow([
            #             "timestamp", "model", "tokens_used", "cost_usd",
            #             "total_cost_usd", "remaining_budget_usd"
            #         ])
            #     writer.writerow([
            #         datetime.now().isoformat(timespec="seconds"),
            #         getattr(self.llm, "model", type(self.llm).__name__),
            #         total_tokens,
            #         round(cost, 4),
            #         round(self.total_cost_usd, 4),
            #         round(self.budget_usd, 2)
            #     ])

            return response.content if hasattr(response, "content") else str(response)

        except Exception as e:
            raise Exception(f"Error running LLM: {e}")
