# Request Flow Analysis

## Entry Points Overview

The AI Documentation Generator is a command-line application with multiple entry points defined in `src/main.py`. The application uses an argument parser to handle different commands:

### Primary Entry Points
- **CLI Entry Point**: `main()` function in `src/main.py` serves as the primary entry point
- **Command Structure**: Uses `argparse` with subcommands for different operations:
  - `analyze` - Runs code analysis agents
  - `document` - Generates documentation (README)
  - `cronjob` - Automated analysis for GitLab projects

### Command Flow Initialization
The application follows this initialization pattern:
1. Configure Langfuse for observability
2. Parse command-line arguments using `parse_args()`
3. Route to appropriate handler based on command
4. Configure logging per repository
5. Execute the selected handler

## Request Routing Map

The application uses a command-based routing system rather than HTTP routing:

### Command Routing
```
main() → parse_args() → match command:
├── "analyze" → analyze(args)
├── "document" → document(args) 
└── "cronjob" → cronjob_analyze(args)
```

### Handler Resolution
Each command resolves to a specific handler:
- **analyze**: Creates `AnalyzeHandler` with `AnalyzeHandlerConfig`
- **document**: Creates `ReadmeHandler` with `ReadmeHandlerConfig`
- **cronjob**: Creates `JobAnalyzeHandler` with `JobAnalyzeHandlerConfig`

### Configuration Loading
The routing system includes sophisticated configuration loading:
1. Load configuration from YAML files (`.ai/config.yaml`)
2. Merge with CLI arguments
3. Apply defaults from Pydantic models
4. Validate and instantiate handler configs

## Middleware Pipeline

The application implements several middleware-like components:

### Logging Middleware
- **Function**: `configure_logging()` in `main.py`
- **Purpose**: Sets up file and console logging per repository
- **Configuration**: Different log levels for file vs console output
- **Location**: Logs stored in `logs/{repo_name}/{date}` structure

### Observability Middleware
- **Langfuse Integration**: Configured via `configure_langfuse()`
- **OpenTelemetry**: Used throughout for tracing agent execution
- **Span Creation**: Each agent run creates spans for monitoring

### Configuration Middleware
- **Config Loading**: Multi-source configuration merging
- **Validation**: Pydantic model validation for all configurations
- **Environment Variables**: Loaded via `config.py` with `.env` support

### Error Handling Middleware
- **Exception Handling**: Try-catch blocks around major operations
- **Graceful Degradation**: Continues execution even if some agents fail
- **Logging**: Comprehensive error logging with context

## Controller/Handler Analysis

The application uses a handler-based architecture with clear separation of concerns:

### Base Handler Structure
- **Abstract Base**: `AbstractHandler` defines the interface
- **Base Implementation**: `BaseHandler` provides common functionality
- **Configuration**: Each handler has associated Pydantic config model

### Handler Implementations

#### AnalyzeHandler (`src/handlers/analyze.py`)
- **Purpose**: Orchestrates multiple analysis agents
- **Configuration**: `AnalyzeHandlerConfig` extends base config with agent options
- **Execution**: Runs multiple agents concurrently using `asyncio.gather()`
- **Agents Managed**:
  - Structure Analyzer
  - Dependency Analyzer  
  - Data Flow Analyzer
  - Request Flow Analyzer
  - API Analyzer

#### ReadmeHandler (`src/handlers/readme.py`)
- **Purpose**: Generates README documentation
- **Configuration**: `ReadmeHandlerConfig` with section exclusion options
- **Execution**: Single documenter agent execution
- **Output**: Writes to `README.md` in repository root

#### JobAnalyzeHandler (`src/handlers/cronjob.py`)
- **Purpose**: Automated analysis for GitLab projects
- **Configuration**: `JobAnalyzeHandlerConfig` with GitLab-specific settings
- **Workflow**:
  1. Fetch projects from GitLab group
  2. Filter applicable projects
  3. Clone repositories
  4. Run analysis
  5. Create merge requests
  6. Cleanup

### Agent Architecture
Each handler delegates to specialized agents:
- **AnalyzerAgent**: Multiple specialized analysis agents
- **DocumenterAgent**: Single documentation generation agent
- **Tool Integration**: Agents use tools for file reading and directory listing

## Authentication & Authorization Flow

The application handles authentication for external services:

### GitLab Authentication
- **OAuth Token**: Configured via `GITLAB_OAUTH_TOKEN` environment variable
- **Usage**: Used in `JobAnalyzeHandler` for GitLab API access
- **Scope**: Repository cloning, branch creation, merge request creation

### LLM Provider Authentication
- **Analyzer LLM**: API key via `ANALYZER_LLM_API_KEY`
- **Documenter LLM**: API key via `DOCUMENTER_LLM_API_KEY`
- **Base URLs**: Configurable endpoints for different providers

### Configuration Security
- **Environment Variables**: Sensitive data loaded from `.env` files
- **No Hardcoding**: All credentials externalized
- **Validation**: Required credentials validated at startup

## Error Handling Pathways

The application implements comprehensive error handling:

### Command-Level Error Handling
```python
try:
    args = parse_args()
except SystemExit as e:
    return e.code
```

### Handler-Level Error Handling
- **Agent Failures**: Individual agent failures don't stop other agents
- **Concurrent Execution**: Uses `return_exceptions=True` in `asyncio.gather()`
- **Validation**: File existence validation after agent completion

### Tool-Level Error Handling
- **File Operations**: `ModelRetry` exceptions for file access issues
- **Permission Errors**: Specific handling for permission denied scenarios
- **Path Validation**: Existence checks before file operations

### GitLab Integration Error Handling
- **Project Processing**: Individual project failures logged but don't stop batch processing
- **Repository Operations**: Cleanup guaranteed via try-finally blocks
- **API Failures**: Comprehensive error logging with project context

### Logging Strategy
- **Structured Logging**: Context-rich log messages with data dictionaries
- **Error Context**: Exception info and stack traces preserved
- **Performance Metrics**: Token usage and execution time tracking

## Request Lifecycle Diagram

```
┌─────────────────┐
│   CLI Command   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Parse Arguments│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Configure Logging│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Load Config    │
│ (YAML + CLI)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Create Handler  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Execute Handler │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Create Agents  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Run Agents      │
│ (Concurrent)    │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Generate Output │
│ (Markdown Files)│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Validate Results│
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   Cleanup &     │
│   Exit          │
└─────────────────┘
```

### Concurrent Agent Execution Flow
For the analyze command, multiple agents run concurrently:

```
AnalyzeHandler
├── Structure Analyzer Agent ──┐
├── Dependency Analyzer Agent ─┤
├── Data Flow Analyzer Agent ──┼── asyncio.gather()
├── Request Flow Analyzer Agent┤
└── API Analyzer Agent ────────┘
```

Each agent follows this internal flow:
1. Initialize with LLM model and tools
2. Render prompt template with configuration
3. Execute agent with tools (file reading, directory listing)
4. Generate markdown output
5. Write to designated file path
6. Log performance metrics and results