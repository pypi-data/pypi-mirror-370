<div align="center">

# 🚀 Genesis MCP Core SDK
### Enterprise-Ready Model Context Protocol Development Kit

**Complete MCP 2025-06-18 SDK with Enterprise Templates & Healthcare AI Integration**

[![MCP Protocol](https://img.shields.io/badge/MCP-2025--06--18-blue.svg)](https://modelcontextprotocol.io)
[![Python](https://img.shields.io/badge/Python-3.12+-green.svg)](https://python.org)
[![PyPI](https://img.shields.io/badge/PyPI-v0.0.3-orange.svg)](https://pypi.org/project/genesis-mcp-core/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)](#testing)
[![Enterprise](https://img.shields.io/badge/Enterprise-Ready-red.svg)](#enterprise-features)

**🏗️ Complete SDK** • **⚡ Enterprise Templates** • **🔒 Production Ready** • **📦 PyPI Available**

[🎯 Quick Start](#-quick-start) • [🏗️ Enterprise Features](#-enterprise-features) • [📚 Documentation](#-documentation) • [🤝 Contributing](#-contributing)

---

</div>

**Genesis MCP Core SDK** is the most comprehensive software development kit for building production-ready Model Context Protocol servers. It provides everything needed for enterprise healthcare AI applications with advanced template generation, CI/CD pipelines, Kubernetes deployment, and full MCP 2025-06-18 compliance.

## ✨ **What Makes Genesis MCP Core Special?**

> 🎯 **The only MCP SDK with enterprise-ready templates, CI/CD pipelines, and Kubernetes deployment out-of-the-box**

<table>
<tr>
<td width="50%">

### 🏗️ **Enterprise Templates**
- **🚀 Complete Project Scaffolding** - Full MCP server generation
- **🔄 Azure DevOps CI/CD** - Production-ready pipelines
- **⚓ Kubernetes Helm Charts** - Container orchestration
- **🔧 Template Engine** - Jinja2-powered customization

</td>
<td width="50%">

### 🤖 **Advanced MCP Features**
- **📋 MCP 2025-06-18 Compliance** - Latest protocol support
- **🧠 Intelligent Elicitation** - Human-in-the-loop interactions
- **🔒 Security Hardening** - Enterprise-grade security
- **🏥 Healthcare Integration** - Medical API connectors

</td>
</tr>
</table>

## 🚀 **Quick Start**

### **Installation**

```bash
# Install from PyPI
pip install genesis-mcp-core

# Or install latest development version
pip install git+https://github.com/your-org/genesis-mcp-core.git
```

### **Create Your First MCP Server**

```bash
# Create a new enterprise-ready MCP server
genesis-mcp create my-healthcare-service \
  --template basic \
  --connectors encoder \
  --connectors pa

# Navigate to your new service
cd my-healthcare-service

# Install dependencies
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your API credentials

# Start development server
make dev
```

### **What You Get**

```
my-healthcare-service/
├── 🔄 azure-devops/           # Complete CI/CD pipeline
│   ├── build-template.yml     # Docker build & push
│   ├── cicd.yaml             # Full deployment pipeline
│   ├── helmpublish.yml       # Helm chart publishing
│   └── sonar.yml             # Code quality & testing
├── ⚓ helmcharts/             # Kubernetes deployment
│   └── my-healthcare-service/
│       ├── Chart.yaml        # Helm chart definition
│       ├── values.yaml       # Configuration values
│       └── templates/        # K8s manifests
├── 🔌 connectors/            # MCP connector configs
├── 🐍 main.py                # MCP server implementation
├── 🐳 Dockerfile             # Container configuration
├── 📋 Makefile               # Build automation
└── 🧪 tests/                 # Test suite
```

## 🏗️ **Enterprise Features**

<div align="center">

| Feature | Status | Description |
|---------|:------:|-------------|
| **🚀 Project Templates** | ✅ | Complete MCP server scaffolding |
| **🔄 Azure DevOps CI/CD** | ✅ | Production-ready build pipelines |
| **⚓ Kubernetes Helm Charts** | ✅ | Container orchestration manifests |
| **🔧 Template Engine** | ✅ | Jinja2-powered customization |
| **🏥 Healthcare Connectors** | ✅ | Medical API integrations |
| **🔒 Security Hardening** | ✅ | Enterprise-grade security patterns |
| **📦 PyPI Distribution** | ✅ | Easy installation & updates |
| **🧪 Testing Framework** | ✅ | Comprehensive test suite |

</div>

### **🔄 Azure DevOps Integration**

Generated services include complete CI/CD pipelines:

- **Build Pipeline** - Docker image creation and registry push
- **Quality Gates** - SonarCloud integration with code coverage
- **Helm Packaging** - Automatic chart versioning and publishing  
- **GitOps Deployment** - Automated environment updates
- **Security Scanning** - Container and dependency vulnerability checks

### **⚓ Kubernetes Deployment**

Production-ready Helm charts with:

- **Deployment Manifests** - Scalable container orchestration
- **Service Configuration** - Load balancing and networking
- **ConfigMaps & Secrets** - Environment-specific configuration
- **Health Checks** - Liveness and readiness probes
- **Horizontal Pod Autoscaling** - Automatic scaling based on metrics
- **Ingress Configuration** - External access and SSL termination

## 📚 **Template System**

### **Available Templates**

- **`basic`** - Complete MCP server with enterprise features
- **`healthcare`** - Healthcare-optimized with medical APIs *(coming soon)*
- **`api`** - REST API focused template *(coming soon)*
- **`database`** - Database integration template *(coming soon)*

### **Template Customization**

```bash
# Create service with specific configuration
genesis-mcp create enterprise-service \
  --template basic \
  --server-port 8001 \
  --connectors encoder \
  --connectors pa \
  --connectors qnxt \
  --azure-registry myregistry \
  --helm-registry myhelm
```

### **Template Variables**

The template system supports dynamic customization:

- **`{{ SERVICE_NAME }}`** - Service identifier
- **`{{ SERVER_PORT }}`** - HTTP server port
- **`{{ CONNECTOR_NAMES }}`** - List of enabled connectors
- **`{{ AZURE_CONTAINER_REGISTRY }}`** - Container registry
- **`{{ HELM_ACR_NAME }}`** - Helm chart registry

## 🤖 **MCP 2025-06-18 Features**

### **Core Protocol Support**

- **Modern Endpoints** - `/mcp` with bidirectional streaming
- **Legacy Compatibility** - Full backward compatibility
- **Elicitation Engine** - Human-in-the-loop parameter collection
- **Structured Output** - JSON Schema validation
- **Security Hardening** - Anti-poisoning and input validation

### **Healthcare Integration**

Built-in support for medical APIs:

- **Molina Healthcare** - Medical coding and prior authorization
- **Azure OpenAI** - Clinical AI and document processing  
- **QNXT System** - Claims processing and member management
- **JIVA Platform** - Contact and document workflows

## 🧪 **Testing**

### **Run Tests**

```bash
# Install development dependencies
poetry install --with dev

# Run full test suite
poetry run pytest tests/ -v --cov=genesis_mcp_core

# Run enterprise template tests
poetry run pytest tests/test_enterprise_templating.py -v

# Run specific test categories
poetry run pytest tests/unit/ -v          # Unit tests
poetry run pytest tests/integration/ -v   # Integration tests
```

### **Test Coverage**

- **Template Generation** - Complete scaffolding validation
- **CLI Functionality** - Command-line interface testing
- **Enterprise Features** - CI/CD and Helm chart validation
- **MCP Protocol** - 2025-06-18 compliance testing
- **Healthcare APIs** - Medical connector integration

## 🔧 **Development**

### **Local Development**

```bash
# Clone repository
git clone https://github.com/your-org/genesis-mcp-core.git
cd genesis-mcp-core

# Install dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Build package
poetry build

# Install locally for testing
pip install dist/genesis_mcp_core-*.whl
```

### **Contributing**

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

#### **Areas for Contribution**

- 🏗️ **New Templates** - Additional project templates
- 🔌 **Connector Types** - New API integrations
- 🔒 **Security Features** - Enhanced security patterns
- 📚 **Documentation** - Guides and examples
- 🧪 **Testing** - Test coverage and scenarios

## 📖 **Documentation**

- **[CLI Reference](docs/cli.md)** - Command-line usage
- **[Template Guide](docs/templates.md)** - Creating custom templates
- **[Enterprise Deployment](docs/enterprise.md)** - Production setup
- **[Healthcare APIs](docs/healthcare.md)** - Medical integrations
- **[Contributing Guide](CONTRIBUTING.md)** - Development workflow

## 🏥 **Healthcare Use Cases**

Genesis MCP Core is designed for healthcare AI applications:

- **Clinical Decision Support** - AI-powered medical insights
- **Prior Authorization** - Automated approval workflows  
- **Medical Coding** - ICD-10, CPT, and HCPCS processing
- **Claims Processing** - Healthcare billing automation
- **Patient Engagement** - Conversational healthcare interfaces

## 📦 **Distribution**

### **PyPI Package**

```bash
# Latest stable release
pip install genesis-mcp-core

# Specific version
pip install genesis-mcp-core==0.0.3

# Development version
pip install --pre genesis-mcp-core
```

### **Docker Images**

```bash
# Pull pre-built image
docker pull ghcr.io/your-org/genesis-mcp-core:latest

# Run containerized CLI
docker run --rm -v $(pwd):/workspace \
  ghcr.io/your-org/genesis-mcp-core:latest \
  create my-service --template basic
```

## 🔒 **Security**

Genesis MCP Core implements enterprise-grade security:

- **Input Validation** - Comprehensive parameter sanitization
- **Authentication** - OAuth2 and API key support
- **Authorization** - Role-based access control
- **Encryption** - TLS/SSL for all communications
- **Audit Logging** - Complete request/response tracking

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **[Model Context Protocol](https://modelcontextprotocol.io)** - For the MCP specification
- **[Autonomize AI](https://github.com/autonomize-ai)** - For healthcare connector integrations
- **Healthcare Community** - For real-world feedback and use cases
- **Open Source Contributors** - For making this project better

---

<div align="center">

**Built with ❤️ for Enterprise Healthcare AI**

[🎯 Get Started](#-quick-start) • [🏗️ Enterprise Features](#-enterprise-features) • [📚 Documentation](#-documentation) • [🤝 Contribute](#-contributing)

**⭐ Star this project to support enterprise MCP development!**

</div>