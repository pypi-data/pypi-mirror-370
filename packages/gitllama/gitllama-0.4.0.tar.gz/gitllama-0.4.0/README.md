# GitLlama 🦙🤖

AI-powered git automation tool with deep project understanding. GitLlama v0.4.0 uses hierarchical AI analysis and intelligent single-word decision-making to clone, analyze, optimize, commit, and push your code.

## 🌟 Key Features

- **🧠 Deep Project Analysis**: Hierarchical summarization system that understands entire codebases
- **🎯 Single-Word Decision System**: AI makes deterministic decisions with fuzzy matching for reliability
- **🌿 Intelligent Branch Selection**: AI analyzes existing branches and decides whether to reuse or create new ones
- **📝 TODO.md Integration**: Detects and follows project owner guidance from TODO.md files
- **📊 Smart File Operations**: AI selects up to 5 files to create, modify, or delete intelligently
- **🔄 Guided Questions**: AI asks strategic questions throughout analysis for better understanding
- **📈 Synthesis & Recommendations**: Provides actionable next steps and development priorities
- **📝 Detailed Decision Tracking**: See every AI decision with confidence scores and reasoning

## 🚀 Installation

```bash
pip install gitllama
```

## 📋 Prerequisites

GitLlama requires Ollama for AI-powered features:

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull a recommended model
ollama pull gemma3:4b
```

## 💻 Usage

### Basic usage (recommended):

```bash
gitllama https://github.com/user/repo.git
```

### With custom model:

```bash
gitllama https://github.com/user/repo.git --model llama3:8b
```

### With specific branch (AI handles all other decisions):

```bash
gitllama https://github.com/user/repo.git --branch feature/my-improvement
```

### Verbose mode (see all AI decisions):

```bash
gitllama https://github.com/user/repo.git --verbose
```

## 🔬 How It Works

GitLlama uses a sophisticated multi-step process to understand and improve repositories:

### 1. **Deep Repository Analysis** 🔍
   - **Step 1: Data Gathering** - Scans all text files, configs, and documentation
   - **Step 2: Smart Chunking** - Groups files to maximize AI context window usage
   - **Step 3: Parallel Analysis** - Each chunk analyzed independently for scalability
   - **Step 4: Hierarchical Merging** - Combines summaries using merge-sort approach
   - **Step 5: Result Formatting** - Creates structured insights about the project

### 2. **Intelligent Workflow** 🤖
   1. **Clones the repository**
   2. **AI explores the project** - Deep multi-level analysis across all branches
   3. **AI analyzes existing branches** - Evaluates reuse potential and compatibility
   4. **AI decides on branch strategy** - Smart selection between reusing existing or creating new
   5. **AI makes intelligent changes** - Based on comprehensive project understanding
   6. **AI generates commit message** - Follows conventional commit format
   7. **Pushes to remote**

### Example Analysis Output:
```
Starting hierarchical repository analysis
============================================================
STEP 1: DATA GATHERING
  Found 45 files with 12500 total tokens
STEP 2: CHUNKING
  Created 5 chunks for analysis
    Chunk 1: 12 files, 2500 tokens
    Chunk 2: 10 files, 2800 tokens
    Chunk 3: 8 files, 2200 tokens
    Chunk 4: 9 files, 2600 tokens
    Chunk 5: 6 files, 2400 tokens
STEP 3: CHUNK ANALYSIS
  Analyzing 5 chunks
    Processing chunk 1/5...
    Processing chunk 2/5...
    ...
STEP 4: HIERARCHICAL MERGING
  Starting hierarchical merge of 5 summaries
    Level 1: Merging 5 summaries (1800 tokens)
STEP 5: FORMAT RESULTS
  Formatting final results
============================================================
Repository analysis complete!
```

### 3. **Intelligent Branch Selection** 🌿

GitLlama now features sophisticated branch analysis and selection:

```
Starting intelligent branch selection process
============================================================
STEP 1: ANALYZE EXISTING BRANCHES
  Analyzing purposes of 3 branches
    Branch 'feature/auth-system': Production-ready authentication system
    Branch 'wip-database': Work-in-progress database optimization
    Branch 'docs/api': API documentation updates
STEP 2: EVALUATE REUSE POTENTIAL
  Evaluating reuse potential for existing branches
    wip-database: score=45, reasons=work-in-progress branch, matching project type
    feature/auth-system: score=35, reasons=feature branch, matching technologies
STEP 3: MAKE BRANCH DECISION
  Making branch selection decision
🤖 AI: Deciding branch selection strategy with 2 candidates
    Decision: REUSE - High compatibility with existing WIP branch
STEP 4: GENERATE/SELECT BRANCH NAME
  Finalizing branch selection
    Selected existing branch: wip-database
============================================================
Branch selection complete: wip-database
```

#### Branch Selection Features:
- **🔍 Multi-branch Analysis**: Examines all branches in the repository
- **🎯 Smart Scoring**: Evaluates compatibility based on project type, technologies, and purpose
- **🔄 Reuse Preference**: Strongly favors reusing existing branches (80% bias)
- **🏗️ Branch Classification**: Identifies feature, fix, docs, and WIP branches
- **⚙️ Intelligent Fallback**: Creates new branches with meaningful names when needed

## 🐍 Python API

```python
from gitllama import GitAutomator, AICoordinator

