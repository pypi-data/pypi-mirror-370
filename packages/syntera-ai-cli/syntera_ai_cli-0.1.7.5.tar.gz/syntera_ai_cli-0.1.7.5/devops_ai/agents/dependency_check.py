from .base_agent import BaseAgent

class DependencyCheckAgent(BaseAgent):
    """Agent for checking outdated or vulnerable dependencies"""
    
    def analyze(self, repo_path: str) -> str:
        """Check for outdated or vulnerable dependencies in the given repository.
        
        Args:
            repo_path: Path to local directory or GitHub repository URL
            
        Returns:
            Analysis of dependencies
        """
        try:
            # Get repository analysis data from base agent
            repo_data = self.analyze_repository(repo_path)
            
            # Generate analysis using LLM
            prompt = f"""Check the repository for outdated or vulnerable dependencies based on this information:
            {repo_data['repo_info']}
            
            Please provide:
            1. List of outdated dependencies
            2. Known vulnerabilities
            3. Upgrade recommendations
            4. Security best practices
            """
            response_text = self.run_llm(prompt)
            return response_text
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error checking dependencies: {str(e)}"