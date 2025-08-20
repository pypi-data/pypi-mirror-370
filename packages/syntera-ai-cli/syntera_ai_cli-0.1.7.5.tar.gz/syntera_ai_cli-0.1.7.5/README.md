# SynteraAI DevOps Toolkit

An AI-powered DevOps toolkit for infrastructure automation and analysis. This tool helps DevOps engineers automate infrastructure recommendations, security scanning, code quality analysis, and more using AI.

## Features

- 🤖 AI-powered infrastructure recommendations

- 🐳 Automatic Dockerfile generation

- 📦 Dependency checking

- ⚙️ Deployment automation with Ansible

- 📊 Monitoring automation with Prometheus and Grafana


## Installation

```bash
pip install syntera-ai-cli
```

## Quick Start

1. Set up your OpenAI API key:
linux:
```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```
windows(Powershell):
```bash
$env:GEMINI_API_KEY = "your-gemini-api-key-here"

```
Another great option:
use `.env `file .


2. Run the dashboard
- in windows :
```bash
syntera-ai dashboard
```
- in unix (mac or linux):

```bash
sudo GEMINI_API_KEY=$GEMINI_API_KEY syntera-ai dashboard
```


3. Enter your GitHub repository URL when prompted.

4. Use the interactive dashboard to:
   - Generate infrastructure recommendations
   - Generate Docker files
   - Generate ansible deployment files
   - And more!

## Usage Examples

### Infrastructure Recommendations
```bash
syntera-ai dashboard
# Select option 2 for infrastructure recommendations
```

### Security Scanning
```bash
syntera-ai dashboard
# Select option 3 for security scanning
```

### Code Quality Analysis
```bash
syntera-ai dashboard
# Select option 6 for code quality analysis
```

## Requirements

- Python 3.8 or higher
- Gemmini API key
- Git (for repository analysis)

## 🚀 Features

This tool provides a full DevOps automation pipeline, from containerization to deployment and monitoring setup. Follow the features **in order** for the best results.

---

### 🐳 Docker Generation

Automatically generate `Dockerfile`s and `docker-compose.yml` based on your project’s structure and tech stack.

- Detects backend/frontend frameworks, ports, and dependencies.
- Creates service-specific Dockerfiles with best practices.
- Adds `.env` support if available.
- Ensures Nginx handling and proper ENTRYPOINT setup.

➡️ **Output**: Dockerfiles and a ready-to-use `docker-compose.yml`.

---

### 🏗️ Infrastructure Provisioning

Generates full Ansible playbooks and reusable roles to deploy your app on a cloud server (e.g., AWS EC2).

- Provisions VPC, subnet, EC2, keypair, security groups.
- Installs Docker, sets up app containers, and deploys from your repo.
- Includes modular roles like `install_docker`, `code_setup`, `docker_template`, and optional `database_service`.

➡️ **Output**: Ansible `main.yml` and role directories under `roles/`.

---

### 📈 Monitoring Audit

Analyzes your Prometheus & Grafana setup for observability and DevOps best practices.

- Reviews Ansible roles for monitoring (e.g., `monitoring`, `alerting`).
- Suggests improvements in metrics collection, dashboards, and alert rules.
- Ensures roles are modular and production-ready.

➡️ **Output**: An analysis report with improvement recommendations, in addition to eding the ansible playbook to automate generate grafana dashboard for server metrics.

---

### ✅ Usage Order

To use this tool effectively:

1. **Start with Docker Generation** – containerize your services.
2. **Proceed to Infrastructure Provisioning** – deploy containers to the cloud.
3. **Finish with Monitoring Audit** – validate observability and alerts.

---


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Fouad Mahmoud
- GitHub: [@fouadmahmoud281](https://github.com/fouadmahmoud281)
- Email: fouadmahmoud281@gmail.com 