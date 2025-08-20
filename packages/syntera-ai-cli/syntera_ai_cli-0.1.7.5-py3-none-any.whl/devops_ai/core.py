import os
from langchain_openai import ChatOpenAI
from langchain.agents import Tool
from dotenv import load_dotenv

# Import all agent classes
from .agents import (
    RepoAnalyzeAgent,
    CodeQualityAgent,
    DependencyCheckAgent,
    ContributorsAgent,
    LogAnalysisAgent,
    InfraSuggestAgent,
    SecurityScanAgent,
    OptimizeAgent,
    DockerGenerationAgent,
    GrapheneAgent
)

# Load environment variables
load_dotenv()

class DevOpsAITools:
    def __init__(self):
        # Initialize agent instances
        self.repo_analyze_agent = RepoAnalyzeAgent()
        self.code_quality_agent = CodeQualityAgent()
        self.dependency_check_agent = DependencyCheckAgent()
        self.contributors_agent = ContributorsAgent()
        self.log_analysis_agent = LogAnalysisAgent()
        self.infra_suggest_agent = InfraSuggestAgent()
        self.security_scan_agent = SecurityScanAgent()
        self.optimize_agent = OptimizeAgent()
        self.docker_generation_agent = DockerGenerationAgent()
      
        self.grafana_analysis_agent = GrapheneAgent()
        
        # Initialize tools
        self.tools = self._initialize_tools()

    def _code_quality(self, repo_path: str, max_file_size: int = 10485760,
                     include_patterns = None, exclude_patterns = None, output = None) -> str:
        """Analyze code quality and maintainability for the given repository."""
        try:
            return self.code_quality_agent.analyze(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error analyzing code quality: {str(e)}"

    def _analyze_logs(self, log_file: str) -> str:
        """Analyze log files for errors and patterns"""
        try:
            return self.log_analysis_agent.analyze(log_file)
        except Exception as e:
            return f"Error analyzing logs: {str(e)}"

    def _infra_suggest(self, context=None, repo_path=None, generate_iac=False):
        """Get infrastructure recommendations"""
        try:
            return self.infra_suggest_agent.analyze(
                query=context,
                repo_path=repo_path,
                generate_iac=generate_iac
            )
        except Exception as e:
            return f"Error getting infrastructure recommendations: {str(e)}"

    def _security_scan(self, target: str = "", repo_path: str = None, max_file_size: int = 10485760,
                      include_patterns = None, exclude_patterns = None, output = None) -> str:
        """Perform security scanning"""
        try:
            return self.security_scan_agent.analyze(
                target=target,
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error performing security scan: {str(e)}"

    def _optimize(self, context: str = "") -> str:
        """Get performance optimization recommendations"""
        try:
            return self.optimize_agent.analyze(context)
        except Exception as e:
            return f"Error getting optimization recommendations: {str(e)}"

    def _dependency_check(self, repo_path: str, max_file_size: int = 10485760,
                      include_patterns = None, exclude_patterns = None, output = None) -> str:
        """Check for outdated or vulnerable dependencies in the given repository."""
        try:
            return self.dependency_check_agent.analyze(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error checking dependencies: {str(e)}"

    def _contributors(self, repo_path: str, max_file_size: int = 10485760,
                       include_patterns = None, exclude_patterns = None, output = None) -> str:
        """Show contributor statistics and activity for the given repository."""
        try:
            return self.contributors_agent.analyze(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error fetching contributor statistics: {str(e)}"

    def _repo_analyze(self, repo_path: str, max_file_size: int = 10485760,
                      include_patterns = None, exclude_patterns = None, output = None) -> str:
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
            return self.repo_analyze_agent.analyze(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error analyzing repository: {str(e)}"

    def _docker_generation(self, repo_path: str, env_path: str = None, max_file_size: int = 10485760,
                      include_patterns = None, exclude_patterns = None, output = None) -> str:
        """Generate Docker and docker-compose files for the given repository.
        
        Args:
            repo_path: Path to local directory or GitHub repository URL
            max_file_size: Maximum file size in bytes to analyze (default: 10MB)
            include_patterns: List of glob patterns to include (e.g., ['*.py', '*.js'])
            exclude_patterns: List of glob patterns to exclude (e.g., ['**/node_modules/**'])
            output: Optional path to save the analysis results
            
        Returns:
            Results of Docker file generation
        """
        try:
            return self.docker_generation_agent.analyze(
                repo_path=repo_path,
                env_path=env_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"Error generating Docker files: {str(e)}"
        
    def _grafana_analysis(self, repo_path: str, max_file_size: int = 10485760,
                      include_patterns=None, exclude_patterns=None, output=None) -> str:
        """
        Analyze Grafana setup within a repository for dashboards, data sources, and observability practices.

        Args:
            repo_path (str): Path to the local repository or GitHub repository URL.
            max_file_size (int, optional): Max file size to include in analysis (default: 10MB).
            include_patterns (list[str] or str, optional): File patterns to include (e.g., ['*.json', '*.yml']).
            exclude_patterns (list[str] or str, optional): File patterns to exclude.
            output (str, optional): Optional output path to store analysis result.

        Returns:
            str: Analysis summary or recommendations for the Grafana setup.
        """
        try:
            return self.grafana_analysis_agent.analyze(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )
        except Exception as e:
            return f"❌ Error analyzing Grafana repository: {str(e)}"


    def _initialize_tools(self):
        return [
            Tool(
                name="analyze_logs",
                func=self._analyze_logs,
                description="Analyze log files for errors and patterns"
            ),
            Tool(
                name="infra_suggest",
                func=self._infra_suggest,
                description="Get infrastructure recommendations"
            ),
            Tool(
                name="security_scan",
                func=self._security_scan,
                description="Perform security scanning with customizable file filters"
            ),
            Tool(
                name="optimize",
                func=self._optimize,
                description="Get performance optimization recommendations"
            ),
            Tool(
                name="repo_analyze",
                func=self._repo_analyze,
                description="Analyze GitHub repositories for insights and patterns with customizable file filters"
            ),
            Tool(
                name="code_quality",
                func=self._code_quality,
                description="Analyze code quality and maintainability with customizable file filters"
            ),
            Tool(
                name="dependency_check",
                func=self._dependency_check,
                description="Check for outdated or vulnerable dependencies with customizable file filters"
            ),
            Tool(
                name="contributors",
                func=self._contributors,
                description="Show contributor statistics and activity with customizable file filters"
            ),
            Tool(
                name="docker_generation",
                func=self._docker_generation,
                description="Generate Docker and docker-compose files based on repository analysis"
            ),
            Tool(
    name="grafana_analysis",
    func=self._grafana_analysis,
    description="Analyze Grafana configuration and dashboards for observability insights and best practices"
)

        ]