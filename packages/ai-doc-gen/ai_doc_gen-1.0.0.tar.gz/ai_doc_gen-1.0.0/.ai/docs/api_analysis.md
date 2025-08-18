# API Documentation

## APIs Served by This Project

### Overview
This project is an AI-powered code documentation generator that provides a command-line interface rather than traditional REST APIs. The system operates through CLI commands and does not expose HTTP endpoints for external consumption.

### Command-Line Interface
The application serves functionality through three main CLI commands:

#### Analyze Command
- **Command**: `ai-doc-gen analyze`
- **Description**: Runs comprehensive code analysis on a repository
- **Parameters**:
  - `--repo-path` (required): Path to the repository to analyze
  - `--exclude-code-structure`: Skip code structure analysis
  - `--exclude-data-flow`: Skip data flow analysis  
  - `--exclude-dependencies`: Skip dependency analysis
  - `--exclude-request-flow`: Skip request flow analysis
  - `--exclude-api-analysis`: Skip API analysis
- **Output**: Creates analysis files in `{repo_path}/.ai/docs/`:
  - `structure_analysis.md`
  - `dependency_analysis.md`
  - `data_flow_analysis.md`
  - `request_flow_analysis.md`
  - `api_analysis.md`

#### Document Command
- **Command**: `ai-doc-gen document`
- **Description**: Generates comprehensive README documentation
- **Parameters**:
  - `--repo-path` (required): Path to the repository
  - Various `--exclude-*` flags for README sections
  - `--use-existing-readme`: Incorporate existing README content
- **Output**: Creates/updates `README.md` in the repository root

#### Cronjob Command
- **Command**: `ai-doc-gen cronjob analyze`
- **Description**: Automated analysis for GitLab projects
- **Parameters**:
  - `--max-days-since-last-commit`: Filter projects by activity (default: 30)
  - `--working-path`: Temporary directory for cloning (default: `/tmp/cronjob/projects`)
  - `--group-project-id`: GitLab group ID to analyze (default: 3)
- **Output**: Creates merge requests with analysis results

### Authentication & Security
- **CLI Access**: No authentication required for local usage
- **GitLab Integration**: Uses OAuth token (`GITLAB_OAUTH_TOKEN`) for repository access
- **LLM Services**: Requires API keys for analyzer and documenter models
- **Observability**: Optional Langfuse integration for monitoring

### Rate Limiting & Constraints
- **LLM API Limits**: Subject to configured model provider rate limits
- **GitLab API**: Standard GitLab API rate limiting applies
- **Parallel Processing**: Configurable parallel tool calls for LLM agents
- **Timeout Settings**: 180-second timeout for LLM requests
- **Token Limits**: 8192 max tokens per LLM response

## External API Dependencies

### LLM Services (Primary Dependencies)

#### Analyzer LLM Service
- **Service Name**: Code Analysis LLM Provider
- **Purpose**: Powers AI agents for code structure, data flow, dependency, request flow, and API analysis
- **Configuration**:
  - Base URL: `ANALYZER_LLM_BASE_URL`
  - API Key: `ANALYZER_LLM_API_KEY`
  - Model: `ANALYZER_LLM_MODEL` (e.g., claude-sonnet-4-20250514)
- **Endpoints Used**: OpenAI-compatible chat completions API
- **Authentication**: Bearer token authentication
- **Error Handling**: 2 retries with exponential backoff
- **Integration Pattern**: Uses pydantic-ai with OpenAI provider

#### Documenter LLM Service  
- **Service Name**: Documentation Generation LLM Provider
- **Purpose**: Generates comprehensive README documentation from analysis results
- **Configuration**:
  - Base URL: `DOCUMENTER_LLM_BASE_URL`
  - API Key: `DOCUMENTER_LLM_API_KEY`
  - Model: `DOCUMENTER_LLM_MODEL`
- **Endpoints Used**: OpenAI-compatible or Gemini API
- **Authentication**: API key authentication
- **Error Handling**: 2 retries with timeout handling
- **Integration Pattern**: Supports both OpenAI and Gemini providers

### GitLab API Integration

#### GitLab REST API
- **Service Name**: GitLab Repository Management
- **Purpose**: Repository cloning, branch management, merge request creation
- **Base URL**: `GITLAB_API_URL` (default: https://git.divar.cloud)
- **Endpoints Used**:
  - `/api/v4/groups/{id}/projects` - List group projects
  - `/api/v4/projects/{id}` - Get project details
  - `/api/v4/projects/{id}/repository/branches` - Branch operations
  - `/api/v4/projects/{id}/merge_requests` - MR management
- **Authentication**: OAuth token (`GITLAB_OAUTH_TOKEN`)
- **Error Handling**: Built-in python-gitlab library error handling
- **Rate Limiting**: Respects GitLab API rate limits
- **Integration Pattern**: Uses python-gitlab library wrapper

### Observability Services

#### Langfuse Integration
- **Service Name**: LLM Observability Platform
- **Purpose**: Monitoring LLM usage, costs, and performance
- **Configuration**:
  - Public Key: `LANGFUSE_PUBLIC_KEY`
  - Secret Key: `LANGFUSE_SECRET_KEY`
  - Host: `LANGFUSE_HOST`
- **Authentication**: Basic auth with encoded credentials
- **Integration Pattern**: OpenTelemetry integration via logfire

#### OpenTelemetry Collector
- **Service Name**: Telemetry Data Collection
- **Purpose**: Distributed tracing and metrics collection
- **Configuration**: `OTEL_EXPORTER_OTLP_ENDPOINT`
- **Authentication**: Header-based authentication
- **Integration Pattern**: Automatic instrumentation via logfire

### Integration Patterns

#### Async Processing
- All LLM interactions use async/await patterns
- Concurrent execution of multiple analysis agents
- Graceful error handling with `asyncio.gather(return_exceptions=True)`

#### Configuration Management
- Environment variable-based configuration
- YAML file overrides for project-specific settings
- Hierarchical configuration merging (defaults → file → CLI args)

#### Error Resilience
- **LLM Retries**: 2 automatic retries for model failures
- **Tool Retries**: 2 retries for file system operations
- **Timeout Handling**: 180-second timeouts for LLM requests
- **Graceful Degradation**: Continues processing even if some agents fail

#### Resource Management
- Temporary directory cleanup for cronjob operations
- Git repository cloning with automatic cleanup
- Memory-efficient file processing with line-based reading

## Available Documentation

### Configuration Documentation
- **File**: `config_example.yaml` - Complete configuration reference
- **File**: `.env.sample` - Environment variable template
- **Quality**: Comprehensive with inline comments and examples

### Agent Prompts
- **Directory**: `src/agents/prompts/`
- **Files**: 
  - `analyzer.yaml` - System and user prompts for analysis agents
  - `documenter.yaml` - Prompts for documentation generation
- **Quality**: Well-structured YAML with detailed prompt engineering

### Code Documentation
- **Type**: Inline docstrings and type hints throughout codebase
- **Coverage**: Comprehensive docstrings for all public methods
- **Quality**: High-quality with examples and parameter descriptions

### Tool Documentation
- **Files**: Individual tool classes with detailed docstrings
- **Coverage**: Complete documentation for file reading and directory listing tools
- **Quality**: Production-ready with error handling documentation

### Integration Guides
- **Docker**: `Dockerfile` provides containerization setup
- **Dependencies**: `pyproject.toml` with complete dependency specifications
- **Quality**: Production-ready configuration files

The project demonstrates excellent documentation practices with comprehensive configuration examples, detailed prompts, and thorough inline documentation suitable for both human developers and AI agents.