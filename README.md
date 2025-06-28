# 🎭 Multi-LLM Conductor - Multi-Agent AI Orchestration System

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/status-alpha-orange.svg" alt="Alpha Status">
</p>

Multi-LLM Conductor orchestrates multiple AI agents (CLI-based and API-based) to collaboratively work on software development projects with full transparency and project management capabilities.

## ✨ Features

- **Multi-Agent Collaboration**: Coordinate multiple AI agents working together
- **CLI & API Support**: Integrate both Claude CLI and various API-based models
- **Project Management**: Full visibility into agent activities, task queues, and progress
- **Real-time Monitoring**: Live dashboard showing what each agent is doing
- **Cost Tracking**: Monitor API usage and costs per project
- **Organized Output**: Each project gets its own folder with structured outputs

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Claude CLI installed (`claude` command available)
- API keys for desired AI services

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Clark-Wallace/Multi-LLM-Conductor.git
cd Multi-LLM-Conductor
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. Run the server:
```bash
python api/server_fast.py
```

6. Open browser to http://localhost:8200

## 🎯 Usage

### Basic Orchestration

1. Enter a task description in the web UI
2. Choose between FAST mode (parallel) or DETAILED mode (sequential)
3. Watch agents collaborate in real-time
4. Find generated files in `projects_master/your-project-timestamp/`

### Example Tasks

- "Create a REST API for a todo application"
- "Build a React dashboard with authentication"
- "Develop a Python CLI tool for file management"

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web UI        │────▶│   Conductor     │────▶│   Agent Pool    │
│                 │     │   Orchestrator  │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                          │
                               ▼                          ▼
                        ┌─────────────┐           ┌──────────────┐
                        │Project State│           │ • Claude CLI │
                        │  Manager    │           │ • GPT-4 API  │
                        └─────────────┘           │ • DeepSeek   │
                                                  └──────────────┘
```

### Key Components

- **Orchestrator**: Manages project lifecycle and agent coordination
- **Agent Registry**: Tracks agent capabilities and availability
- **Task Queue**: Handles task distribution and dependencies
- **Project Manager**: Maintains project state and file organization

## 📁 Project Structure

```
multi-llm-conductor/
├── core/               # Core orchestration logic
├── agents/             # Agent implementations
│   ├── cli_agents/     # CLI-based agents (Claude)
│   └── api_agents/     # API-based agents (GPT-4, etc.)
├── api/                # FastAPI server
├── ui/                 # Web interface
├── projects_master/    # Generated project outputs
└── tests/              # Test suite
```

## 🔧 Configuration

### Supported AI Providers

- **Claude CLI** (Local)
- **OpenAI** (GPT-4, GPT-3.5)
- **Anthropic** (Claude API)
- **DeepSeek** (Coding specialized)
- **Google Gemini**
- **Groq** (Fast inference)
- **Ollama** (Local models)

### Environment Variables

See `.env.example` for all configuration options. Key settings:

- `MAX_PARALLEL_AGENTS`: Number of agents that can work simultaneously
- `MAX_COST_PER_PROJECT`: Cost limit per project
- `PROJECT_BASE_DIR`: Where project outputs are stored

## 🧪 Development

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

### Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📊 Roadmap

- [x] Basic multi-agent orchestration
- [x] Project folder organization
- [x] Real-time web interface
- [ ] API agent integration
- [ ] Advanced project management UI
- [ ] Task dependency resolution
- [ ] Cost optimization algorithms
- [ ] Template system
- [ ] Plugin architecture

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/Clark-Wallace/Multi-LLM-Conductor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Clark-Wallace/Multi-LLM-Conductor/discussions)
- **Documentation**: [Wiki](https://github.com/Clark-Wallace/Multi-LLM-Conductor/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Claude by Anthropic for CLI integration
- FastAPI for the web framework
- All AI providers for their APIs

---

<p align="center">
  Built with ❤️ by developers, for developers
</p>