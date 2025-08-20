from .base_agent import BaseAgent

class LogAnalysisAgent(BaseAgent):
    """Agent for analyzing log files for errors and patterns"""
    
    def analyze(self, log_file: str, repo_path: str = None) -> str:
        """Analyze log files for errors and patterns
        
        Args:
            log_file: Path to the log file to analyze
            repo_path: Optional path to repository for context
            
        Returns:
            Analysis of log file
        """
        try:
            # Read log file content
            with open(log_file, 'r') as f:
                log_content = f.read()
            
            # Get repository context if provided
            repo_context = ""
            if repo_path:
                print(f"Analyzing repository at {repo_path} for context...")
                try:
                    repo_data = self.analyze_repository(repo_path)
                    repo_context = f"\n\nRepository Context:\n{repo_data['summary']}"
                except:
                    print(f"Failed to analyze repository at {repo_path} for context.")
                    pass
            
            # Generate analysis using LLM
            prompt = f"""Analyze the following log file and provide insights:{repo_context}
            {log_content}
            
            Please provide:
            1. Error patterns
            2. Critical issues
            3. Performance bottlenecks
            4. Recommendations
            """
            
            response_text = self.run_llm(prompt)
            return response_text
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error analyzing logs: {str(e)}"

# class LogAnalysisAgent(BaseAgent):
#     """Agent for analyzing log files and optionally repository metadata like framework and port."""

#     def analyze(self, log_file: str = None, repo_path: str = None) -> str:
#         try:
#             repo_context = ""
#             if repo_path:
#                 print(f"Analyzing repository at {repo_path}...")
#                 try:
#                     repo_data = self.analyze_repository(repo_path)
#                     repo_context = repo_data['repo_info']  # this should contain actual code, dependencies, etc.
#                 except Exception as e:
#                     return f"Error analyzing repository: {str(e)}"
#             else:
#                 return "Error: Repository path is required to analyze framework, port, and entry-point."

#             # 🔍 Framework/Port/Entrypoint detection prompt
#             prompt = f"""
# You are a DevOps assistant. Analyze this code repository and identify the following:

# 1. Which web framework (if any) is used. You can determine this from the dependencies (e.g., requirements.txt, package.json) or from the source code itself.
# 2. Which port(s) the server listens on. If the port is not explicitly set in the code, infer the default port based on the detected framework.
# 3. The main entry-point file (i.e., the script or file used to start the server).

# REPOSITORY CONTENT:
# {repo_context}
# """

#             response_text = self.run_llm(prompt)
#             return response_text

#         except Exception as e:
#             return f"Error analyzing logs: {str(e)}"
