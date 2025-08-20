from typing import List, Union
from .base_agent import BaseAgent

class RepoAnalyzeAgent(BaseAgent):
    """Agent for analyzing GitHub repositories for insights and patterns"""
    
    def analyze(self, repo_path: str, max_file_size: int = 10485760,
               include_patterns: Union[List[str], str] = None,
               exclude_patterns: Union[List[str], str] = None,
               output: str = None) -> str:
        """Analyze GitHub repositories for insights and patterns
        
        Args:
            repo_path: Path to local directory or GitHub repository URL
            max_file_size: Maximum file size in bytes to analyze (default: 10MB)
            include_patterns: List of glob patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/node_modules/**'])
            output: Optional path to save the analysis results
            
        Returns:
            Analysis of the repository content
        """
        try:
            # Get repository analysis data from base agent with enhanced parameters
            repo_data = self.analyze_repository(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
            
            # Generate analysis using LLM
            prompt = f"""Analyze the following GitHub repository information and provide DevOps insights:
            {repo_data['repo_info']}
            
            Please provide:
            1. Code quality assessment
            2. Architecture patterns
            3. Potential technical debt
            4. DevOps improvement opportunities
            5. Security considerations
            """

            response_text=self.run_llm(prompt)
            return response_text
        except Exception as e:
            return f"Error analyzing repository: {str(e)}"