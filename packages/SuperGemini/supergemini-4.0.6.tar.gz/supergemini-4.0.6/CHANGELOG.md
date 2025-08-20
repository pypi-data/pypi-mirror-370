# Changelog

All notable changes to SuperGemini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.3] - 2025-08-18

### Added
- **SemanticPrompt MCP Server Auto-Installation**: Automatic installation and configuration of semantic-prompt MCP server during SuperGemini setup
- **Enhanced --yes Flag Support**: Auto-selection of default active MCP servers (context7, sequential, playwright, semantic-prompt) when using --yes flag
- **Improved MCP Documentation**: Added comprehensive MCP_SemanticPrompt.md with activation methods and tool information

### Fixed
- **Cross-Platform File Locking**: Resolved Windows permission errors with improved file locking mechanisms and fallback strategies
- **MCP Configuration Reliability**: Enhanced settings.json writing with retry logic and better error handling
- **Installation Robustness**: Improved error handling during MCP server package installation process

### Improved
- **User Experience**: Users can now install SuperGemini with semantic-prompt server automatically included without manual intervention
- **File Operations**: Non-blocking locks with graceful fallback for better cross-platform compatibility
- **Installation Process**: Streamlined MCP server selection and configuration workflow

### Technical Details
- semantic-prompt-mcp@latest package automatically installed via npm during setup
- CHAIN_OF_THOUGHT_CONFIG environment variable automatically configured to use supergemini.json
- Enhanced install.py with auto-selection logic for default MCP servers
- Improved mcp.py with robust cross-platform file operations

## [4.0.2] - 2024-08-18

### Changed
- Agent names standardized across all command configurations
  - `root-cause-analyzer` → `root-cause-analyst`
  - `performance-optimizer` → `performance-engineer`
- Enhanced `/sg:cot` command with universal framework guidance

### Added
- **NEW MCP SERVER**: semantic-prompt MCP integration for intelligent chain-of-thought reasoning
  - 4-step SuperGemini Framework thinking with automatic sg command integration
  - Automatic agent persona extraction and embodiment from TOML files
  - Step 1: Analyze user intent, files involved, expected outcome
  - Step 2: sg Command Selection & TOML Reading (MANDATORY - 90% command preference)
  - Step 3: Agent Persona Extraction & Reading from ~/.gemini/agents/{agents}.md
  - Step 4: Agent Embodiment & Problem Solving Execution with multi-agent coordination
- Automatic `/sg:*` command activation and agent mode integration
- Intelligent TOML document tracking and system-reminder optimization
- supergemini.json configuration for chain-of-thought parameters and framework integration

### Fixed
- Consistent agent naming conventions across all SuperGemini commands
- `/sg:cot` command generalized for universal framework utilization