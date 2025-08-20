from .base_agent import BaseAgent

class ContributorsAgent(BaseAgent):
    """Agent for analyzing contributor statistics and activity"""
    
    def analyze(self, repo_path: str) -> str:
        """Show contributor statistics and activity for the given repository.
        
        Args:
            repo_path: Path to local directory or GitHub repository URL
            
        Returns:
            Analysis of contributor statistics
        """
        try:
            # Get repository analysis data from base agent
            repo_data = self.analyze_repository(repo_path)
            
            # Generate analysis using LLM
            prompt = f"""Analyze the repository and provide contributor statistics based on this information:
            {repo_data['repo_info']}
            
            Please provide:
            1. Top contributors
            2. Contribution frequency
            3. Recent activity
            4. Suggestions to improve collaboration
            """
            response_text = self.run_llm(prompt)
            return response_text
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error fetching contributor statistics: {str(e)}"