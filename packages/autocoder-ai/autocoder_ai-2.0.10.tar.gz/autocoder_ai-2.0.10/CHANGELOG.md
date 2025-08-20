# Changelog

All notable changes to the AutoCoder AI Coding Agent System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-08-19

### Fixed

#### CI/CD Pipeline Issues (Resolves #6, #8, #9, #10)

- **Dependency Conflicts (#8)**: 
  - Migrated all dependencies to Pydantic v2 compatible versions
  - Updated LangChain to latest version (0.3.27) with Pydantic v2 support
  - Fixed httpx version constraint (changed from >=1.0.0 to >=0.27.0)
  - Upgraded all provider libraries to latest compatible versions
  - All dependencies now install cleanly without conflicts across Python 3.10, 3.11, and 3.12

- **Docker Build Issues (#9)**:
  - Updated Dockerfile to use `python:3.11-slim-bookworm` base image for stability
  - Added explicit Debian repository configuration for reliable package installation
  - Implemented retry logic for apt-get operations
  - Used `--no-install-recommends` flag to minimize image size
  - Added proper error handling for package installation failures

- **Playwright E2E Test Issues (#10)**:
  - Fixed Playwright browser installation command (`--with-deps` flag order)
  - Added fallback for libasound2/libasound2t64 package name changes in Ubuntu 24.04
  - Updated CI/CD workflow to properly install system dependencies

- **Docker Compose Syntax (#6)**:
  - Updated all CI/CD workflows to support both `docker compose` (v2) and `docker-compose` (v1) syntax
  - Added fallback commands for backward compatibility

### Enhanced

#### Agent Configuration System (Resolves #3)

- **Comprehensive Agent Configuration**:
  - Implemented `EnhancedAgentConfig` class with full customization support
  - Added ability to edit system prompts via API and UI
  - Implemented per-agent MCP server configuration
  - Added tool management endpoints for agents
  - Created provider-specific configuration support

- **New API Endpoints**:
  - GET `/api/agents` - List all configured agents
  - GET `/api/agents/{id}/config` - Get detailed agent configuration
  - PUT `/api/agents/{id}/config` - Update agent configuration including system prompt
  - POST `/api/agents/{id}/mcp-servers` - Add MCP server to specific agent
  - DELETE `/api/agents/{id}/mcp-servers/{name}` - Remove MCP server from agent
  - GET `/api/agents/{id}/tools` - Get all available tools for an agent

#### Model Provider Support (Resolves #5)

- **Multi-Provider Support**:
  - Verified all LangChain provider libraries are included in requirements.txt
  - Added support for: OpenAI, Anthropic, Google Gemini, Azure OpenAI, Hugging Face, Ollama, LlamaCPP, and OpenAI-compatible endpoints
  - Implemented provider configuration abstraction layer
  - Added automatic API key management from config.yaml

- **Provider Testing Endpoints**:
  - POST `/api/providers/{name}/test` - Test API key and fetch available models
  - Dynamic model discovery for each provider
  - Support for reasoning models and vision models detection

### Added

- **CHANGELOG.md**: This file to track version changes and improvements
- **Enhanced Error Handling**: Better error messages and logging throughout the system
- **Test Coverage**: Comprehensive test suite for all major components

### Technical Details

#### Dependencies Updated
```
langchain>=0.3.27
langchain-community>=0.3.27
langchain-openai>=0.3.30
langchain-anthropic>=0.3.19
langchain-google-genai>=2.0.10
pydantic>=2.11.7
httpx>=0.28.1
fastapi>=0.116.1
```

#### Configuration Structure
The enhanced agent configuration now supports:
- Custom system prompts per agent
- Multiple model providers with fallback options
- Per-agent MCP server configurations
- Tool priority ordering (Agent-specific → Global → Provider-specific)
- Retry strategies and timeout configurations

### Migration Notes

- No breaking changes for existing configurations
- Old configuration format is automatically converted to new enhanced format
- API keys continue to load from config.yaml without environment variables

## [2.0.0] - 2025-08-18

### Added

- CLI improvements with WebSocket support for real-time monitoring
- Enhanced web interface with task detail views
- Authentication system with session management
- Export functionality for projects and tasks
- Package distribution setup (MANIFEST.in, pyproject.toml)

### Fixed

- Modal popup issues on New Project page
- Missing web interface routes for /projects and /new-project
- Modal interaction issues with form submission

## [1.0.0] - 2025-08-17

### Initial Release

- Multi-agent AI system with LangGraph orchestration
- FastAPI web interface
- OpenAI-compatible gateway
- MCP (Model Context Protocol) support
- SQLite database for persistence
- Docker support
