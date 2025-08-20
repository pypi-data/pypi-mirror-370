from typing import List, Union
from .base_agent import BaseAgent

class SecurityScanAgent(BaseAgent):
    """Agent for performing security scanning"""
    
    def analyze(self, target: str = "", repo_path: str = None, max_file_size: int = 10485760,
               include_patterns: Union[List[str], str] = None,
               exclude_patterns: Union[List[str], str] = None,
               output: str = None) -> str:
        """Perform security scanning
        
        Args:
            target: Optional target to scan
            repo_path: Optional path to repository for additional context
            max_file_size: Maximum file size in bytes to analyze (default: 10MB)
            include_patterns: List of glob patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/node_modules/**'])
            output: Optional path to save the analysis results
            
        Returns:
            Security scan results
        """
        try:
            # Get repository context if provided
            repo_context = ""
            if repo_path:
                try:
                    # Get repository analysis data from base agent with enhanced parameters
                    repo_data = self.analyze_repository(
                        repo_path=repo_path,
                        max_file_size=max_file_size,
                        include_patterns=include_patterns,
                        exclude_patterns=exclude_patterns,
                        output=output
                    )
                    repo_context = f"\n\nRepository Context:\n{repo_data['repo_info']}"
                except:
                    pass
            
            # Generate analysis using LLM
            prompt = f"""Analyze the following for security concerns:{repo_context}
            {target}
            
            Please provide:
            1. Security vulnerabilities
            2. Compliance issues
            3. Best practices
            4. Remediation steps
            """
            response_text = self.run_llm(prompt)
            return response_text
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error performing security scan: {str(e)}"