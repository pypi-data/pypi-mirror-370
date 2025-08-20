from typing import List, Union
from .base_agent import BaseAgent

class CodeQualityAgent(BaseAgent):
    """Agent for analyzing code quality and maintainability"""
    
    def analyze(self, repo_path: str, max_file_size: int = 10485760,
               include_patterns: Union[List[str], str] = None,
               exclude_patterns: Union[List[str], str] = None,
               output: str = None) -> str:
        """Analyze code quality and maintainability for the given repository.
        
        Args:
            repo_path: Path to local directory or GitHub repository URL
            max_file_size: Maximum file size in bytes to analyze (default: 10MB)
            include_patterns: List of glob patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/node_modules/**'])
            output: Optional path to save the analysis results
            
        Returns:
            Analysis of code quality and maintainability
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
            prompt = f"""Analyze the code quality and maintainability of the repository based on this information:
            {repo_data['repo_info']}
            
            Please provide:
            1. Code smells and anti-patterns
            2. Maintainability issues
            3. Suggestions for improvement
            4. Best practices
            """
            response_text = self.run_llm(prompt)
            return response_text
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error analyzing code quality: {str(e)}"