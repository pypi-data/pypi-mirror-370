
import re
import requests
import json
import logging
import os
import yaml  # Requires PyYAML
import shutil

from requests.auth import HTTPBasicAuth
from typing import List, Union
from .docker_generation import DockerGenerationAgent
from .base_agent import BaseAgent

# Set up logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class GrapheneAgent(BaseAgent):
    """Agent for analyzing GitHub repositories for insights and patterns"""
    
    
    def __init__(self):
       super().__init__() 
       self.docker_generation_agent = DockerGenerationAgent()
       
    
    def _save_monitoring_config_report(self, repo_path: str, report: dict, filename: str = "monitoring_config.json"):
        """Save Prometheus/Grafana monitoring configuration as a JSON file"""
        if repo_path and os.path.isdir(repo_path):
            report_path = os.path.join(repo_path, filename)
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Saved monitoring configuration to {report_path}")
            except Exception as e:
                logger.warning(f"Failed to save monitoring configuration: {str(e)}")
                
                
    def handle_repo_analysis(self, repo_path: str):
        try:
            # Check if Docker and Docker Compose files exist
            dockerfile_exists = os.path.exists(os.path.join(repo_path, "Dockerfile"))
            compose_exists = os.path.exists(os.path.join(repo_path, "docker-compose.yml"))

            # If not found, run analysis to generate them
            if not (dockerfile_exists and compose_exists):
                logging.info("Docker or Compose file missing. Triggering auto-analysis.")
                self.docker_generation_agent.analyze(
                    repo_path=repo_path,
                   
                )
            else:
                logging.info("Docker and Compose files exist. Skipping auto-analysis.")

            # Always get framework and port mapping once Docker setup is ensured
            framework_analysis = self.docker_generation_agent.get_port_framework(repo_path)
            logging.info(f"Framework/Port Analysis: {framework_analysis}")


            return framework_analysis

        except Exception as e:
            logging.error(f"Error in repo analysis: {str(e)}")
            return {"error": str(e)}

    
    def analyze(self, repo_path: str, max_file_size: int = 10485760,
            include_patterns: Union[List[str], str] = None,
            exclude_patterns: Union[List[str], str] = None,
            output: str = None) -> str:
        """
        Analyze GitHub repositories for insights and patterns including framework port analysis.
        """
        try:
            # Path to framework port analysis file
            framework_path = os.path.join(repo_path, "framework_port_analysis.json")

            if os.path.exists(framework_path):
                # Load existing framework analysis
                with open(framework_path, "r", encoding="utf-8") as f:
                    framework_analysis = json.load(f)
                logger.info("Loaded existing framework_port_analysis.json")
            else:
                # Generate framework analysis if file doesn't exist
                framework_analysis = self.handle_repo_analysis(repo_path)  # You must define this method
                
                
            
            data=self.copy_and_check_monitoring_role( repo_path, framework_analysis)
            playbook_path = data.get("playbook_path")
            
            with open(playbook_path, "r") as f:
                playbook_data = yaml.safe_load(f) or []

            

            with open(playbook_path, "w") as f:
                yaml.dump(playbook_data, f, default_flow_style=False)
            logger.info("Playbook updated with monitoring role.")

                


            # Use framework_analysis in prompt if needed
            prompt = f"""
            An Ansible playbook was generated based on the framework and port analysis of the repository.

            ### Framework & Port Analysis:
            {json.dumps(framework_analysis, indent=2)}

            ### Generated Playbook Configuration:
            {playbook_data}

            Please analyze the playbook configuration with the following objectives:

            1. Review the use of Ansible roles (e.g., monitoring, backend, frontend, database).
            2. Identify missing roles or misconfigurations in the deployment strategy.
            3. Suggest improvements for scalability, maintainability, and best practices in deployment.
            4. Recommend structure improvements, such as using templates, handlers, or separating environment-specific logic.

            **Goal:** Ensure the deployment is modular, reusable, and production-ready by using well-defined roles aligned with modern DevOps practices.
            """




            response_text = self.run_llm(prompt)
            return response_text

        except Exception as e:
            return f"Error analyzing repository: {str(e)}"

    def copy_and_check_monitoring_role(self, repo_path, framework_analysis: dict):
        """
        Copy the monitoring role folder into the ansible folder in the repo,
        check for port conflicts using framework_analysis, and modify the role vars accordingly.
        Also adds the monitoring role to the playbook.yml file.

        Returns:
            dict: {
                "roles": List of role names found in roles folder,
                "playbook_path": Path to playbook.yml
            }
        """
        try:
            # Determine used ports from analysis
            used_ports = set()
            for entry in framework_analysis.get("services", []):
                port = entry.get("port")
                if port:
                    used_ports.add(int(port))

            # Default desired Grafana port
            desired_port = 3001
            while desired_port in used_ports:
                desired_port += 1

            # Paths
            base_dir = os.path.dirname(__file__)  # This is the directory of the current Python file
            role_src_path = os.path.join(base_dir, "mointoring", "roles", "monitoring")
            ansible_folder = os.path.join(repo_path, "ansible")
            roles_folder = os.path.join(ansible_folder, "roles")
            roles_dest_path = os.path.join(roles_folder, "monitoring")
            playbook_path = os.path.join(ansible_folder, "main.yml")

            # Copy monitoring role
            if not os.path.exists(roles_dest_path):
                shutil.copytree(role_src_path, roles_dest_path)
                logger.info("Copied monitoring role to repo.")
            else:
                logger.info("Monitoring role already exists. Skipping copy.")

            # Write vars file
            vars_data = {
                "grafana_url": f"http://localhost:{desired_port}",
                "domain": "localhost",
                "http_port": desired_port
            }
            
         
            with open(playbook_path, "r") as f:
                playbook_data = yaml.safe_load(f) or []

            

            with open(playbook_path, "w") as f:
                yaml.dump(playbook_data, f, default_flow_style=False)
            logger.info("Playbook updated with monitoring role.")

            # List role names in the roles folder
            if os.path.exists(roles_folder):
                role_names = [
                    name for name in os.listdir(roles_folder)
                    if os.path.isdir(os.path.join(roles_folder, name))
                ]
            else:
                role_names = []
               


                
            prompt = f"""
    The following is an Ansible playbook (`playbook.yml`) for deploying infrastructure and services.
                        Here is the framework and port analysis:
                        {json.dumps(framework_analysis, indent=2)}
                        make sure to use the correct port for Grafana and there not conflict between the service port and grafana port
                        otherwise choose different {desired_port}.

                    ---

             Your tasks:
            1. Add a `monitoring` role to the second play (that deploys to `new_ec2_instance`).
            2. Ensure there are no port conflicts using the following framework + port analysis.

            3. Inject necessary variables under `vars` for this role:
            - `grafana_url: "http://localhost:<desired_port>"`
            - `http_port: {desired_port}`
            - `domain: localhost`
            4. Output ONLY a clean, valid YAML playbook file — do NOT include Markdown code fences like ```yaml.


            Here is the current playbook:
           
            {playbook_data}
            Only return valid YAML content, no explanations or formatting.

                            
                    """

            updated_playbook = self.run_llm(prompt).strip()

            # Step 6: Overwrite the playbook with LLM-edited content
            with open(playbook_path, "w") as f:
                f.write(updated_playbook + "\n")
            logger.info("Updated playbook.yml with monitoring role via LLM.")

            # Step 7: List all roles
            role_names = [
                name for name in os.listdir(roles_folder)
                if os.path.isdir(os.path.join(roles_folder, name))
            ] if os.path.exists(roles_folder) else []

            return {
                "roles": role_names,
                "playbook_path": playbook_path
            }

        except Exception as e:
            logger.exception("Error updating playbook with monitoring role")
            return {
                "roles": [],
                "playbook_path": None,
                "error": str(e)
            }

        
