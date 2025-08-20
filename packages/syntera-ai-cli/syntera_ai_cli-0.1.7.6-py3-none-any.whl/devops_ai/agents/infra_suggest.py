import shutil
from typing import Dict, Any, List, Union, Optional, Tuple
from devops_ai.agents.base_agent import BaseAgent
import os
import json
import logging
import getpass
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import uuid
import yaml
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.output_parsers import RetryOutputParser
from tempfile import TemporaryDirectory
from langchain_community.agent_toolkits import FileManagementToolkit
from pydantic import BaseModel
from langchain_community.agent_toolkits import JsonToolkit, create_json_agent
from langchain_community.tools.json.tool import JsonSpec
from pprint import pprint
from langchain.output_parsers import PydanticOutputParser



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class Finalres(BaseModel):
    modules: List[str]
 
class InfraSuggestAgent(BaseAgent):
    """Agent for providing infrastructure recommendations including AWS machine types and IAC generation"""
    
    def __init__(self):
        super().__init__()
        self.aws_credentials = None
        # Validate OpenAI API key on initialization
        # self._validate_api_credentials()
        
    def parse_tree_string_to_dict(self,tree_str: str) -> Dict[str, dict]:
        """
        Converts a visual directory tree string (like from `tree`) into a dictionary
        with relative file paths as keys for easier parsing.

        Example input line:
            "│   ├── app.py" or "└── frontend/index.html"

        Returns:
            Dict[str, dict] where keys are relative file paths.
        """
        file_paths = {}
        current_path = []

        for line in tree_str.splitlines():
            stripped = line.strip("│├└─ ")
            if not stripped:
                continue

            # Calculate depth from indentation (each level is approx 4 chars)
            depth = (len(line) - len(line.lstrip())) // 4

            # Truncate path stack to current depth
            current_path = current_path[:depth]
            current_path.append(stripped)

            # If it's a file (contains a dot and not ending with '/'), add it
            if "." in stripped and not stripped.endswith("/"):
                rel_path = "/".join(current_path)
                file_paths[rel_path] = {}

        return file_paths

    

    
    def _analyze_aws_instance_requirements(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze component requirements and recommend optimal AWS EC2 instance
        with enhanced error handling and tier-based recommendations
        """
        
        # Define tier mappings for quick fallback
        TIER_MAPPINGS = {
    # 'basic': {
    #     'instance_type': 't3.micro',
    #     'cpu': '1 vCPU',
    #     'memory': '1 GB',
    #     'storage': 'gp3 - 20 GB',
    #     'cost_range': '$8-15/month (instance) + $2-4/month (storage)'
    # },
    't3.medium': {
        'instance_type': 't3.medium',
        'cpu': '2 vCPU',
        'memory': '4 GB',
        'storage': 'gp3 - 50 GB',
        'cost_range': '$20-25/month (instance) + $4-5/month (storage)'
    },
    # 't3.xlarge': {
    #     'instance_type': 't3.xlarge',
    #     'cpu': '4 vCPU',
    #     'memory': '16 GB',
    #     'storage': 'gp3 - 100 GB',
    #     'cost_range': '$70-80/month (instance) + $10/month (storage)'
    # },
    # 'balanced': {
    #     'instance_type': 'm5.large',
    #     'cpu': '2 vCPU',
    #     'memory': '8 GB',
    #     'storage': 'gp3 - 100 GB',
    #     'cost_range': '$70-90/month (instance) + $10-15/month (storage)'
    # },
    # 'compute': {
    #     'instance_type': 'c5.large',
    #     'cpu': '2 vCPU',
    #     'memory': '4 GB',
    #     'storage': 'gp3 - 50 GB',
    #     'cost_range': '$85-100/month (instance) + $5-8/month (storage)'
    # },
    # 'memory': {
    #     'instance_type': 'r5.large',
    #     'cpu': '2 vCPU',
    #     'memory': '16 GB',
    #     'storage': 'gp3 - 200 GB',
    #     'cost_range': '$125-150/month (instance) + $20-25/month (storage)'
    # }
}

        # Storage type recommendations
        STORAGE_TYPES = {
            'gp3': 'General Purpose SSD - Balanced price/performance',
            # 'gp2': 'General Purpose SSD - Legacy option',
            # 'io1': 'Provisioned IOPS SSD - High performance',
            # 'io2': 'Provisioned IOPS SSD - Latest high performance',
            # 'st1': 'Throughput Optimized HDD - Big data workloads',
            # 'sc1': 'Cold HDD - Infrequent access',
            # 'instance_store': 'Temporary high-performance storage'
        }
        
        # Enhanced response schema
        aws_schema = [
            ResponseSchema(name="instance_type", description="Recommended EC2 instance type (t3.medium)"),
            ResponseSchema(name="tier", description="Instance tier category (t3.medium)"),
            ResponseSchema(name="reasoning", description="Detailed explanation for the recommendation based on workload requirements"),
            ResponseSchema(name="cost_estimate", description="Estimated monthly cost breakdown for instance and storage"),
            ResponseSchema(name="storage_recommendation", description="Detailed storage configuration with type, size, and performance"),
            ResponseSchema(name="alternative_options", description="List of 2-3 alternative instance types with brief pros/cons"),
        ]
        
        parser = StructuredOutputParser.from_response_schemas(aws_schema)
        retry_parser = RetryOutputParser.from_llm(parser=parser, llm=self.llm)
        
        # Extract component details with defaults
        component_name = component.get('component', 'Unknown Component')
        description = component.get('description', 'No description provided')
        cpu_cores = component.get('cpu_cores', 'Not specified')
        memory_gb = component.get('memory_gb', 'Not specified')
        storage = component.get('storage', 'Not specified')
        storage_type = component.get('storage_type', 'Not specified')
        iops_requirements = component.get('iops_requirements', 'Not specified')
        networking = component.get('networking', 'Standard')
        workload_type = component.get('workload_type', 'General purpose')
        
        # Determine tier based on requirements
        predicted_tier = self._determine_instance_tier(cpu_cores, memory_gb, component_name)
        storage_recommendation = self._determine_storage_type(storage, storage_type, workload_type)
        
        prompt = f"""
        You are an AWS Solutions Architect with expertise in EC2 instance selection and EBS storage optimization. 
        Analyze the following component requirements and provide a comprehensive recommendation.
        and use TIER_MAPPINGS:{TIER_MAPPINGS} to determine the best instance type and storage configuration
        and STORAGE_TYPES:{STORAGE_TYPES} .

        === COMPONENT REQUIREMENTS ===
        Component Name: {component_name}
        Description: {description}
        Workload Type: {workload_type}
        
        === TECHNICAL SPECIFICATIONS ===
        CPU Cores Required: {cpu_cores}
        Memory Required: {memory_gb} GB
        Storage Capacity: {storage}
        Storage Type Preference: {storage_type}
        IOPS Requirements: {iops_requirements}
        Network Performance: {networking}
        
        === ANALYSIS CONTEXT ===
        Predicted Tier: {predicted_tier}
        Storage Recommendation: {storage_recommendation}
        
        === INSTRUCTIONS ===
        1. SELECT INSTANCE TYPE: Choose the most cost-effective instance that meets requirements from the TIER_MAPPINGS.
        2. TIER CLASSIFICATION: Use one of: basic,t3.medium,
        3. STORAGE ANALYSIS: Recommend EBS type (gp3, gp2, io1, io2, st1, sc1) with size and IOPS
        4. COST ESTIMATION: Provide separate costs for instance and storage (US East-1 pricing)
        
        
        === STORAGE DECISION MATRIX ===
        - gp3: Best for most workloads (3,000 IOPS baseline, cost-effective)
       
        
        === INSTANCE SELECTION GUIDELINES ===
        - t3/t4g: Burstable CPU for variable workloads
        - m5/m6i: Balanced compute for general applications
        - c5/c6i: CPU-intensive applications
        - r5/r6i: Memory-intensive applications
        - x1e/z1d: High-performance specialized workloads
        
        === RESPONSE FORMAT ===
        {parser.get_format_instructions()}
        
        Focus on practical, production-ready recommendations with clear cost justifications.
        """
        
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Analyzing AWS requirements for {component_name} (attempt {attempt + 1})")
                
                # Get LLM response
                response_text = self.run_llm(prompt)
                
                # Parse response
                parsed_result = retry_parser.parse_with_prompt(response_text, prompt)
                print(f"parsed_result from aws analysis:{parsed_result}")

                
                # Validate and enhance the response
                validated_result = self._validate_aws_response(parsed_result, predicted_tier)
                
                logger.info(f"Successfully analyzed AWS requirements for {component_name}")
                return validated_result
                
            except Exception as parse_err:
                logger.warning(f"AWS analysis attempt {attempt + 1} failed: {parse_err}")
                
                

    def _determine_instance_tier(self, cpu_cores: Any, memory_gb: Any, component_name: str) -> str:
        """Determine the appropriate instance tier based on requirements"""
        
        try:
            cpu = int(cpu_cores) if cpu_cores != 'Not specified' else 1
            memory = int(memory_gb) if memory_gb != 'Not specified' else 1
        except (ValueError, TypeError):
            cpu, memory = 1, 1
        
        # Check component name for hints
        component_lower = component_name.lower()
        
        # High performance indicators
        if any(keyword in component_lower for keyword in ['database', 'cache', 'redis', 'elasticsearch']):
            if memory > 32:
                return 'high_performance'
            elif memory > 16:
                return 'memory'
        
        # Compute intensive indicators
        if any(keyword in component_lower for keyword in ['processing', 'compute', 'batch', 'ml', 'ai']):
            if cpu > 8:
                return 'high_performance'
            elif cpu > 4:
                return 'compute'
        
        # Standard tier determination logic
        # if cpu <= 1 and memory <= 2:
        #     return 'basic'
        if cpu <= 4 and memory <= 16:
            return 't3.medium'
        # elif cpu > 4 and memory <= 32:
        #     return 'compute'
        # elif memory > 32:
        #     return 'memory'
        # else:
        #     return 'high_performance'

    def _determine_storage_type(self, storage: Any, storage_type: str, workload_type: str) -> str:
        """Determine optimal storage type based on requirements"""
        
        try:
            storage_size = int(storage.replace('GB', '').replace('TB', '000').strip()) if isinstance(storage, str) else 100
        except (ValueError, AttributeError):
            storage_size = 100
        
        workload_lower = workload_type.lower()
        
        # High IOPS requirements
        if any(keyword in workload_lower for keyword in ['database', 'oltp', 'high performance']):
            return 'io2' if storage_size > 1000 else 'io1'
        
        # Big data workloads
        if any(keyword in workload_lower for keyword in ['big data', 'analytics', 'data warehouse']):
            return 'st1'
        
        # Cold storage
        if any(keyword in workload_lower for keyword in ['backup', 'archive', 'cold']):
            return 'sc1'
        
        # Default to gp3 for most workloads
        return 'gp3'

    def _validate_aws_response(self, response: Dict[str, Any], predicted_tier: str) -> Dict[str, Any]:
        """Validate and enhance the AWS response"""
        
        # Ensure required fields exist
        required_fields = ['instance_type', 'reasoning', 'cost_estimate', 'storage_recommendation']
        
        for field in required_fields:
            if field not in response or not response[field]:
                logger.warning(f"Missing or empty field: {field}")
                if field == 'storage_recommendation':
                    response[field] = {
                        'type': 'gp3',
                        'size': '100 GB',
                        'iops': '3000',
                        'throughput': '125 MB/s'
                    }
                else:
                    response[field] = f"Not specified for {field}"
        
        # Add tier if missing
        if 'tier' not in response:
            response['tier'] = predicted_tier
        
        # Ensure storage_recommendation is properly formatted
        if not isinstance(response.get('storage_recommendation'), dict):
            response['storage_recommendation'] = {
                'type': 'gp3',
                'size': '100 GB',
                'iops': '3000',
                'throughput': '125 MB/s',
                'cost_per_month': '$10-15'
            }
        
        return response

    def _create_simplified_prompt(self, component: Dict[str, Any], parser) -> str:
        """Create a simplified prompt for retry attempts"""
        
        return f"""
        AWS EC2 + Storage recommendation for: {component.get('component', 'Application')}
        
        Requirements:
        - CPU: {component.get('cpu_cores', 1)} cores
        - Memory: {component.get('memory_gb', 1)} GB
        - Storage: {component.get('storage', '100 GB')}
        - Workload: {component.get('workload_type', 'General purpose')}
        
        Provide:
        1. EC2 instance type (e.g., t3.medium)
        2. EBS storage type and size (e.g., gp3, 100 GB)
        3. Monthly cost estimate
        4. Brief reasoning
        
        Response format:
        {parser.get_format_instructions()}
        """

    # def _create_fallback_response(self, tier: str, tier_mappings: Dict[str, Any]) -> Dict[str, Any]:
    #     """Create a fallback response when all analysis attempts fail"""
        
    #     fallback_tier = tier_mappings.get(tier, tier_mappings['basic'])
        
    #     return {
    #         "instance_type": fallback_tier['instance_type'],
    #         "tier": tier,
    #         "reasoning": f"Fallback recommendation based on {tier} tier requirements. This is a safe default that should handle most {tier} workloads. Consider manual review for optimization.",
    #         "cost_estimate": fallback_tier['cost_range'],
    #         "performance_characteristics": {
    #             "cpu": fallback_tier['cpu'],
    #             "memory": fallback_tier['memory'],
    #             "network": "Up to 5 Gbps" if tier == 'basic' else "Up to 10 Gbps",
    #             "storage": "EBS optimized available"
    #         },
    #         "storage_recommendation": {
    #             "type": "gp3",
    #             "size": fallback_tier['storage'].split(' - ')[1],
    #             "iops": "3000 (baseline)" if 'gp3' in fallback_tier['storage'] else "16000+",
    #             "throughput": "125 MB/s",
    #             "cost_per_month": fallback_tier['cost_range'].split(' + ')[1] if ' + ' in fallback_tier['cost_range'] else "$10-15/month"
    #         },
    #         "alternative_options": [
    #             f"Scale up to {tier}_plus for better performance",
    #             "Consider Reserved Instances for 30-60% cost savings",
    #             "Evaluate Spot Instances for non-critical workloads"
    #         ],
    #     }


    
    def analyze(
    self,
    query: str = "",
    repo_path: str = None,
    generate_iac: bool = False,
    deploy: bool = False,
    iac_format: str = "ansible"
) -> str:
        """
        Get infrastructure recommendations based on repository context or user query.
        Optionally generate Infrastructure as Code (IAC) and deploy to AWS.

        Args:
            query: Optional natural language input for infrastructure suggestions
            repo_path: Path to local git repository for contextual analysis
            generate_iac: Whether to generate IAC templates (CloudFormation or Ansible)
            deploy: Whether to deploy the infrastructure to AWS
            iac_format: Format of IAC to generate ("cloudformation" or "ansible")

        Returns:
            str: Infrastructure recommendations in structured format
        """
        try:
            # Step 1: Extract repository context if provided
            repo_context = ""
            repo_summary = {}

            if repo_path:
               
                repo_data = self.analyze_repository(repo_path)
                tree = repo_data.get("tree")

                if isinstance(tree, str):
                    try:
                        tree = self.parse_tree_string_to_dict(tree)
                        repo_data["tree"] = tree  # 👈 update back into the repo_data dict
                    except json.JSONDecodeError:
                        raise ValueError("Expected 'tree' to be a dict but got invalid JSON string.")

                print(f"Repository data tree type after parsing: {type(tree)}, {len(tree)} items")
                logging.info(f"Repository data tree type after parsing: {type(tree)}, {len(tree)} items")

                detected_services = self._detect_services_from_repo(repo_data, tree)
                print(f"Detected services: {detected_services}")
                
                

                repo_summary = {
                    "structure": repo_data.get("tree"),
                    "key_files": self._extract_key_file_contents(repo_path),
                    "services": detected_services
                }

                repo_context = self._format_repo_context_for_prompt(repo_summary)

                # except Exception as e:
                #     logger.warning(f"Failed to extract repository context: {str(e)}")

            # Step 2: Define the expected response schema
            infra_schema = [
                ResponseSchema(name="architecture_overview", description="High-level architecture description"),
                ResponseSchema(name="infrastructure_recommendations", description="List of infrastructure recommendations for each detected service/component. Each item must be a dictionary.")
                
            ]
            # Base parser
            infra_parser = StructuredOutputParser.from_response_schemas(infra_schema)

            # Wrapped parser with retry capability
            
            # Step 3: Build the prompt
            prompt = f"""
                You are an expert DevOps architect. Your goal is to recommend a robust cloud infrastructure setup based on the user's repository and application structure.

                === CONTEXT ===
                {repo_context}

                User Query: {query}

                === TASK ===
                For each detected service/component, provide detailed infrastructure recommendations in the format below. Each recommendation must include:

                - component: Name of the component (e.g. backend, frontend)
                - description: Brief description of its function and workload
              
                - storage: Estimated storage size in GB (e.g. 50 GB)
                - storage_type: Preferred EBS type (e.g. gp3, io2)
                - iops_requirements: Estimated IOPS (e.g. 3000)
                - networking: Network performance level (e.g. standard, high)
                - availability_zones: Number or names of AZs to use (e.g. 2, "eu-west-1a,eu-west-1b")
                - workload_type: One of [general purpose, compute optimized, memory optimized, high throughput, latency sensitive]

                === FORMAT ===
                {infra_parser.get_format_instructions()}

                Ensure all fields are filled meaningfully. Avoid generic values like "not specified". If a value must be estimated, use the application context.
                """


            logger.info("Invoking LLM for infrastructure recommendation...")

            # Step 4: Call LLM with retry
   
                
            response_text = self.run_llm(prompt)
            retry_parser = RetryOutputParser.from_llm(parser=infra_parser, llm=self.llm)
            try:
                json_response = retry_parser.parse_with_prompt(response_text, prompt)
                print(f"📦 Type of json response : {type(json_response)}")

                recommendations = json_response.get("infrastructure_recommendations")
                
                if isinstance(recommendations, str):
                    recommendations = json.loads(recommendations)
                    print(f"📦 Type of recommendations: {type(recommendations)}")
                    json_response["infrastructure_recommendations"] = recommendations

            except Exception as e:
                # Retry manually if error is recoverable
                print("🔁 Retrying LLM call due to post-parsing failure...")
                response_text = self.run_llm(prompt)
                json_response = retry_parser.parse_with_prompt(response_text, prompt)

            # Explicit validation before normalizing
           

            # Try to parse if it's a string that might be JSON
            # if isinstance(recommendations, str):
            #     print(f"📦 Type of recommendations: {type(recommendations)}")
            #     try:
            #         recommendations = json.loads(recommendations)
            #         print("✅ Successfully parsed string into JSON.")

            #         # Recheck after parsing
            #         if not isinstance(recommendations, list) or not all(isinstance(r, dict) for r in recommendations):
            #             raise ValueError("Parsed JSON is still not a valid list of dictionaries.")
            #     except json.JSONDecodeError as e:
            #         print(f"❌ Failed to parse JSON string: {e}")
            #         raise ValueError("Could not parse recommendations from string JSON.") from e
            # else:
            #     raise ValueError("Invalid recommendations format. Expected a list of dictionaries.")

                        
                
            # Step 6: Analyze EC2 instance type for each component
            for comp in json_response["infrastructure_recommendations"]:
                instance_analysis = self._analyze_aws_instance_requirements(comp)
                comp["aws_ec2_instance_type"] = instance_analysis["instance_type"]
                comp["instance_analysis"] = instance_analysis

            # Step 7: Save infrastructure report
            self._save_infra_recommendation_report(repo_path, json_response)

            # Step 8: Generate IAC
            iac_output = ""
            if generate_iac:
                try:
                    if iac_format.lower() == "ansible":
                        iac_templates = self._generate_ansible_playbooks(json_response,repo_path)
                        self._save_ansible_playbooks(repo_path, iac_templates)
                        iac_output = f"\n\n=== INFRASTRUCTURE AS CODE GENERATED ===\nAnsible playbooks saved to {repo_path}/ansible/"
                    else:
                        iac_templates = self._generate_cloudformation_templates(json_response)
                        self._save_cloudformation_templates(repo_path, iac_templates)
                        iac_output = f"\n\n=== INFRASTRUCTURE AS CODE GENERATED ===\nCloudFormation templates saved to {repo_path}/cloudformation/"
                except Exception as e:
                    logger.error(f"Error generating IAC: {str(e)}", exc_info=True)
                    iac_output = f"\n\nError generating Infrastructure as Code: {str(e)}"

            # Step 9: Deployment
            deployment_output = ""
            if deploy:
                if not self.aws_credentials:
                    self._collect_aws_credentials()

                if self.aws_credentials:
                    try:
                        if iac_format.lower() == "ansible":
                            deployment_result = self._deploy_with_ansible(repo_path, json_response)
                        else:
                            deployment_result = self._deploy_to_aws(repo_path, json_response)
                        deployment_output = f"\n\n=== DEPLOYMENT STATUS ===\n{deployment_result}"
                    except Exception as e:
                        logger.error(f"Deployment error: {str(e)}", exc_info=True)
                        deployment_output = f"\n\nError deploying to AWS: {str(e)}"
                else:
                    deployment_output = "\n\nAWS deployment skipped: No credentials provided."

            # Step 10: Final output
            return self._format_output(json_response) + iac_output + deployment_output

        except Exception as e:
            logger.error(f"Error generating infrastructure suggestion: {str(e)}", exc_info=True)
            return f"Error generating infrastructure suggestions: {str(e)}"
        
        
    def _normalize_component_fields(self, component: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required component fields exist."""
        defaults = {
            "component": "Unknown Component",
            "description": "No description provided",
            "storage": "Not specified",
            "storage_type": "Not specified",
            "iops_requirements": "Not specified",
            "networking": "Standard",
            "availability_zones": "Not specified",
            "workload_type": "General purpose"
        }
        for key, value in defaults.items():
            component.setdefault(key, value)
        return component



    def _extract_key_file_contents(self, repo_path: str, max_files: int = 5, max_chars: int = 2000) -> Dict[str, str]:
        """Extract content from key files for LLM context"""
        key_files = []
        for root, _, files in os.walk(repo_path):
            for fname in files:
                if fname.lower() in {"package.json", "requirements.txt", "Dockerfile", "docker-compose.yml",
                                     "pom.xml", "build.gradle", "setup.py", "Gemfile", ".gitignore"}:
                    key_files.append(os.path.relpath(os.path.join(root, fname), repo_path))

        file_contents = {}
        for fname in key_files[:max_files]:
            fpath = os.path.join(repo_path, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()[:max_chars]
                        file_contents[fname] = content
                except Exception as e:
                    file_contents[fname] = f"[ERROR reading file: {e}]"
        return file_contents

    def _detect_services_from_repo(self, repo_data: dict, tree: dict) -> List[Dict[str, Any]]:
        """Try to detect services/components from repository structure with detailed information"""
        services = []
        service_names = set()
        
        
        # 1. Detect services from Dockerfiles
        for path in tree.keys():
            if "dockerfile" in path.lower() or path.lower().endswith(".dockerfile") or path.lower().startswith("dockerfile"):
                print(f"Found Dockerfile at: {path}")
                # Extract service name from Dockerfile.service_name pattern
                parts = os.path.basename(path).split('.')
                if len(parts) > 1 and parts[0].lower() == "dockerfile":
                    service_name = parts[1].lower()
                    if service_name not in service_names:
                        service_names.add(service_name)
                        services.append({
                            "component": service_name,
                            "description": f"Service identified from {path}",
                            "source": "dockerfile"
                        })
        
        # 2. Detect services from docker-compose.yml
        docker_compose_paths = [p for p in tree.keys() if p.lower().endswith("docker-compose.yml")]
        for dc_path in docker_compose_paths:
            try:
                # Try to read docker-compose.yml content from repo_data or file system
                dc_content = None
                if "content" in repo_data and dc_path in repo_data["content"]:
                    dc_content = repo_data["content"][dc_path]
                else:
                    # Attempt to read from file system if available
                    full_path = os.path.join(os.path.dirname(dc_path), "docker-compose.yml")
                    if os.path.exists(full_path):
                        with open(full_path, 'r') as f:
                            dc_content = f.read()
                
                if dc_content:
                    # Parse YAML content
                    try:
                        dc_yaml = yaml.safe_load(dc_content)
                        if dc_yaml and "services" in dc_yaml:
                            for svc_name, svc_config in dc_yaml["services"].items():
                                if svc_name not in service_names:
                                    service_names.add(svc_name)
                                    # Extract more details if available
                                    description = "Service defined in docker-compose.yml"
                                    if "image" in svc_config:
                                        description += f", using image {svc_config['image']}"
                                    
                                    services.append({
                                        "component": svc_name,
                                        "description": description,
                                        "source": "docker-compose"
                                    })
                    except Exception as e:
                        logger.warning(f"Error parsing docker-compose.yml: {str(e)}")
            except Exception as e:
                logger.warning(f"Error processing docker-compose file {dc_path}: {str(e)}")
        
        # 3. Detect services from common project structures
        service_dirs = set()
        service_keywords = ["api", "web", "service", "worker", "db", "database", "cache", "gateway", "auth", "frontend", "backend"]
        
        for path in tree.keys():
            parts = path.split("/")
            if len(parts) > 1:
                # Check if first directory component is a service keyword
                if parts[0].lower() in service_keywords and parts[0] not in service_names:
                    service_dirs.add(parts[0])
        
        # Add services from directory structure
        for svc_dir in service_dirs:
            if svc_dir not in service_names:
                service_names.add(svc_dir)
                services.append({
                    "component": svc_dir,
                    "description": "Service identified from directory structure",
                    "source": "directory"
                })
        
        # 4. If no services detected, add default components based on repository type
        if not services:
            # Check for common application types
            has_frontend = any("index.html" in p.lower() for p in tree.keys())
            has_backend = any(p.lower().endswith((".py", ".js", ".java", ".go")) for p in tree.keys())
            
            if has_frontend:
                services.append({
                    "component": "frontend",
                    "description": "Frontend web application detected from repository structure",
                    "source": "inferred"
                })
            
            if has_backend:
                services.append({
                    "component": "backend",
                    "description": "Backend application detected from repository structure",
                    "source": "inferred"
                })
            
            # If still no services detected, add a generic application component
            if not services:
                services.append({
                    "component": "application",
                    "description": "Generic application component",
                    "source": "default"
                })
        
        return services

    def _format_repo_context_for_prompt(self, repo_summary: dict) -> str:
        """Format repository data into a prompt-friendly string"""
        context = "\nRepository Context:\n"

        if "structure" in repo_summary:
            context += "\nDirectory Tree:\n"
            for path in repo_summary["structure"]:
                context += f"- {path}\n"

        if "key_files" in repo_summary:
            context += "\nKey Files Content:\n"
            for fname, content in repo_summary["key_files"].items():
                context += f"\n--- {fname} ---\n{content[:500]}...\n"

        if "services" in repo_summary and repo_summary["services"]:
            context += "\nDetected Services/Components:\n"
            for svc in repo_summary["services"]:
                component = svc.get("component", "Unknown")
                description = svc.get("description", "No description")
                source = svc.get("source", "Unknown")
                context += f"- {component}: {description} (Source: {source})\n"

        return context


    def _save_infra_recommendation_report(self, repo_path: str, report: dict):
        """Save infrastructure recommendation as JSON file"""
        if repo_path and os.path.isdir(repo_path):
            report_path = os.path.join(repo_path, "infrastructure_recommendation.json")
            try:
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2)
                logger.info(f"Saved infrastructure report to {report_path}")
            except Exception as e:
                logger.warning(f"Failed to save infrastructure report: {str(e)}")

    
    
    def _generate_fallback_response(self, error_message: str) -> str:
        """Generate a fallback response when LLM API call fails"""
        # Create a basic fallback response with error information
        fallback_json = {
            "architecture_overview": f"Unable to generate detailed recommendations due to API error: {error_message}. Using fallback recommendations.",
            "infrastructure_recommendations": [
                {
                    "component": "Web Application",
                    "description": "Basic web application service",
                    "aws_ec2_instance_type": "t3.medium",
                    "cpu_cores": "2",
                    "memory_gb": "4",
                    "storage": "20GB SSD",
                    "networking": "Public subnet with security group",
                    "availability_zones": "2",
                    "scaling": "Auto-scaling group with 2-4 instances"
                },
                {
                    "component": "Database",
                    "description": "Relational database for application data",
                    "aws_ec2_instance_type": "t3.large",
                    "cpu_cores": "2",
                    "memory_gb": "8",
                    "storage": "100GB SSD",
                    "networking": "Private subnet",
                    "availability_zones": "2",
                    "scaling": "Multi-AZ deployment"
                }
            ],
            # "resource_optimization": "Use reserved instances for predictable workloads. Implement auto-scaling for variable loads.",
            # "cost_saving_tips": "Consider using Spot instances for non-critical workloads. Implement lifecycle policies for EBS volumes.",
            # "security_best_practices": "Use security groups to restrict access. Enable encryption for data at rest and in transit.",
            # "deployment_pipeline_suggestions": "Implement CI/CD pipeline with AWS CodePipeline or GitHub Actions."
        }
        
        # Format and return the fallback response
        return self._format_output(fallback_json)

    def _format_output(self, result: dict) -> str:
        """Format final output for user readability"""
        output = ""

        output += "=== INFRASTRUCTURE RECOMMENDATION ===\n\n"
        output += "Architecture Overview:\n"
        output += result.get("architecture_overview", "") + "\n\n"

        output += "Infrastructure Components:\n"
        for comp in result.get("infrastructure_recommendations", []):
            output += f"- {comp['component']} ({comp['aws_ec2_instance_type']}):\n"
            output += f"  Description: {comp['description']}\n"
            output += f"  Storage: {comp['storage']}\n"
            output += f"  Networking: {comp['networking']}\n"
            

        return output
        
    def _generate_cloudformation_templates(self, infra_recommendations: Dict[str, Any]) -> Dict[str, str]:
        """Generate CloudFormation templates based on infrastructure recommendations using LLM"""
        templates = {}
        
        # Extract key information from recommendations
        components = infra_recommendations.get("infrastructure_recommendations", [])
        architecture_overview = infra_recommendations.get("architecture_overview", "")
        
        # Build prompt for LLM to generate CloudFormation template
        prompt = f"""Generate a complete AWS CloudFormation template based on the following infrastructure requirements.

Architecture Overview:
{architecture_overview}

Infrastructure Components:
"""

        # Add each component's details to the prompt
        for comp in components:
            prompt += f"""
- Component: {comp.get('component', 'Unknown')}
  Description: {comp.get('description', 'No description')}
  EC2 Instance Type: {comp.get('aws_ec2_instance_type',)}
  Storage: {comp.get('storage', 'Not specified')}
  Networking: {comp.get('networking', 'Not specified')}
  Availability Zones: {comp.get('availability_zones', 'Not specified')}
 
"""
        
        # Add instructions for generating the CloudFormation template
        prompt += """

Please generate a complete AWS CloudFormation template in JSON format that implements this infrastructure.
The template should include:
1. Appropriate VPC and networking resources
2. Security groups with proper ingress/egress rules
3. EC2 instances or Auto Scaling Groups as specified
4. Any necessary IAM roles and policies
5. Appropriate resource tagging
6. Outputs for important resource IDs

The template should follow AWS best practices and be optimized for security, reliability, and cost-efficiency.
Provide ONLY the CloudFormation template JSON without any explanations or markdown formatting.
"""

        logger.info("Invoking LLM to generate CloudFormation template...")
        try:
            # Invoke LLM to generate the CloudFormation template
            # response = self.llm.invoke(prompt)
            #template_text = response.content.strip()
            response_text = self.run_llm(prompt)
            template_text = response_text.strip()

            # Try to parse the response as JSON
            try:
                # Extract JSON if it's wrapped in code blocks
                if template_text.startswith("```") and template_text.endswith("```"):
                    # Extract content between code blocks
                    start_idx = template_text.find("\n") + 1
                    end_idx = template_text.rfind("```")
                    template_text = template_text[start_idx:end_idx].strip()
                
                # Validate the template is valid JSON
                json.loads(template_text)
                
                # Store the main template
                templates["main-stack.json"] = template_text
                
                # Generate component-specific templates if there are multiple components
                if len(components) > 1:
                    for idx, comp in enumerate(components):
                        component_name = comp["component"].replace(" ", "")
                        component_prompt = f"""Generate a CloudFormation template for just the {comp['component']} component with these specifications:
                        
- Description: {comp.get('description', 'No description')}
- EC2 Instance Type: {comp.get('aws_ec2_instance_type')}
- Storage: {comp.get('storage', 'Not specified')}
- Networking: {comp.get('networking', 'Not specified')}
- Availability Zones: {comp.get('availability_zones', 'Not specified')}


Provide ONLY the CloudFormation template JSON without any explanations or markdown formatting.
"""
                        
                        # Only generate component templates for the first few components to avoid excessive API calls
                        if idx < 3:  # Limit to 3 component-specific templates
                            component_template=self.run_llm(prompt).strip()  
                            # component_response = self.llm.invoke(component_prompt)
                            # component_template = component_response.content.strip()
                            
                            # Extract JSON if wrapped in code blocks
                            if component_template.startswith("```") and component_template.endswith("```"):
                                start_idx = component_template.find("\n") + 1
                                end_idx = component_template.rfind("```")
                                component_template = component_template[start_idx:end_idx].strip()
                            
                            # Validate and store component template
                            try:
                                json.loads(component_template)
                                templates[f"{component_name.lower()}-stack.json"] = component_template
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse component template for {component_name} as JSON")
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse CloudFormation template as JSON: {str(e)}")
                # Create a fallback template if parsing fails
                fallback_template = self._create_fallback_template(infra_recommendations)
                templates["main-stack.json"] = json.dumps(fallback_template, indent=2)
        
        except Exception as e:
            logger.error(f"Error generating CloudFormation template with LLM: {str(e)}")
            # Create a fallback template if LLM invocation fails
            # fallback_template = self._create_fallback_template(infra_recommendations)
            # templates["main-stack.json"] = json.dumps(fallback_template, indent=2)
        
        return templates
        
    # def _create_fallback_template(self, infra_recommendations: Dict[str, Any]) -> Dict[str, Any]:
    #     """Create a fallback CloudFormation template if LLM generation fails"""
    #     # Basic template structure
    #     template = {
    #         "AWSTemplateFormatVersion": "2010-09-09",
    #         "Description": "Fallback CloudFormation template generated from infrastructure recommendations",
    #         "Parameters": {
    #             "EnvironmentName": {
    #                 "Description": "Environment name (e.g., dev, test, prod)",
    #                 "Type": "String",
    #                 "Default": "dev"
    #             },
    #             "VpcCIDR": {
    #                 "Description": "CIDR block for the VPC",
    #                 "Type": "String",
    #                 "Default": "10.0.0.0/16"
    #             }
    #         },
    #         "Resources": {
    #             "VPC": {
    #                 "Type": "AWS::EC2::VPC",
    #                 "Properties": {
    #                     "CidrBlock": {"Ref": "VpcCIDR"},
    #                     "EnableDnsSupport": True,
    #                     "EnableDnsHostnames": True,
    #                     "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${EnvironmentName}-vpc"}}]
    #                 }
    #             },
    #             "PublicSubnet1": {
    #                 "Type": "AWS::EC2::Subnet",
    #                 "Properties": {
    #                     "VpcId": {"Ref": "VPC"},
    #                     "CidrBlock": {"Fn::Select": [0, {"Fn::Cidr": [{"Ref": "VpcCIDR"}, 4, 8]}]},
    #                     "AvailabilityZone": {"Fn::Select": [0, {"Fn::GetAZs": ""}]},
    #                     "Tags": [{"Key": "Name", "Value": {"Fn::Sub": "${EnvironmentName}-public-subnet-1"}}]
    #                 }
    #             }
    #         },
    #         "Outputs": {
    #             "VpcId": {
    #                 "Description": "VPC ID",
    #                 "Value": {"Ref": "VPC"},
    #                 "Export": {"Name": {"Fn::Sub": "${EnvironmentName}-VpcId"}}
    #             }
    #         }
    #     }
        
    #     # Add resources for each component in the recommendations
    #     for idx, comp in enumerate(infra_recommendations.get("infrastructure_recommendations", [])):
    #         component_name = comp["component"].replace(" ", "")
    #         instance_type = comp["aws_ec2_instance_type"]
            
    #         # Add security group for the component
    #         sg_name = f"{component_name}SecurityGroup"
    #         template["Resources"][sg_name] = {
    #             "Type": "AWS::EC2::SecurityGroup",
    #             "Properties": {
    #                 "GroupDescription": f"Security group for {comp['component']}",
    #                 "VpcId": {"Ref": "VPC"},
    #                 "SecurityGroupIngress": [
    #                     {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22, "CidrIp": "0.0.0.0/0"}
    #                 ],
    #                 "Tags": [{"Key": "Name", "Value": {"Fn::Sub": f"${{EnvironmentName}}-{component_name}-sg"}}]
    #             }
    #         }
            
    #         # Add EC2 instance or Auto Scaling Group based on scaling strategy
    #         if "auto" in comp.get("scaling", "").lower():
    #             # Create Launch Template
    #             lt_name = f"{component_name}LaunchTemplate"
    #             template["Resources"][lt_name] = {
    #                 "Type": "AWS::EC2::LaunchTemplate",
    #                 "Properties": {
    #                     "LaunchTemplateName": {"Fn::Sub": f"${{EnvironmentName}}-{component_name}-lt"},
    #                     "VersionDescription": "Initial version",
    #                     "LaunchTemplateData": {
    #                         "InstanceType": instance_type,
    #                         "SecurityGroupIds": [{"Ref": sg_name}],
    #                         "ImageId": "ami-0c55b159cbfafe1f0",
    #                         "UserData": {"Fn::Base64": {"Fn::Sub": f"#!/bin/bash\necho 'Setting up {comp['component']}'\n"}}
    #                     }
    #                 }
    #             }
                
    #             # Create Auto Scaling Group
    #             asg_name = f"{component_name}ASG"
    #             template["Resources"][asg_name] = {
    #                 "Type": "AWS::AutoScaling::AutoScalingGroup",
    #                 "Properties": {
    #                     "AutoScalingGroupName": {"Fn::Sub": f"${{EnvironmentName}}-{component_name}-asg"},
    #                     "LaunchTemplate": {
    #                         "LaunchTemplateId": {"Ref": lt_name},
    #                         "Version": {"Fn::GetAtt": [lt_name, "LatestVersionNumber"]}
    #                     },
    #                     "MinSize": 1,
    #                     "MaxSize": 3,
    #                     "DesiredCapacity": 2,
    #                     "VPCZoneIdentifier": [{"Ref": "PublicSubnet1"}],
    #                     "Tags": [{
    #                         "Key": "Name",
    #                         "Value": {"Fn::Sub": f"${{EnvironmentName}}-{component_name}"},
    #                         "PropagateAtLaunch": True
    #                     }]
    #                 }
    #             }
    #         else:
    #             # Create EC2 instance
    #             ec2_name = f"{component_name}Instance"
    #             template["Resources"][ec2_name] = {
    #                 "Type": "AWS::EC2::Instance",
    #                 "Properties": {
    #                     "InstanceType": instance_type,
    #                     "SecurityGroupIds": [{"Ref": sg_name}],
    #                     "SubnetId": {"Ref": "PublicSubnet1"},
    #                     "ImageId": "ami-0c55b159cbfafe1f0",
    #                     "Tags": [{"Key": "Name", "Value": {"Fn::Sub": f"${{EnvironmentName}}-{component_name}"}}]
    #                 }
    #             }
        
    #     return template
    
    def _save_cloudformation_templates(self, repo_path: str, templates: Dict[str, str]) -> None:
        """Save CloudFormation templates to the repository"""
        if not repo_path or not os.path.isdir(repo_path):
            logger.warning("No valid repository path provided for saving CloudFormation templates")
            return
            
        # Create cloudformation directory if it doesn't exist
        cf_dir = os.path.join(repo_path, "cloudformation")
        os.makedirs(cf_dir, exist_ok=True)
        
        # Save each template
        for template_name, content in templates.items():
            template_path = os.path.join(cf_dir, template_name)
            try:
                with open(template_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logger.info(f"Saved CloudFormation template to {template_path}")
            except Exception as e:
                logger.warning(f"Failed to save CloudFormation template {template_name}: {str(e)}")
    
    def _collect_aws_credentials(self) -> None:
        """Securely collect AWS credentials from the user"""
        print("\n=== AWS Credentials Required for Deployment ===")
        print("Please enter your AWS credentials. These will only be used for this deployment and won't be stored permanently.")
        print("Note: For security, your input will not be displayed as you type.\n")
        
        try:
            aws_access_key = getpass.getpass("AWS Access Key ID: ")
            aws_secret_key = getpass.getpass("AWS Secret Access Key: ")
            aws_region = input("AWS Region (e.g., us-east-1): ")
            
            # Validate credentials
            if not aws_access_key or not aws_secret_key or not aws_region:
                print("Error: All credential fields are required.")
                return
            
            # Store credentials temporarily
            self.aws_credentials = {
                "aws_access_key_id": aws_access_key,
                "aws_secret_access_key": aws_secret_key,
                "region_name": aws_region
            }
            
            # Verify credentials
            try:
                session = boto3.Session(
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                sts = session.client('sts')
                sts.get_caller_identity()
                print("AWS credentials verified successfully.")
            except Exception as e:
                print(f"Error verifying AWS credentials: {str(e)}")
                self.aws_credentials = None
                
        except KeyboardInterrupt:
            print("\nAWS credential collection cancelled.")
            self.aws_credentials = None
        except Exception as e:
            print(f"\nError collecting AWS credentials: {str(e)}")
            self.aws_credentials = None
    
    def _deploy_to_aws(self, repo_path: str, infra_recommendations: Dict[str, Any]) -> str:
        """Deploy infrastructure to AWS using CloudFormation"""
        if not self.aws_credentials:
            return "Error: AWS credentials not available. Please provide credentials first."
        
        # Create CloudFormation client
        try:
            cf_client = boto3.client(
                'cloudformation',
                aws_access_key_id=self.aws_credentials["aws_access_key_id"],
                aws_secret_access_key=self.aws_credentials["aws_secret_access_key"],
                region_name=self.aws_credentials["region_name"]
            )
            
            # Generate stack name
            stack_name = f"infra-{uuid.uuid4().hex[:8]}"
            
            # Get template path
            cf_dir = os.path.join(repo_path, "cloudformation")
            template_path = os.path.join(cf_dir, "main-stack.json")
            
            if not os.path.exists(template_path):
                # Generate templates if they don't exist
                templates = self._generate_cloudformation_templates(infra_recommendations)
                self._save_cloudformation_templates(repo_path, templates)
            
            # Read template content
            with open(template_path, "r") as f:
                template_body = f.read()
            
            # Create CloudFormation stack
            response = cf_client.create_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {
                        'ParameterKey': 'EnvironmentName',
                        'ParameterValue': 'dev'
                    }
                ],
                Capabilities=['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                OnFailure='ROLLBACK'
            )
            
            stack_id = response['StackId']
            return f"Deployment initiated successfully!\nStack Name: {stack_name}\nStack ID: {stack_id}\n\nYou can monitor the deployment status in the AWS CloudFormation console."
            
        except ClientError as e:
            logger.error(f"AWS CloudFormation error: {str(e)}", exc_info=True)
            return f"AWS CloudFormation error: {str(e)}"
        except NoCredentialsError:
            return "Error: AWS credentials not found or invalid."
        except Exception as e:
            logger.error(f"Deployment error: {str(e)}", exc_info=True)
            return f"Deployment error: {str(e)}"
        
    def get_jinja_docker_templates(self,repo_path):
        jinja_files = []
        for root, _, files in os.walk(repo_path):
            for filename in files:
                if filename.startswith("Dockerfile"):
                    new_filename = f"{filename}.j2"
                    jinja_files.append(os.path.join(root, new_filename))

                elif filename.startswith("docker-compose") and filename.endswith(".yml"):
                    new_filename = filename.replace(".yml", ".j2")
                    jinja_files.append(os.path.join(root, new_filename))

        return jinja_files
    
    def discover_required_modules(self, ansible_role_summary: str):
        parser = PydanticOutputParser(pydantic_object=Finalres)
        base_dir = os.path.dirname(__file__)  # This is the directory of the current Python file
        modules_path = os.path.join(base_dir, "aws", "all_modules.json")
        params_path = os.path.join(base_dir, "aws", "aws_modules_params.json")
        returns_path = os.path.join(base_dir, "aws", "aws_modules_returns.json")
        
        # Load your JSON data
        with open(modules_path) as f:
            data = json.load(f)
        with open(params_path) as f:
            data_params = json.load(f)
        with open(returns_path) as f:
            data_returns = json.load(f)
        
        # Convert list of modules to a dict with name as key
        data_dict = {entry["name"]: entry for entry in data}
        
        # Setup the spec and toolkit
        json_spec = JsonSpec(dict_=data_dict, max_value_length=4000)
        json_toolkit = JsonToolkit(spec=json_spec)
        
        def count_tokens_approx(text):
            return int(len(text) / 4)
        
        def extract_nested_structure(data_dict):
            """Recursively extract parameters/returns with their nested suboptions."""
            result = {}
            
            for key, value in data_dict.items():
                if isinstance(value, dict):
                    param_info = {
                        # "type": value.get("type", "unknown"),
                        # "required": value.get("required", False),
                        "description":value.get("description", "unknown")
                    
                    }
                    
                    # Check if this parameter has suboptions
                    if "suboptions" in value and value["suboptions"]:
                        param_info["suboptions"] = extract_nested_structure(value["suboptions"])
                    
                    result[key] = param_info
                
            return result
        
        def extract_nested_returns_structure(data_dict):
            """Recursively extract return values with their nested suboptions."""
            result = {}
            
            for key, value in data_dict.items():
                if isinstance(value, dict):
                    return_info = {
                        "type": value.get("type", "unknown"),
                    
                    }
                    
                    # Add additional return-specific fields if they exist
                    if "elements" in value:
                        return_info["elements"] = value["elements"]
                    if "sample" in value:
                        return_info["sample"] = value["sample"]
                    
                    # Check if this return value has suboptions
                    if "suboptions" in value and value["suboptions"]:
                        return_info["suboptions"] = extract_nested_returns_structure(value["suboptions"])
                    
                    result[key] = return_info
                
            return result
        
        json_agent_executor = create_json_agent(
            llm=self.llm, toolkit=json_toolkit, verbose=True, handle_parsing_errors=True
        )
        
        # Run the agent and count tokens
        # Step 1: Add JSON output format instruction to the prompt
        question = parser.get_format_instructions() + "\n" + ansible_role_summary
        
        # Step 2: Invoke agent
        response = json_agent_executor.invoke({"input": question})
        
        # Step 3: Parse output as Pydantic model
        parsed_output = parser.parse(response['output'])
        
        # Step 4: Access params and returns with full nested structure
        modules_with_params_and_returns = []
        for module_name in parsed_output.modules:
            # Extract parameters with nested suboptions
            module_params = data_params.get(module_name, {}).get("parameters", {})
            params_structure = extract_nested_structure(module_params)
            
            # Extract return values with nested suboptions
            module_returns = data_returns.get(module_name, {}).get("return_values", {})
            returns_structure = extract_nested_returns_structure(module_returns)
            
            modules_with_params_and_returns.append({
                "module": module_name,
                "params": params_structure,
                "returns": returns_structure
            })
        
        pprint(f"modules_with_params_and_returns: {modules_with_params_and_returns}")
        return modules_with_params_and_returns
    
   
    

    def format_nested_options(self,options_dict, indent_level=1):
        """Recursively format nested options without descriptions."""
        result = ""
        indent = "    " * indent_level
        
        for key, value in options_dict.items():
            result += f"{indent}- `{key}`"
            
            # Add type and required info inline
            if isinstance(value, dict):
                type_info = value.get('type', 'unknown')
                required = value.get('required', False)
                req_text = " (required)" if required else ""
                result += f" [{type_info}]{req_text}\n"
                
                # If there are suboptions, recursively format them
                if 'suboptions' in value and value['suboptions']:
                    result += self.format_nested_options(value['suboptions'], indent_level + 1)
            else:
                result += "\n"
        
        return result
                

    def _generate_ansible_playbooks(self, infra_recommendations: Dict[str, Any],repo_path: str) -> Dict[str, str]:
        """Generate Ansible playbooks based on infrastructure recommendations using LLM"""
        # Extract key information from recommendations
        components = infra_recommendations.get("infrastructure_recommendations", [])
        architecture_overview = infra_recommendations.get("architecture_overview", "")
        templates_names_list=self.get_jinja_docker_templates(repo_path)
        # Discover required modules
        ansible_role_summary = (
            "What are the required Ansible modules used to implement infrastructure provisioning "
            "on AWS based on these roles: vpc, subnet, internet_gateway, route_table, keypair, "
            "ec2 provisioning, install_docker, code_setup, docker_template, security_group, database_service."
        )
        modules_info = self.discover_required_modules(ansible_role_summary)

        module_param_section = "\n📦 Required Ansible Modules, Parameters, and Return Values:\n"
        for item in modules_info:
            module_param_section += f"- `{item['module']}`\n"
            
            # Add parameters section
            if item['params']:
                module_param_section += "  📥 Parameters:\n"
                module_param_section += self.format_nested_options(item['params'], indent_level=1)
            
            # Add return values section
            if item['returns']:
                module_param_section += "  📤 Return Values:\n"
                module_param_section += self.format_nested_options(item['returns'], indent_level=1)
            
            module_param_section += "\n"  # Add spacing between modules

        print("=========================================================================================")
        print(f"module_param_section:{module_param_section}")
        print("=========================================================================================")
        # Build prompt for LLM to generate Ansible playbooks
        prompt = f"""You are an expert DevOps automation assistant.

        Generate Ansible playbooks to provision infrastructure and deploy the following application components on a **single AWS EC2 instance** using Docker.

        Architecture Overview:
        {architecture_overview}

        Infrastructure Components:
        """

        # Step 2: Dynamically include component descriptions
        for comp in components:
            prompt += f"""
        - Component: {comp.get('component', 'Unknown')}
        Description: {comp.get('description', 'No description')}
        EC2 Instance Type: {comp.get('aws_ec2_instance_type', 'Not specified')}
        Storage: {comp.get('storage', 'Not specified')}
        Networking: {comp.get('networking', 'Not specified')}
        Availability Zones: {comp.get('availability_zones', 'Not specified')}
        """
        prompt += module_param_section  # Add module info to the prompt
        
        # Add instructions for generating the Ansible playbooks
        # Step 3: Add instructions
        prompt += f"""

        Based on the above, generate **complete Ansible playbooks** in YAML format for deploying the components on a single EC2 instance.

        📌 Required Features:
        - App Repo: `{repo_path}`  
            This should be included in `vars.yml` as `app_repo_url`.
        - Provision one EC2 instance with the specified instance type
        - Use Docker to run detected components ({"frontend" if any(comp["component"] == "frontend" for comp in components) else ""}{" and " if all(comp["component"] in ["frontend", "backend"] for comp in components) else ""}{"backend" if any(comp["component"] == "backend" for comp in components) else ""})
        - Configure network (VPC, Subnet, IGW, Security Groups, Route Table)
        - Setup keypair and SSH access
        - Install Docker engine
        - Setup Docker Compose or Dockerfiles for services
        - Pull app code from GitHub (or allow code to be copied to instance)
        - (Optional) Prepare a role for DB service do not create if no DB detected, otherwise create a role to set up the database service (e.g., MySQL, PostgreSQL) with Docker
        - use Ansible modules from amazon.aws to integrate with any other AWS services from the previous list.
        - Make sure to include only one availability zone.
            🔧 List of Roles to Generate:
            - `vpc` — create a VPC,✅ Make sure the `keypair` role handles copying an existing public SSH key (`id_rsa.pub`) to AWS key pair.
            - `subnet` — Use `aws_subnet` to create the subnet **first** (do NOT use `map_public_ip_on_launch`), then use `ec2_vpc_subnet` to set `map_public: yes`. Never use `map_public_ip_on_launch` — it's not supported.
            - `security_group` — create security groups for the instance , never add description to the rules .
            - `internet_gateway`— create an Internet Gateway and attach it to the VPC
            - `route_table`
            - `keypair` - use key_material: "{{ lookup('file', key_path) }}"
            - `ec2_provision`
                 — launch the EC2 instance and register IP ,use  volume_type: gp3, use ami-014e30c8a36252ae5 , use the EBS settings for volumes such as : volumes:
                    - device_name: /dev/xvda
                        ebs:.
                - After provisioning, add a task to wait for 30 seconds before continuing (to allow the instance to become accessible)

            - `install_docker` — install Docker & Docker Compose make sure in Verify Docker installation to become: yes in order to have the permission ,
            - `code_setup` — clone app code or copy it to `/opt/app`
            - `docker_template` — create Docker Compose or Dockerfiles based on detected services
            - `database_service` — do not create if no DB detected, otherwise create a role to set up the database service (e.g., MySQL, PostgreSQL) with Docker
            

            🧠 Role Behavior:
            - make sure to use vaild and correct key params and modules
            - If only **backend** is detected → skip frontend setup in Docker role
            - If only **frontend** is detected → skip backend setup
            - If **both** are detected → include both in the Docker setup
            - If **no DB** → include an empty `database_service` role (create folder and files but leave them empty)
            - If **DB** is detected → create a role to set it up (e.g., MySQL, PostgreSQL) with Docker
            📌 Important Instructions:
            - Use `delegate_to` and `add_host` to run roles like `install_docker`, `code_setup`, `docker_template` on the provisioned EC2 instance using its public IP.
            - Use `add_host` and `wait_for` in `main.yml` to dynamically add the EC2 host to inventory after creation.
            - Ensure tasks use `ansible_user`, `ansible_ssh_private_key_file`, and the proper `groupname`.
            - Roles must be modular and reusable.
            - Use comments inside tasks for clarity.
            - All services must run inside Docker containers.

            - 📁 Generate these Ansible **roles**, each as its **own directory** with:
            - `roles/ROLE_NAME/tasks/main.yml` → task definitions
            - `roles/ROLE_NAME/defaults/main.yml` → default variables
            - Any shared vars should go in `vars.yml`

            + 📁 For each role, output files in the format:
            + ```yaml
            + # roles/ROLE_NAME/tasks/main.yml
            + ...
            + ```
            write just main.yml at root as the top-level playbook
                - Generate `main.yml` using only the `roles:` section under `hosts: localhost`
                - Skip `include_role` and per-task entries
                - Assume all orchestration is handled **inside the roles**
                includes tasks to:
                    - use these files {templates_names_list}
                    - Render a `Dockerfile` from a Jinja2 template and save it. .
                    - Render a `docker-compose.yml` from `docker-compose.yml.j2` and save it.

            Use the `ansible.builtin.template` module for rendering.
            Ensure the source files are in the `ansible/templates` directory relative to the repo root.
            Set file permissions to `0644`.
            + Use the above format to indicate the file path.
            + Use these full paths as YAML comment headers for every file you output.
            + Do NOT merge all content into one file.
            + Do NOT output only `main.yml`. Every role must have its own correct path header.


            ✅ No placeholder comments like “add your logic here” — implement actual working Ansible tasks.
                    """

        logger.info("Invoking LLM to generate Ansible playbooks...")
        try:
            playbooks_text = self.run_llm(prompt).strip()
            
            # Parse the response to extract individual playbooks
            playbook_sections = self._extract_playbooks_from_response(playbooks_text)
            
            if not playbook_sections:
                logger.warning("Failed to extract playbooks from LLM response, using fallback")
                # return self._generate_fallback_ansible_playbooks(infra_recommendations)
            
            return playbook_sections
            
        except Exception as e:
            logger.error(f"Error generating Ansible playbooks with LLM: {str(e)}")
            # Create fallback playbooks if LLM invocation fails
            # return self._generate_fallback_ansible_playbooks(infra_recommendations)
            
    def _extract_playbooks_from_response(self, response_text: str) -> Dict[str, str]:
        """Extract individual playbooks or related files from LLM response"""
        import re
        playbooks = {}

        pattern = r'```(?:yaml|yml|jinja2)?\s*#\s*(roles/[\w\-_]+/[\w\-/]+\.(?:ya?ml|j2)|[\w\-_]+\.(?:ya?ml|j2))\s*\n([\s\S]*?)```'
        matches = re.findall(pattern, response_text)

        if not matches:
            print("⚠️ No matches found in LLM response.")
            return {}

        for filename, content in matches:
            clean_content = content.strip()
            playbooks[filename.strip()] = clean_content

        return playbooks


    
    
    

    

    def _save_ansible_playbooks(self, repo_path: str, playbooks: Dict[str, str]):
        """Save Ansible playbooks using LangChain FileManagementToolkit tools."""
        if not repo_path or not os.path.isdir(repo_path):
            print("⚠️ Invalid repo path")
            return

        # Initialize toolkit with selected tools
        toolkit = FileManagementToolkit(
            root_dir=repo_path,
            selected_tools=["write_file", "list_directory", "read_file"]
        )
        tools = toolkit.get_tools()

        write_tool = next(t for t in tools if t.name == "write_file")

        # Create required directories
        for sub_dir in ["ansible", "ansible/templates"]:
            os.makedirs(os.path.join(repo_path, sub_dir), exist_ok=True)

        # Write playbook files
        for playbook_name, content in playbooks.items():
            # Properly construct the file path
            file_path = os.path.join("ansible", playbook_name)

            # Ensure directory exists
            full_dir = os.path.dirname(os.path.join(repo_path, file_path))
            os.makedirs(full_dir, exist_ok=True)

            # Save the file
            result = write_tool.invoke({
                "file_path": file_path,
                "text": content
            })


            print(f"✅ Wrote: {file_path} – {result}")

        # ✅ Copy any Docker-related files to templates/ with .j2 extension
        for fname in os.listdir(repo_path):
            if fname.lower().startswith("dockerfile") or fname.lower().startswith("docker-compose"):
                src_path = os.path.join(repo_path, fname)
                if os.path.isfile(src_path):
                    new_name = fname
                    if new_name.endswith(".yml") or new_name.endswith(".yaml"):
                        new_name = new_name.rsplit(".", 1)[0] + ".j2"
                    else:
                        new_name += ".j2"
                    dest_path = os.path.join(repo_path, "ansible", "templates", new_name)
                    shutil.copyfile(src_path, dest_path)
                    print(f"📄 Copied {fname} ➝ templates/{new_name}")



    


            

            