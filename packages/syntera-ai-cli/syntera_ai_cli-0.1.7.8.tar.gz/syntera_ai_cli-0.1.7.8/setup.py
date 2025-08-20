# setup.py

import os
from setuptools import setup, find_packages

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    

def get_package_data():
    """Collect all static files for package_data"""
    package_data = {}
    
    # AWS directory
    aws_files = []
    aws_path = 'devops_ai/agents/aws'
    if os.path.exists(aws_path):
        for root, dirs, files in os.walk(aws_path):
            for file in files:
                if not file.endswith('.py'):  # Exclude Python files
                    rel_path = os.path.relpath(os.path.join(root, file), aws_path)
                    aws_files.append(rel_path)
    if aws_files:
        package_data['devops_ai.agents.aws'] = aws_files
    
    # Monitoring directory  
    monitoring_files = []
    monitoring_path = 'devops_ai/agents/monitoring'
    if os.path.exists(monitoring_path):
        for root, dirs, files in os.walk(monitoring_path):
            for file in files:
                if not file.endswith('.py'):  # Exclude Python files
                    rel_path = os.path.relpath(os.path.join(root, file), monitoring_path)
                    monitoring_files.append(rel_path)
    if monitoring_files:
        package_data['devops_ai.agents.monitoring'] = monitoring_files
    
    return package_data

# Get package data
package_data = get_package_data()
print(f"Package data found: {package_data}")
setup(
    name="syntera-ai-cli",
    version="0.1.7.8",  # Updated version
    author="Fouad Mahmoud",
    author_email="fouadmahmoud281@gmail.com",
    description="An AI-powered DevOps toolkit for infrastructure automation and analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mariamkhaled99/Devops-CLI",
    packages=find_packages(),
    package_data=package_data,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[

        # Compatible LangChain versions
        # langchain-core 0.3.60 is required for stability with this package
        "langchain==0.3.26",                  # Core LangChain library
        "langchain-community==0.3.27",        # Community extensions for LangChain
        "langchain-core>=0.3.68,<1.0.0",      # Core LangChain components
        "langchain-openai==0.3.17",           # OpenAI wrapper for LangChain
        "google-generativeai>=0.3.0",        # Google Gemini support
        "langchain-google-genai>=1.0.0",  # Google Gemini integration

        # Anthropic support with compatible langchain-anthropic version
        "langchain-anthropic==0.3.17",        # Compatible with langchain-core 0.3.60
        "anthropic==0.57.1",                  # Latest tested compatible version

        # LLM provider
        "openai==1.81.0",                     # Official OpenAI API client

        # CLI and utility tools
        "rich==14.0.0",                       # Rich text formatting for CLI
        "typer==0.15.4",                      # CLI framework
        "python-dotenv==1.1.0",               # Environment variable loading

        # AWS and cloud interaction
        "boto3==1.38.21",
        "botocore==1.38.21",

        # Git utilities
        "gitpython==3.1.44",
        "gitingest==0.1.2",                   # Git ingest utility (ensure this exists)

        # Networking and HTTP
        "httpx==0.28.1",
        "urllib3==2.4.0",

        # GitHub API
        "pygithub==2.6.1",

        # Keyboard interactions (might require elevated privileges)
        # "keyboard==0.13.5",
        "inquirer==3.4.1",  # Interactive CLI prompts
        "pyfiglet==1.0.3",  # ASCII art generation

        # Packaging
        "setuptools==75.2.0",
        
        "tiktoken==0.7.0",              # Tokenization for OpenAI models
        # "windows-curses==2.4.1",  # Curses support for Windows (if needed)
    ],
    entry_points={
        "console_scripts": [
            "syntera-ai=devops_ai.cli:app",
        ],
    },
)
