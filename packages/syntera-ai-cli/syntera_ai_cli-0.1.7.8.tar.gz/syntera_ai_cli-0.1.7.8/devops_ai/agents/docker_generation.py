import re
from typing import List, Union, Dict, Any

import tiktoken
from .base_agent import BaseAgent
import os
import json
import logging
import datetime
from pathlib import Path
from git import Repo
from github import Github
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import HumanMessage
from langchain.output_parsers import StructuredOutputParser, ResponseSchema


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)



# # Dependency and entrypoint file patterns
DEPENDENCY_FILES = {
    "requirements.txt", "package.json", "pom.xml", "build.gradle","tsconfig.json"
    "composer.json", "gemfile", "cargo.toml", "setup.py",
    "pyproject.toml", "environment.yml", "pipfile", "makefile", "dockerfile"
}

ENTRYPOINT_KEYWORDS = ["app.run(", "app.listen(", "main(", "__main__", "server.start", "uvicorn.run"]

FRONTEND_EXTENSIONS = {".html", ".js", ".jsx", ".ts", ".tsx", ".vue", ".css"}




class DockerGenerationAgent(BaseAgent):
    """Agent for generating Docker and docker-compose files based on repository analysis"""

    def __init__(self):
       super().__init__() 
       
    def extract_key_files(self, repo_path: str, max_files: int = 5) -> dict:
        print(f"Extracting key files from repository: {repo_path}")
        repo_path = Path(repo_path)
        file_contents = {}

        # Get dependency files first
        for file in repo_path.rglob("*"):
            name = file.name.lower()
            if name in DEPENDENCY_FILES:
                try:
                    content = file.read_text(encoding='utf-8')[:2000]
                    file_contents[str(file.relative_to(repo_path))] = content
                    if len(file_contents) >= max_files:
                        break
                except Exception as e:
                    file_contents[str(file.relative_to(repo_path))] = f"[Error reading file: {e}]"

        # Try to identify likely entrypoint files (app.py, server.js etc.)
        if len(file_contents) < max_files:
            for file in repo_path.rglob("*"):
                if file.suffix in {".py", ".js", ".ts", ".go"}:
                    try:
                        content = file.read_text(encoding='utf-8')[:2000]
                        if any(k in content for k in ENTRYPOINT_KEYWORDS):
                            file_contents[str(file.relative_to(repo_path))] = content
                            if len(file_contents) >= max_files:
                                break
                    except:
                        pass

        return file_contents
    def extract_frontend_files(self, repo_path: Path, max_files: int = 5) -> dict:
        frontend_files = {}
        for file in repo_path.rglob("*"):
            if file.suffix in FRONTEND_EXTENSIONS:
                try:
                    content = self._strip_comments(file.read_text(encoding='utf-8')[:2000], file.suffix)
                    frontend_files[str(file.relative_to(repo_path))] = content
                    if len(frontend_files) >= max_files:
                        break
                except Exception as e:
                    frontend_files[str(file.relative_to(repo_path))] = f"[Error reading file: {e}]"
        return frontend_files

    def _strip_comments(self, content: str, extension: str) -> str:
        if extension in {'.js', '.ts', '.jsx', '.tsx'}:
            # Remove // and /* */ comments
            content = re.sub(r'//.*?$|/\*.*?\*/', '', content, flags=re.DOTALL | re.MULTILINE)
        elif extension == '.html':
            # Remove HTML comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        return content

    def analyze(self, repo_path: str,env_path:str, max_file_size: int = 10485760,
                include_patterns: Union[List[str], str] = None,
                exclude_patterns: Union[List[str], str] = None,
                output: str = None) -> str:
        """Analyze repository structure and generate Docker files"""
        try:
            abs_repo_path = os.path.abspath(repo_path)
            logger.info(f"Starting analysis for repo: {repo_path}")
            logger.info(f"Absolute path: {abs_repo_path}")
            logger.info(f"Directory exists: {os.path.isdir(abs_repo_path)}")

            repo_data = self.analyze_repository(
                repo_path=repo_path,
                max_file_size=max_file_size,
                include_patterns=include_patterns,
                exclude_patterns=exclude_patterns,
                output=output
            )

            if 'repo_path' not in repo_data:
                repo_data['repo_path'] = abs_repo_path

            dockerfile_content, compose_content = self._generate_docker_files(repo_data, env_path=env_path)

            logger.info(f"Docker files generated. Services: {list(dockerfile_content.keys())}")
            logger.info(f"Compose content length: {len(compose_content) if compose_content else 0}")

            self._write_docker_files(abs_repo_path, dockerfile_content, compose_content)

            return f"Successfully generated Docker files for {repo_path}:\n" + \
                   f"Dockerfile(s): {', '.join(list(dockerfile_content.keys()))}\n" + \
                   f"docker-compose.yml: {'Created' if compose_content else 'Not created'}"

        except Exception as e:
            logger.error(f"Error generating Docker files: {str(e)}", exc_info=True)
            return f"Error generating Docker files: {str(e)}"

    def _generate_docker_files(self, repo_data: Dict[str, Any], env_path: str = None) -> tuple:
        """Generate Dockerfile(s) and docker-compose.yml content using LangChain + OpenAI in a token-efficient manner."""
        # TODO: Exclude the .git directory from tree

        repo_structure = repo_data.get('tree', {})
        repo_path = repo_data.get('repo_path', None)

        print(f"[INFO] Starting Docker generation for: {repo_path}")
        logger.info(f"[INFO] Starting Docker generation for: {repo_path}")
        logger.debug(f"[DEBUG] Repository structure (tree): {repo_structure}")

        # Step 1: Get framework info (already optimized)
        framework_context = self.get_port_framework(repo_path)
        try:
            framework_data = json.loads(re.sub(r"```json|```", "", framework_context.strip()))
            logger.debug(f"[DEBUG] Detected framework info: {framework_data}")
        except json.JSONDecodeError:
            logger.warning("[WARN] Could not parse framework info as JSON.")
            framework_data = {}

        # Step 2: Extract key files
        file_contents = self.extract_key_files(repo_path, max_files=4)
        print(f"[INFO] Extracted key files: {list(file_contents.keys())}")
        logger.info(f"[INFO] Extracted {len(file_contents)} key files: {list(file_contents.keys())}")

        # Step 3a: Generate Dockerfiles using LLM
        dockerfile_prompt = f"""
    You are a DevOps assistant. Generate Dockerfiles based on the following backend/frontend details and key files.

    Framework info:
    {json.dumps(framework_data, indent=2)}

    Use this information to generate appropriate Dockerfile(s).
    This is the repo_path: {repo_path}
        - When copying files in Docker, make sure to use a relative path based on the Docker build context.

    Follow these guidelines strictly:
    - Use multi-stage builds only in case of frontend or backend js based applications .
    - If system-level packages are required, install them first .
    - Before installing application dependencies, install required system-level build tools using the system_packages field in frontend and backend as well .
    - if typescript in the system_packages field, install it using npm install -g typescript in addition with package.json install.
    - Make sure to install npm install instead of npm ci (always).
    - Use the dependency files to infer necessary OS-level packages. 
    - Always install dependencies before copying the rest of the application source code.
    - Use actively maintained and secure minimal base images based on the detected language and framework.
        - prefer the most recent stable version .
        - do not use deprecated or unsupported base images , The buster variant is outdated .
        - Automatically detect the appropriate version from dependency files .
        - Avoid using deprecated or outdated base image tags or any tag associated with unsupported Debian versions.
        - Ensure the base image is compatible with system-level package installation if needed.
    - make sure to copy the whole application code into the container after installing dependencies with the correct path and name.
    - Use the correct working directory for the application.
    - Do not copy nginx configuration files from the repository, instead use the default nginx configuration.
    - Use the correct COMMAND or ENTRYPOINT to run the application that related to the framework and make sure it is full correct path using the entrpoint_file.
    - Include labels like maintainer, version only for docker files (always add them after the image tags).
    - Do not add any comments in the Dockerfile.
    - Avoid invalid syntax and assumptions about stack
    - Make sure to use file naming format: `Dockerfile.<service_name>` 
    - If unsure, clearly explain why and do not generate invalid files
    
    Repository Structure:
    {repo_structure}
    
    """

   

        dockerfile_schema = [
            ResponseSchema(name="dockerfiles", description="Dictionary of Dockerfile contents for each service"),
            ResponseSchema(name="is_nginx_frontend_used", description="Indicates if Nginx is used in frontend"),
            ResponseSchema(name="is_nginx_backend_used", description="Nginx configuration content if used")
        ]
        dockerfile_parser = StructuredOutputParser.from_response_schemas(dockerfile_schema)
        dockerfile_prompt += dockerfile_parser.get_format_instructions()

        try:
            dockerfile_response = self.run_llm(dockerfile_prompt)
            # with open(os.path.join(repo_path, "dockerfile_raw.json"), "w") as f:
            #     f.write(dockerfile_response)
            dockerfile_result = dockerfile_parser.parse(dockerfile_response)
            # 🛡️ Defensive parse if it's returned as a string
            if isinstance(dockerfile_result, str):
                try:
                    dockerfile_result = json.loads(dockerfile_result)
                except json.JSONDecodeError as e:
                    logger.error(f"[ERROR] Failed to parse 'dockerfiles' as JSON: {e}")
                    raise ValueError("Invalid Dockerfiles format returned from LLM.")

            dockerfiles = dockerfile_result.get("dockerfiles", {})
            is_nginx_frontend_used = dockerfile_result.get("is_nginx_frontend_used", False)
            is_nginx_backend_used = dockerfile_result.get("is_nginx_backend_used", False)
            
            
            print(f"[INFO] Generated Dockerfiles: {list(dockerfiles.keys()) if dockerfiles else 'None'}")
            logger.info(f"[INFO] Generated Dockerfiles: {list(dockerfiles.keys()) if dockerfiles else 'None'}")     
            print(f"[INFO] Nginx frontend used: {is_nginx_frontend_used}")
            logger.info(f"[INFO] Nginx frontend used: {is_nginx_frontend_used}")
            print(f"[INFO] Nginx backend used: {is_nginx_backend_used}")    
            logger.info(f"[INFO] Nginx backend used: {is_nginx_backend_used}")

          

            # with open(os.path.join(repo_path, "dockerfiles.json"), "w") as f:
            #     json.dump(dockerfiles, f, indent=2)

        except Exception as e:
            logger.error(f"[ERROR] Failed to generate Dockerfiles: {e}")
            return {}, ""
        env_file_path = os.path.join(repo_path, '.env') if repo_path else None

        env_path = env_file_path if env_file_path and os.path.isfile(env_file_path) else None
        print("env_path:", env_path) 

        # Step 3b: Generate docker-compose.yml separately
        compose_prompt = f"""
    You are a DevOps assistant. Generate a docker-compose.yml file based on the following data:

    Framework info:
    {json.dumps(framework_data, indent=2)}


    Guidelines:
    - Define each service with build context '.', get Dockerfile name from {dockerfiles.keys() if dockerfiles else 'N/A'}
    - Use ports based on detected framework .
        
    - If the frontend Dockerfile uses Nginx (e.g., FROM nginx, or Nginx is part of build): {is_nginx_frontend_used}
    - Expose container port **80** (Nginx default).
    - Map it to the **host port** specified in frontend framework info (frontend_host_port) .
    - Example: ports:
                - "<frontend_host_port>:80"
    if backend Dockerfile needed migration or database connection add the command for it and make sure to wait it .
    - If Nginx is used in backend: {is_nginx_backend_used}
        - Map container port **80** to the **host port** from backend framework info.
    - Use 'depends_on' if backend needed by frontend
    - Add .env file in each service only if env_path is provided:
    {f"env_path is provided: {env_path}" if env_path else "env_path is not provided"}
    - If provided, add to each service:
        env_file:
            - .env
    - If not provided, do not add env_file at all.
    - Do not use 'version' .
    -Make sure to use the correct port for each service based on the framework info and if there is conflict map it.
    - Do not add any comments in the docker_compose.yml.
    """

        compose_schema = [
            ResponseSchema(name="docker_compose", description="Docker Compose YAML content")
        ]
        compose_parser = StructuredOutputParser.from_response_schemas(compose_schema)
        compose_prompt += compose_parser.get_format_instructions()

        try:
            compose_response = self.run_llm(compose_prompt)
            # with open(os.path.join(repo_path, "compose_raw.json"), "w") as f:
            #     f.write(compose_response)
            compose_result = compose_parser.parse(compose_response)
            docker_compose = compose_result.get("docker_compose", "").strip()

            if not docker_compose or "generation failed" in docker_compose.lower():
                raise ValueError("Invalid docker-compose.yml content.")

            # with open(os.path.join(repo_path, "docker-compose.yml"), "w") as f:
            #     f.write(docker_compose)

        except Exception as e:
            logger.error(f"[ERROR] Failed to generate docker-compose.yml: {e}")
            return {}, ""

        # Final logging and return
        # logger.info("[INFO] Successfully generated Dockerfiles and docker-compose.")
        # with open(os.path.join(repo_path, ".repo-analysis.json"), "w") as f:
        #     json.dump(framework_data, f, indent=2)

        return dockerfiles, docker_compose




    def _write_docker_files(self, repo_path: str, dockerfiles: dict, compose_content: str) -> None:
        """Write Dockerfile(s), docker-compose.yml, and supporting files to the repository"""
        try:
            if repo_path.startswith(('http://', 'https://', 'git@')):
                raise ValueError("Repository path must be a local directory")

            logger.debug(f"Writing Docker files to {repo_path}")
            logger.debug(f"Dockerfiles to write: {list(dockerfiles.keys()) if dockerfiles else 'None'}")

            if not os.path.isdir(repo_path):
                logger.error(f"Repository path is not a directory: {repo_path}")
                raise ValueError(f"Invalid repository path: {repo_path}")

            if not dockerfiles:
                logger.error("No Dockerfiles generated. Cannot proceed.")
                raise ValueError("No Dockerfiles generated. Cannot proceed.")

            # Write Dockerfiles
            for service, content in dockerfiles.items():
                dockerfile_path = os.path.join(repo_path, f"{service}" if service.startswith("Dockerfile.") else f"Dockerfile.{service}")
                logger.info(f"Writing Dockerfile for {service} to {dockerfile_path}")
                with open(dockerfile_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.debug(f"Successfully wrote {dockerfile_path}")

            # Write docker-compose.yml
            if compose_content:
                compose_path = os.path.join(repo_path, "docker-compose.yml")
                logger.info(f"Writing docker-compose.yml to {compose_path}")
                with open(compose_path, "w", encoding="utf-8") as f:
                    f.write(compose_content)
                logger.debug(f"Successfully wrote {compose_path}")

            # Generate .dockerignore
            self._generate_dockerignore(repo_path)

            # Generate README-Docker.md
            self._generate_docker_readme(repo_path, dockerfiles)

            # Generate GitHub Actions CI/CD workflow
            self._generate_github_actions_workflow(repo_path)

            # Save analysis log
            self._save_analysis_log(repo_path, dockerfiles, compose_content)

        except Exception as e:
            logger.error(f"Error in _write_docker_files: {str(e)}", exc_info=True)
            raise

    def _generate_dockerignore(self, repo_path: str):
        default_ignore = """
.git
__pycache__
*.log
*.env
.env
node_modules
*.pyc
*.tmp
*.bak
*.swp
*.swo
*.DS_Store
Thumbs.db
*.md
README.md
"""

        dockerignore_path = os.path.join(repo_path, ".dockerignore")
        if not os.path.exists(dockerignore_path):
            with open(dockerignore_path, "w", encoding="utf-8") as f:
                f.write(default_ignore.strip())
            logger.info(f"Generated .dockerignore at {dockerignore_path}")

    def _generate_docker_readme(self, repo_path: str, dockerfiles: dict):
        services = "\n".join([f"- `{k}`" for k in dockerfiles.keys()])
        content = f"""# Docker Setup Guide

This document was auto-generated by the Docker Generation Agent.

## Available Services
{services}

## How to Use

### Build all services:
```bash
docker-compose build
```

### Run all services:
```bash
docker-compose up -d
```

### Build individual service:
```bash
docker build -t <service-name> -f Dockerfile.<service-name> .
```

### View logs:
```bash
docker-compose logs -f
```

For more info see: https://docs.docker.com/
"""

        readme_path = os.path.join(repo_path, "README-Docker.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Generated README-Docker.md at {readme_path}")

    def _generate_github_actions_workflow(self, repo_path: str):
        workflow_dir = os.path.join(repo_path, ".github", "workflows")
        os.makedirs(workflow_dir, exist_ok=True)

        workflow_content = """name: Docker Build and Push
on:
  push:
    branches:
      - main
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      - name: Build and push
        id: docker_build
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: your-dockerhub-username/your-image:latest
"""

        workflow_path = os.path.join(workflow_dir, "docker-build.yml")
        with open(workflow_path, "w", encoding="utf-8") as f:
            f.write(workflow_content)
        logger.info(f"Generated GitHub Actions workflow at {workflow_path}")

    def _save_analysis_log(self, repo_path: str, dockerfiles: dict, compose_content: str):
        log_content = {
            "timestamp": datetime.datetime.now().isoformat(),
            "dockerfiles": list(dockerfiles.keys()),
            "docker_compose_present": bool(compose_content),
            "llm_model": "gpt-4o-mini"
        }

        # log_path = os.path.join(repo_path, ".docker-generation.log.json")
        # with open(log_path, "w", encoding="utf-8") as f:
        #     json.dump(log_content, f, indent=2)
        # logger.info(f"Saved analysis log to {log_path}")

    def push_to_github(self, repo_path: str, token: str, commit_message: str = "Auto-generated Docker files"):
        g = Github(token)
        repo_name = os.path.basename(os.path.abspath(repo_path))
        remote_url = f"https://github.com/<your-org-or-user>/{repo_name}.git"

        repo = Repo.init(repo_path)
        repo.index.add(["Dockerfile.*", "docker-compose.yml", "README-Docker.md", ".dockerignore", ".docker-generation.log.json", ".github/workflows/docker-build.yml"])
        repo.index.commit(commit_message)

        origin = repo.create_remote("origin", remote_url)
        origin.push()
        logger.info(f"Successfully pushed Docker files to GitHub: {remote_url}")
    
    
    def get_port_framework(self, repo_path: str) -> str:
        """Get the default port for the framework used in the repository"""
        try:
            if repo_path:
                print(f"Analyzing repository at {repo_path}...")

            repo_path = Path(repo_path)
            if not repo_path.exists():
                return json.dumps({"error": f"Repository path '{repo_path}' does not exist."})

            backend_files = self.extract_key_files(repo_path)
            frontend_files = self.extract_frontend_files(repo_path)

            if not backend_files and not frontend_files:
                return json.dumps({"error": "No backend or frontend files found."})

            prompt = "You are a DevOps assistant. Analyze the following files and extract insights about:\n\n"

            if backend_files:
                prompt += ("If backend present:\n"
                        "1. Backend web framework\n"
                        "2. get the default port for this framework\n"
                        "3. Backend entry-point file\n"
                        "4. The name of its main dependency file\n"
                        "5. A list of system-level build packages and libraries required for dockerfile installation\n")

            if frontend_files:
                prompt += (
    "If frontend present:\n"
    "1. Frontend framework\n"
    "2. Default port for this framework\n"
    "3. Frontend entry-point file\n"
    "4. The name of its main dependency file\n"
    "5. Analyze the dependency file and list system-level build packages required.\n"
    "- If any `@types/` packages or a `tsconfig.json` file are present, treat the project as using TypeScript.\n"
    "- Always include `typescript` as a required package if inferred.\n"
)


            prompt += "\nReturn valid clean JSON, include only existing sections (backend or frontend):\n"

            example_output = {}
            if backend_files:
                example_output["backend"] = {
                    "framework": "...",
                    "port": "...",
                    "entry_point": "...",
                    "dependency_file": "...",
                    "system_packages": "..."
                }
            if frontend_files:
                example_output["frontend"] = {
                    "framework": "...",
                    "port": "...",
                    "entry_point": "...",
                    "dependency_file": "...",
                    "system_packages": "..."
                }

            prompt += json.dumps(example_output, indent=2)
            prompt += "\n\nFILES:\n"

            for fname, content in {**backend_files, **frontend_files}.items():
                prompt += f"\n--- {fname} ---\n{content}\n"

            response_text = self.run_llm(prompt)
            print(f"[DEBUG] Raw LLM response:\n{response_text[:500]}")  # Log preview

            if not response_text.strip():
                return json.dumps({"error": "LLM returned empty response"})

            # Try extracting JSON block
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.rfind("```")
                response_clean = response_text[start:end].strip()
            elif response_text.startswith("```"):
                start = response_text.find("```") + 3
                end = response_text.rfind("```")
                response_clean = response_text[start:end].strip()
            else:
                response_clean = response_text.strip()

            if not response_clean:
                return json.dumps({"error": "No JSON block found in LLM response"})

            try:
                parsed = json.loads(response_clean)
            except json.JSONDecodeError as e:
                return json.dumps({"error": f"Failed to parse LLM JSON: {e}"})

            filtered = {k: v for k, v in parsed.items() if v and isinstance(v, dict)}
            print(f"Filtered response: {filtered}")
            
            framework_port_analysis_path = os.path.join(repo_path, "framework_port_analysis.json")
            if not os.path.exists(framework_port_analysis_path):
                with open(framework_port_analysis_path, "w", encoding="utf-8") as f:
                    f.write(json.dumps(filtered, indent=2))
                logger.info(f"Generated framework_port_analysis.json at {framework_port_analysis_path}")


            return json.dumps(filtered, indent=2)

        except Exception as e:
            return json.dumps({"error": str(e)})

            
        
        