# With AI - Full intelligent automation
ai = AICoordinator(model="gemma3:4b")
with GitAutomator(ai_coordinator=ai) as automator:
    results = automator.run_full_workflow(
        git_url="https://github.com/user/repo.git"
    )
    
    print(f"Success: {results['success']}")
    print(f"Branch created: {results['branch']}")
    print(f"Files modified: {results['modified_files']}")
    
    # Access detailed AI analysis
    if 'ai_analysis' in results:
        analysis = results['ai_analysis']
        print(f"Project Type: {analysis['project_type']}")
        print(f"Technologies: {', '.join(analysis['technologies'])}")
        print(f"Code Quality: {analysis['quality']}")
        print(f"Architecture: {analysis['architecture']}")

# Without AI - Simple automation
with GitAutomator() as automator:
    results = automator.run_full_workflow(
        git_url="https://github.com/user/repo.git",
        branch_name="my-branch",
        commit_message="My changes"
    )
```

## 🏗️ Architecture

GitLlama is built with a modular architecture for easy extension:

```
gitllama/
├── cli.py              # Command-line interface
├── git_operations.py   # Git automation logic
├── ai_coordinator.py   # AI workflow coordination
├── project_analyzer.py # Hierarchical project analysis
├── branch_analyzer.py  # Intelligent branch selection (NEW!)
├── config.py           # Configuration and logging setup
└── ollama_client.py    # Ollama API integration
```

### Key Components:

- **ProjectAnalyzer**: Handles the 5-step hierarchical analysis process
- **BranchAnalyzer**: Intelligent branch selection with 4-step decision pipeline (NEW!)
- **AICoordinator**: Orchestrates AI decisions throughout the workflow
- **GitAutomator**: Manages git operations with optional AI integration
- **OllamaClient**: Interfaces with local Ollama models

## 🤖 AI Models

The tool works with any Ollama model. Recommended models:

- `gemma3:4b` - Fast and efficient (default)
- `llama3.2:1b` - Ultra-fast for simple tasks
- `codellama:7b` - Optimized for code understanding
- `mistral:7b` - Good general purpose
- `gemma2:2b` - Very fast, good for simple tasks

### Context Window Sizes:
- Small models (1-3B): ~2-4K tokens
- Medium models (7B): ~4-8K tokens
- Large models (13B+): ~8-16K tokens

## 🎯 What Gets Analyzed

GitLlama intelligently analyzes:
- Source code files (Python, JavaScript, Java, Go, Rust, etc.)
- Configuration files (JSON, YAML, TOML, etc.)
- Documentation (Markdown, README, LICENSE)
- Build files (Dockerfile, Makefile, package.json)
- Scripts (Shell, Batch, PowerShell)
- Web assets (HTML, CSS, XML)

## 📊 Analysis Results

The AI provides multi-level insights:

```json
{
  "project_type": "web-application",
  "technologies": ["Python", "FastAPI", "PostgreSQL", "React"],
  "state": "Production-ready with comprehensive test coverage",
  "architecture": "Microservices with REST API",
  "quality": "High - follows best practices",
  "patterns": ["MVC", "Repository Pattern", "Dependency Injection"],
  "analysis_metadata": {
    "total_files": 156,
    "total_tokens": 45000,
    "chunks_created": 12,
    "context_window": 4096,
    "model": "gemma3:4b"
  }
}
```

## ⚙️ Configuration

```bash
# Use a different Ollama server
gitllama https://github.com/user/repo.git --ollama-url http://remote-server:11434

# Use a specific model with more context
gitllama https://github.com/user/repo.git --model codellama:7b

# Verbose output for debugging
gitllama https://github.com/user/repo.git --verbose
```

## 🔧 Extending GitLlama

The modular design makes it easy to add new analysis steps:

```python
# In project_analyzer.py, each step is clearly separated:

def _step1_gather_repository_data(self, repo_path):
    """STEP 1: Gather all repository data"""
    # Add git history analysis here
    # Add dependency scanning here
    # Add security checks here

def _step2_create_chunks(self, files):
    """STEP 2: Create smart chunks"""
    # Add semantic grouping here
    # Add priority-based chunking here

def _step3_analyze_chunks(self, chunks):
    """STEP 3: Analyze each chunk"""
    # Add code quality metrics here
    # Add security scanning here
    # Add performance analysis here
```

## 📈 Performance

- **Small repos (<100 files)**: ~30 seconds
- **Medium repos (100-500 files)**: ~1-2 minutes
- **Large repos (500+ files)**: ~2-5 minutes

*Times vary based on model size and system performance*

## 🛠️ Development

```bash
git clone https://github.com/your-org/gitllama.git
cd gitllama
pip install -e ".[dev]"

# Run tests
pytest

# Check code quality
make lint
make format
make type-check
```

## 🐛 Troubleshooting

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
# Use a smaller, faster model
gitllama repo.git --model llama3.2:1b
```

## 📝 License

GPL v3 - see LICENSE file

## 🤝 Contributing

Contributions are welcome! The modular architecture makes it easy to add:
- New analysis steps
- Additional AI models support
- More file type handlers
- Enhanced decision strategies

## 🚀 Future Enhancements

- [ ] Git history analysis
- [ ] Dependency vulnerability scanning
- [ ] Parallel chunk processing
- [ ] Code quality metrics
- [ ] Security analysis
- [ ] Test coverage assessment
- [ ] README generation
- [ ] Automatic PR descriptions
- [ ] Multi-language documentation

---

**Note**: GitLlama requires git credentials configured for pushing to repositories. Ensure you have proper access rights to the repositories you're modifying.