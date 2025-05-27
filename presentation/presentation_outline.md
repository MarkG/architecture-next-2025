# Presentation Outline: Building Architect Assistant with Vibe/Agentic Coding

## 1. Introduction to Vibe/Agentic Coding
    - What is Vibe Coding? (Andrej Karpathy quote)
    - Overview of Agentic Coding techniques
    - Why this approach for Architect Assistants?

## 2. The Landscape of AI Coding Tools
    - No-code / Low-code platforms (Lovable, Replit, Base44)
    - IDE-based tools (Cursor, Windsurf)
    - VS Code Extensions (GitHub Copilot, Cline, Roo Code)
    - Command-line tools (Aider, Claude Code, Manus, Codex Cli)
    - Asynchronous Agents (Codex, Claude Code, Google Jules)

## 3. Core Concepts of AI Coding
    - The "Big 3": Context, Model, Prompt
    - Best practices and rules for AI coding

## 4. Architectural Patterns for AI Coding
    - Vertical Slice Architecture:
        - Pros: Organized by feature, single prompt context, minimized cross-cutting concerns, feature-centric
        - Cons: Code duplication, discipline required, poor code reuse

## 5. Architect Assistant: Vision and Functionality
    - Problem statement: Challenges in current software architecture
    - Vision for CodeValue Architect Assistant
    - Core functionalities: reverse engineering, dependency mapping, use-case identification, diagram generation (Mermaid/PlantUML)

## 6. Practical Implementation & Tips
### Naive approach (Approve All)
    - Starting with an initial basic prompt
    - Enhancing prompts (e.g., using PromptPerfect)
    - Naive approach results and lessons learned (token usage, context window)
### Using 
    - Development workflow: plan, feature-by-feature, tests, UI templates
    - Adding context to agents and using MCP servers
    - Setting up Roo Code and Memory Bank
    - Improving Context Usage
      - Claude Code:
        - Project-specific commands
        - Folder structure (.claude, ai_docs, specs)
      - Roo Code: 
        - Memory Bank integration

## 7. Conclusion & Future Outlook
    - Summary of key takeaways
    - Q&A