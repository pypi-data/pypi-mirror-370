# GitLlama 🦙🤖

AI-powered git automation tool. Let AI intelligently clone, branch, change, commit, and push your code.

## Features

- **AI-Powered Decision Making**: Uses Ollama LLMs to make intelligent decisions
- **Smart Repository Analysis**: AI explores and understands your project structure
- **Intelligent Branch Naming**: AI suggests meaningful branch names based on context
- **Automated File Operations**: AI decides what files to create, modify, or delete
- **Context-Aware Commits**: AI generates meaningful commit messages
- **Fallback Mode**: Works without AI for simple automation

## Installation

```bash
pip install gitllama
```

## Prerequisites

For AI features, you need Ollama running locally:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model (recommended for this tool)
ollama pull llama3.2:3b
```

## Usage

### Basic AI-powered usage:

```bash
gitllama https://github.com/user/repo.git
```

### With custom model:

```bash
gitllama https://github.com/user/repo.git --model codellama:7b
```

### Manual branch name (AI still handles other decisions):

```bash
gitllama https://github.com/user/repo.git --branch feature/my-improvement
```

### Manual commit message:

```bash
gitllama https://github.com/user/repo.git --message "feat: add new feature"
```

### Disable AI (simple automation):

```bash
gitllama https://github.com/user/repo.git --no-ai
```

## What it does

1. **Clones the repository**
2. **AI explores the project** - reads files, understands structure
3. **AI decides on branch name** - meaningful and context-aware
4. **AI makes intelligent changes** - creates, modifies, or deletes files
5. **AI generates commit message** - follows conventional commit format
6. **Pushes to remote**

## Python API

```python
from gitllama import GitAutomator, AICoordinator

# With AI
ai = AICoordinator(model="llama3.2:3b")
with GitAutomator(ai_coordinator=ai) as automator:
    results = automator.run_full_workflow(
        git_url="https://github.com/user/repo.git"
    )
    print(f"Success: {results['success']}")
    print(f"AI Analysis: {results.get('ai_analysis')}")

# Without AI
with GitAutomator() as automator:
    results = automator.run_full_workflow(
        git_url="https://github.com/user/repo.git",
        branch_name="my-branch",
        commit_message="My changes"
    )
```

## AI Models

The tool works with any Ollama model. Recommended models:

- `llama3.2:3b` - Fast and efficient (default)
- `codellama:7b` - Better for code-heavy repositories
- `mistral:7b` - Good general purpose
- `gemma2:2b` - Very fast, good for simple tasks

## Configuration

```bash
# Use a different Ollama server
gitllama https://github.com/user/repo.git --ollama-url http://remote-server:11434

# Verbose output for debugging
gitllama https://github.com/user/repo.git --verbose
```

## How AI Makes Decisions

1. **Repository Exploration**: AI reads key files to understand project type, technologies, and structure
2. **Branch Naming**: Based on project context, suggests descriptive branch names
3. **File Operations**: Decides whether to:
   - Create new files (documentation, configs, utilities)
   - Modify existing files (improvements, fixes)
   - Delete unnecessary files
4. **Commit Messages**: Generates conventional commit format messages based on changes

## Development

```bash
git clone https://github.com/your-org/gitllama.git
cd gitllama
pip install -e ".[dev]"
```

## License

GPL v3 - see LICENSE file.