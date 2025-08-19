# Agent as Code - Python Package

```
    _                _       _          ___         _               _         ___ 
   /_\  __ _ ___ _ _| |_    /_\   ___  / __|___  __| |___   ___    /_\  __ _ / __|
  / _ \/ _` / -_) ' \  _|  / _ \ (_-< | (__/ _ \/ _` / -_) |___|  / _ \/ _` | (__ 
 /_/ \_\__, \___|_||_\__| /_/ \_\/__/  \___\___/\__,_\___|       /_/ \_\__,_|\___|
       |___/                                                                      
```

**Docker-like CLI for AI agents with hybrid Go + Python architecture**

[![PyPI version](https://badge.fury.io/py/agent-as-code.svg)](https://badge.fury.io/py/agent-as-code)
[![Python versions](https://img.shields.io/pypi/pyversions/agent-as-code.svg)](https://pypi.org/project/agent-as-code/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 **Hybrid Architecture**

Agent as Code combines the **performance of Go** with the **ecosystem of Python**:

- **⚡ Go Binary Core**: High-performance CLI operations with 10x speed improvement
- **🐍 Python Wrapper**: Seamless integration with Python development workflows
- **📦 Zero Dependencies**: Single binary with no runtime requirements
- **🌍 Cross-Platform**: Native binaries for Linux, macOS, Windows (x86_64, ARM64)

## What is Agent as Code?

Agent as Code (AaC) brings the simplicity of Docker to AI agent development. Just like Docker revolutionized application deployment, Agent as Code revolutionizes AI agent development with:

- **Familiar Commands**: `agent build`, `agent run`, `agent push` - just like Docker
- **Declarative Configuration**: Define agents with simple `agent.yaml` files
- **Template System**: Pre-built templates for common use cases
- **Multi-Runtime Support**: Python, Node.js, Go, and more
- **Registry Integration**: Share and discover agents easily

## Quick Start

### Installation

```bash
pip install agent-as-code
```

### Create Your First Agent

```bash
# Create a new chatbot agent
agent init my-chatbot --template chatbot

# Navigate to the project
cd my-chatbot

# Build the agent
agent build -t my-chatbot:latest .

# Run the agent
agent run my-chatbot:latest
```

Your agent is now running at `http://localhost:8080`! 🚀

## Available Templates

Get started instantly with pre-built templates:

```bash
agent init my-bot --template chatbot           # Customer support chatbot
agent init analyzer --template sentiment      # Sentiment analysis
agent init summarizer --template summarizer   # Document summarization  
agent init translator --template translator   # Language translation
agent init insights --template data-analyzer  # Data analysis
agent init writer --template content-gen      # Content generation
```

## Python API Usage

Use Agent as Code programmatically in your Python applications:

```python
from agent_as_code import AgentCLI

# Initialize the CLI
cli = AgentCLI()

# Create a new agent
cli.init("my-agent", template="sentiment", runtime="python")

# Build the agent
cli.build(".", tag="my-agent:latest")

# Run the agent
cli.run("my-agent:latest", port="8080:8080", detach=True)

# Check running agents
images = cli.images(quiet=True)
print(f"Available agents: {images}")
```

## Agent Configuration

Define your agent with a simple `agent.yaml` file:

```yaml
apiVersion: agent.dev/v1
kind: Agent
metadata:
  name: my-chatbot
  version: 1.0.0
  description: Customer support chatbot
spec:
  runtime: python
  model:
    provider: openai
    name: gpt-4
    config:
      temperature: 0.7
      max_tokens: 500
  capabilities:
    - conversation
    - customer-support
  ports:
    - container: 8080
      host: 8080
  environment:
    - name: OPENAI_API_KEY
      value: ${OPENAI_API_KEY}
  healthCheck:
    command: ["curl", "-f", "http://localhost:8080/health"]
    interval: 30s
    timeout: 10s
    retries: 3
```

## Use Cases

