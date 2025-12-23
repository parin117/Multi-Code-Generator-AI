# Multi Code Generation System

An intelligent multi-agent system powered by LangGraph and LangChain that automatically generates complete full-stack web applications from natural language descriptions. The system uses specialized AI agents to handle different aspects of development including database design, backend APIs, frontend interfaces, and documentation.

## 🚀 Features

- **Intelligent Project Analysis**: Automatically analyzes project requirements and breaks them down into manageable tasks
- **Multi-Agent Architecture**: Specialized agents for different development tasks:
  - **Supervisor Agent**: Coordinates and manages the entire development workflow
  - **Database Agent**: Handles database schema design and implementation
  - **Backend Agent**: Creates API endpoints, business logic, and server-side code
  - **Frontend Agent**: Builds user interfaces, components, and client-side functionality
  - **Documentation Agent**: Generates comprehensive project documentation
  - **Flow Validator Agent**: Validates implementation completeness and quality
- **LangGraph Workflow**: Uses LangGraph for orchestrated, stateful multi-agent workflows
- **Interactive Clarification**: Asks clarifying questions when project requirements are ambiguous
- **Automatic Task Planning**: Creates detailed task plans with proper dependency management
- **Project Generation**: Generates complete, production-ready project structures

## 📋 Table of Contents

- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Agents Overview](#agents-overview)
- [Workflow](#workflow)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## 🔧 Prerequisites

- Python 3.8 or higher
- Google Gemini API key (for LLM functionality)
- pip (Python package manager)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/parin117/Toxic-Comment-Classifier.git
   cd Multi_Code_Gen-main
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_gemini_api_key_here
   ```

## ⚙️ Configuration

The system uses environment variables for configuration. Create a `.env` file with the following:

```env
GOOGLE_API_KEY=your_api_key_here
```

You can obtain a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey).

## 🎯 Usage

### Basic Usage

Run the main script to start the code generation process:

```bash
python run.py
```

The system will:
1. Prompt you to enter your project idea
2. Ask clarifying questions if needed (up to 3 iterations)
3. Generate an implementation flow
4. Create a design configuration
5. Ask for a project name
6. Generate the complete project structure

### Example Interaction

```
Enter your project idea: A todo list application with user authentication

Thinker Agent: What type of authentication would you like? (OAuth, JWT, session-based)
Your response: JWT

Flow: [Generated implementation flow]
Design Config: [Generated design configuration]
Project Name: todo-app

--- Generating project with LangGraph workflow system ---
```

### Programmatic Usage

You can also use the system programmatically:

```python
from graph.main_graph import get_idea
from system.workflow_orchestrator import generate_project_with_graph

# Get project analysis
user_idea = "A blog platform with comments and likes"
result = get_idea(user_idea)

# Generate the project
project_result = generate_project_with_graph(
    project_name=result["project_name"],
    flow=result["flow"],
    design_config=result["design_config"]
)
```

## 📁 Project Structure

```
Multi_Code_Gen-main/
├── agents/                  # Specialized AI agents
│   ├── base_agent.py       # Base class for all agents
│   ├── supervisor_agent.py # Coordinates all agents
│   ├── database_agent.py   # Database design and implementation
│   ├── backend_agent.py    # Backend API and logic
│   ├── frontend_agent.py   # Frontend UI and components
│   ├── documentation_agent.py # Documentation generation
│   └── flow_validator_agent.py # Implementation validation
├── chains/                  # LangChain chains
│   ├── thinker.py          # Project analysis chain
│   ├── flow.py             # Implementation flow generation
│   └── design_config.py    # Design configuration chain
├── core/                    # Core utilities
│   ├── llm_utils.py        # LLM initialization and utilities
│   ├── state_manager.py    # State management for workflows
│   └── file_manager.py     # File operations
├── graph/                   # LangGraph workflows
│   └── main_graph.py       # Main project analysis graph
├── system/                  # System orchestration
│   ├── workflow_orchestrator.py # Main workflow orchestrator
│   └── orchestrator.py     # Alternative orchestrator
├── utils/                   # Utility functions
├── run.py                   # Main entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🏗️ Architecture

The system follows a multi-agent architecture pattern:

```
User Input
    ↓
Thinker Agent (Clarification & Analysis)
    ↓
Flow Generation
    ↓
Design Configuration
    ↓
Supervisor Agent (Task Planning)
    ↓
┌─────────────────────────────────────┐
│  Multi-Agent Workflow (LangGraph)   │
│  ┌──────────┐  ┌──────────┐        │
│  │ Database │→ │ Backend  │        │
│  └──────────┘  └──────────┘        │
│       ↓              ↓              │
│  ┌──────────┐  ┌──────────┐        │
│  │ Frontend │← │   Docs   │        │
│  └──────────┘  └──────────┘        │
└─────────────────────────────────────┘
    ↓
Flow Validator
    ↓
Generated Project
```

## 🤖 Agents Overview

### Supervisor Agent
- Analyzes project requirements
- Creates comprehensive task plans
- Manages task dependencies
- Coordinates agent activities
- Monitors project progress

### Database Agent
- Designs database schemas
- Creates models and migrations
- Sets up database connections
- Implements data access layers

### Backend Agent
- Creates API endpoints
- Implements business logic
- Handles data validation
- Sets up server infrastructure

### Frontend Agent
- Builds user interfaces
- Creates interactive components
- Implements client-side logic
- Handles API integration

### Documentation Agent
- Generates README files
- Creates API documentation
- Writes code comments
- Produces user guides

### Flow Validator Agent
- Validates implementation completeness
- Checks code quality
- Identifies missing features
- Ensures project requirements are met

## 🔄 Workflow

1. **Input Processing**: User provides project idea
2. **Clarification**: System asks questions if needed (up to 3 iterations)
3. **Analysis**: Thinker agent analyzes requirements
4. **Flow Generation**: Creates implementation flow
5. **Design Config**: Generates design configuration
6. **Task Planning**: Supervisor creates detailed task plan
7. **Execution**: Agents execute tasks in dependency order
8. **Validation**: Flow validator checks completeness
9. **Iteration**: System iterates until project is complete
10. **Output**: Generated project structure

## 💡 Examples

### Example 1: Todo Application
```
Input: "A todo list app with categories and due dates"
Output: Complete full-stack todo application with:
- Database schema for todos and categories
- REST API endpoints
- Frontend interface with CRUD operations
- User authentication
```

### Example 2: Blog Platform
```
Input: "A blog platform with comments and user profiles"
Output: Full-featured blog platform with:
- Database models for posts, comments, users
- API for content management
- Frontend with post creation and viewing
- Comment system
```

## 🛠️ Development

### Running Tests
```bash
# Add test commands here when tests are implemented
```

### Code Style
The project follows PEP 8 Python style guidelines. Consider using:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

## 📝 Dependencies

Key dependencies include:
- `langchain`: Framework for building LLM applications
- `langgraph`: For creating stateful, multi-agent workflows
- `langchain-google-genai`: Google Gemini integration
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation

See `requirements.txt` for the complete list.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow PEP 8 style guidelines
- Add docstrings to new functions and classes
- Update README if adding new features
- Test your changes before submitting

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Known Issues

- Project path is currently hardcoded in `workflow_orchestrator.py` (line 396)
- Maximum iteration limit is set to 500 (configurable in workflow)

## 🔮 Future Enhancements

- [ ] Support for multiple LLM providers
- [ ] Web UI for project generation
- [ ] Template system for different project types
- [ ] Integration with version control
- [ ] Support for more frameworks and languages
- [ ] Real-time progress tracking
- [ ] Project customization options

## 📞 Support

For issues, questions, or contributions:
- Open an issue on [GitHub](https://github.com/parin117/Toxic-Comment-Classifier/issues)
- Check existing issues and discussions

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/)
- Powered by [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [Google Gemini](https://deepmind.google/technologies/gemini/) for LLM capabilities

## 📊 Project Status

**Current Version**: 1.0.0

**Status**: Active Development

---

Made with ❤️ using AI-powered code generation
