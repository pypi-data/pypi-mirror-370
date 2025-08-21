# GitLlama 🦙

A git automation tool that uses AI to analyze repositories and make code changes. GitLlama clones a repository, analyzes the codebase, selects an appropriate branch, and makes iterative improvements.

## Core Design: Multiple Choice vs Open Response

GitLlama's AI decision-making is built on a dual approach:

- **Multiple Choice Queries**: For deterministic decisions (branch selection, file operations, validation checks)
- **Open Response Queries**: For creative tasks (code generation, commit messages, analysis)

This architecture ensures reliable decision-making while maintaining flexibility for complex tasks.

## Installation

```bash
pip install gitllama
```

## Prerequisites

GitLlama requires Ollama for AI features:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull a model
ollama pull gemma3:4b
```

## Usage

### Basic usage:

```bash
gitllama https://github.com/user/repo.git
```

### With custom model:

```bash
gitllama https://github.com/user/repo.git --model llama3:8b
```

### With specific branch:

```bash
gitllama https://github.com/user/repo.git --branch feature/my-improvement
```

### Verbose mode:

```bash
gitllama https://github.com/user/repo.git --verbose
```

## How It Works

### 1. Repository Analysis
GitLlama analyzes the repository using hierarchical summarization:
- Scans all text files and documentation
- Groups files into chunks that fit the AI's context window
- Analyzes each chunk independently
- Merges summaries hierarchically
- Produces structured insights about the project

### 2. Branch Selection
The AI makes branch decisions using multiple choice queries:
- Analyzes existing branches
- Scores reuse potential
- Decides: REUSE or CREATE
- Selects branch type: feature, fix, docs, or chore

### 3. File Modification
Iterative development with validation:
- AI selects files to modify (multiple choice)
- Generates content (open response)
- Validates changes (multiple choice)
- Continues until satisfied

### 4. Commit and Push
- Generates commit message (open response)
- Commits changes
- Pushes to remote repository

## AI Query Interface

The dual query system provides structure where needed:

```python
# Multiple choice for decisions
result = ai.choice(
    question="Should we reuse an existing branch?",
    options=["REUSE", "CREATE"],
    context="Current branch: main"
)

# Open response for content
result = ai.open(
    prompt="Generate a Python configuration file",
    context="Project type: web application"
)
```

## Architecture

```
gitllama/
├── cli.py                 # Command-line interface
├── git_operations.py      # Git automation
├── ai_coordinator.py      # AI workflow coordination
├── ai_query.py           # Multiple choice / open response interface
├── project_analyzer.py    # Repository analysis
├── branch_analyzer.py     # Branch selection logic
├── file_modifier.py       # File modification workflow
├── response_parser.py     # Response parsing and code extraction
├── report_generator.py    # HTML report generation
└── ollama_client.py      # Ollama API client
```

### Key Components:

- **AIQuery**: Dual interface for structured choices and open responses
- **ProjectAnalyzer**: Hierarchical analysis of repository structure
- **BranchAnalyzer**: Branch selection using multiple choice decisions
- **FileModifier**: Iterative file modification with validation
- **ResponseParser**: Extracts clean code from AI responses

## Reports

GitLlama generates HTML reports with:
- Timeline of AI decisions
- Branch selection rationale
- File modification details
- API usage statistics
- Context window tracking

Reports are saved to `gitllama_reports/` directory.

## Compatible Models

Works with any Ollama model:
- `gemma3:4b` - Fast and efficient (default)
- `llama3.2:1b` - Ultra-fast for simple tasks
- `codellama:7b` - Optimized for code
- `mistral:7b` - General purpose
- `gemma2:2b` - Very fast

## What Gets Analyzed

- Source code (Python, JavaScript, Java, Go, Rust, etc.)
- Configuration files (JSON, YAML, TOML)
- Documentation (Markdown, README)
- Build files (Dockerfile, package.json)
- Scripts (Shell, Batch)

## Performance

- Small repos (<100 files): ~30 seconds
- Medium repos (100-500 files): 1-2 minutes
- Large repos (500+ files): 2-5 minutes

## Development

```bash
git clone https://github.com/your-org/gitllama.git
cd gitllama
pip install -e ".[dev]"

# Run tests
pytest
```

## Troubleshooting

### Ollama not available?
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve
```

### Context window too small?
```bash
# Use a model with larger context
gitllama repo.git --model mistral:7b
```

### Analysis taking too long?
```bash
# Use a smaller model
gitllama repo.git --model llama3.2:1b
```

## License

GPL v3 - see LICENSE file

## Contributing

Contributions welcome! The modular architecture makes it easy to extend.

---

**Note**: GitLlama requires git credentials configured for pushing changes. Ensure you have appropriate repository access before use.