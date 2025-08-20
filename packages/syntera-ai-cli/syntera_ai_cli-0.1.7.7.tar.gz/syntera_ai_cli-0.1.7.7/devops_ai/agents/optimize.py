from .base_agent import BaseAgent

class OptimizeAgent(BaseAgent):
    """Agent for providing performance optimization recommendations"""
    
    def analyze(self, context: str = "", repo_path: str = None) -> str:
        """Get performance optimization recommendations
        
        Args:
            context: Optional context for optimization
            repo_path: Optional path to repository for additional context
            
        Returns:
            Optimization recommendations
        """
        try:
            # Get repository context if provided
            repo_context = ""
            if repo_path:
                try:
                    repo_data = self.analyze_repository(repo_path)
                    repo_context = f"\n\nRepository Context:\n{repo_data['repo_info']}"
                except:
                    pass
            
            # Generate analysis using LLM
            prompt = f"""Based on the following context, provide optimization recommendations:{repo_context}
            {context}
            
            Please provide:
            1. Performance bottlenecks
            2. Resource utilization
            3. Optimization strategies
            4. Implementation steps
            """
            response = self.run_llm(prompt)
            return response
            # response = self.llm.invoke(prompt)
            # return response.content
        except Exception as e:
            return f"Error generating optimization recommendations: {str(e)}"