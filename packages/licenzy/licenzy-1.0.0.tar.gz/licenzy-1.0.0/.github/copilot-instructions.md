<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# 🔑 Licenzy Development Guidelines

## Project Identity
- **Product Name**: Licenzy
- **Core Concept**: Simple, Pythonic license management for AI tools and indie projects
- **Target Audience**: Independent developers, small teams, AI tool builders

## Semantic Conventions
- Use `@licensed` as the primary decorator name
- Core function is `check_license()` - keep it simple and memorable
- Use `license_key` consistently throughout the codebase
- Support aliases: `unlock`, `require_key`, `access_granted` for flexibility

## Code Style
- **Pythonic**: Follow Python conventions and idioms
- **Minimalist**: Clean, simple code with clear purpose
- **Startup-friendly**: Easy to integrate, low friction
- **Emoji Integration**: Use tasteful emojis in docstrings and CLI output for personality
- **Type Hints**: Use comprehensive type annotations for better developer experience

## Architecture Principles
- **Zero Dependencies**: Core functionality should work without external deps (Click only for CLI)
- **Multiple Storage Options**: Support environment variables, home directory, and project files
- **HMAC Validation**: Use secure signature verification for license keys
- **Graceful Degradation**: Show helpful messages when licenses are invalid
- **Development Mode**: Always include bypass mechanisms for development

## API Design
- Keep the main API surface small and intuitive
- Provide both decorator and functional interfaces
- Support method chaining where appropriate
- Use clear, descriptive error messages
- Make common use cases trivial

## Testing Strategy
- Mock external dependencies (file system, environment variables)
- Test both valid and invalid license scenarios
- Include integration tests for CLI commands
- Test all decorator variations and aliases
- Verify HMAC signature generation and validation

## Documentation Style
- Use docstrings with examples for all public functions
- Include emoji in user-facing messages for friendliness
- Provide clear integration examples
- Keep README concise but comprehensive
- Show both simple and advanced usage patterns