### 🤖 **Customer Support**
```bash
agent init support-bot --template chatbot
# Includes conversation memory, intent classification, escalation handling
```

### 📊 **Data Analysis**
```bash
agent init data-insights --template data-analyzer
# Includes statistical analysis, visualization, AI-powered insights
```

### 🌐 **Content Creation**
```bash
agent init content-writer --template content-gen
# Includes blog posts, social media, marketing copy generation
```

### 🔍 **Text Analysis**
```bash
agent init text-analyzer --template sentiment
# Includes sentiment analysis, emotion detection, batch processing
```

## Development Workflow

### Local Development
```bash
# Create and test locally
agent init my-agent --template chatbot
cd my-agent
agent build -t my-agent:dev .
agent run my-agent:dev

# Make changes and rebuild
agent build -t my-agent:dev . --no-cache
```

### Production Deployment
```bash
# Build for production
agent build -t my-agent:1.0.0 .

# Push to registry
agent push my-agent:1.0.0

# Deploy anywhere
docker run -p 8080:8080 my-agent:1.0.0
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Install Agent CLI
  run: pip install agent-as-code

- name: Build Agent
  run: agent build -t ${{ github.repository }}:${{ github.sha }} .

- name: Push Agent
  run: agent push ${{ github.repository }}:${{ github.sha }}
```

## Python Ecosystem Integration

### Jupyter Notebooks
```python
# Install in notebook
!pip install agent-as-code

# Create agent directly in notebook
from agent_as_code import AgentCLI
cli = AgentCLI()
cli.init("notebook-agent", template="sentiment")
```

### Virtual Environments
```bash
# Each project can have its own agent version
python -m venv myproject
source myproject/bin/activate
pip install agent-as-code==1.0.0
agent init my-project-agent
```

### Poetry Integration
```bash
# Add to your Poetry project
poetry add agent-as-code
poetry run agent init my-agent --template chatbot
```

## Advanced Features

### Local LLM Support
```yaml
# Use local models with Ollama
spec:
  model:
    provider: local
    name: llama2
    config:
      host: localhost:11434
```

### Multi-Runtime Support
```bash
# Python runtime
agent init py-agent --runtime python

# Node.js runtime  
agent init js-agent --runtime nodejs

# Go runtime
agent init go-agent --runtime go
```

### Custom Templates
```bash
# Create your own template
mkdir -p ~/.agent-as-code/templates/my-template
# Add your template files
agent init new-agent --template my-template
```

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Architecture**: x86_64 (amd64) or ARM64

The package includes pre-compiled binaries for all supported platforms, so no additional dependencies are required.

## Architecture

This Python package is a wrapper around a high-performance Go binary:

- **Go Binary**: Handles core CLI operations (build, run, etc.)
- **Python Wrapper**: Provides Python API and pip integration
- **Cross-Platform**: Works on Linux, macOS, and Windows
- **Self-Contained**: No external dependencies required

## Contributing

We welcome contributions as soon as we have the Go binary ready to make public along with the github Repo!

## Support

- **📖 Documentation**: [agent-as-code.myagentregistry.com/documentation](https://agent-as-code.myagentregistry.com/documentation)
- **🚀 Getting Started**: [agent-as-code.myagentregistry.com/getting-started](https://agent-as-code.myagentregistry.com/getting-started)
- **💡 Examples**: [agent-as-code.myagentregistry.com/examples](https://agent-as-code.myagentregistry.com/examples)
- **🔧 CLI Reference**: [agent-as-code.myagentregistry.com/cli](https://agent-as-code.myagentregistry.com/cli)
- **📦 Registry Guide**: [agent-as-code.myagentregistry.com/registry](https://agent-as-code.myagentregistry.com/registry)

---

**Ready to build your first AI agent?**

```bash
pip install agent-as-code
agent init my-first-agent --template chatbot
cd my-first-agent
agent run
```

**Join thousands of developers building the future of AI agents! 🚀**