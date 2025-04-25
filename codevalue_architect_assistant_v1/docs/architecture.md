# Architecture Document: CodeValue Architect Assistant

## 1. Overview

This document describes the proposed architecture for the CodeValue Architect Assistant, a command-line tool for reverse-engineering software projects. The architecture aims for modularity, extensibility, and maintainability.

## 2. Architectural Goals

- **Modularity:** Separate components for distinct functionalities (analysis, mapping, diagramming).
- **Extensibility:** Easy to add support for new languages, frameworks, or analysis techniques.
- **Maintainability:** Clear separation of concerns and well-defined interfaces.
- **Testability:** Components should be independently testable.

## 3. High-Level Architecture

The tool will adopt a modular, layered architecture implemented in Python.

```mermaid
graph LR
    CLI[CLI Interface (argparse/click)] --> Core
    Core[Core Orchestrator] --> ModAnalysis[Repository Analysis Module]
    Core --> ModDeps[Dependency Mapping Module]
    Core --> ModUseCases[Use-Case Identification Module]
    Core --> ModDiagrams[Diagram Generation Module]

    ModAnalysis --> FSUtil[File System Utilities]
    ModAnalysis --> LangDetect[Language Detection]
    ModAnalysis --> Parser[Code Parser (AST/Regex)]

    ModDeps --> Parser
    ModDeps --> GraphLib[Graph Library (NetworkX)]

    ModUseCases --> Parser
    ModUseCases --> PatternMatch[Pattern Matching Engine]

    ModDiagrams --> GraphLib
    ModDiagrams --> TemplateEngine[Diagram Templating (Mermaid/PlantUML)]

    subgraph SharedUtils [Shared Utilities]
        FSUtil
        LangDetect
        Parser
        GraphLib
        TemplateEngine
        PatternMatch
    end

    style CLI fill:#f9f,stroke:#333,stroke-width:2px
    style Core fill:#ccf,stroke:#333,stroke-width:2px
    style ModAnalysis fill:#cfc,stroke:#333,stroke-width:1px
    style ModDeps fill:#cfc,stroke:#333,stroke-width:1px
    style ModUseCases fill:#cfc,stroke:#333,stroke-width:1px
    style ModDiagrams fill:#cfc,stroke:#333,stroke-width:1px
    style SharedUtils fill:#eee,stroke:#999,stroke-width:1px,stroke-dasharray: 5 5
```

## 4. Components

### 4.1. CLI Interface
- **Technology:** Python `argparse` or `click`.
- **Responsibility:** Parses command-line arguments, validates input, and invokes the Core Orchestrator. Handles user feedback and output formatting.

### 4.2. Core Orchestrator
- **Responsibility:** Coordinates the workflow based on the user's command. Initializes and calls the relevant functional modules. Manages data flow between modules.

### 4.3. Repository Analysis Module
- **Responsibility:** Scans directories, identifies files, detects languages (Python/JavaScript initially), and potentially identifies frameworks/libraries. Uses file system utilities and basic parsing.

### 4.4. Dependency Mapping Module
- **Responsibility:** Parses code (using AST or regex for imports/requires) to identify dependencies between files/modules. Builds a dependency graph using a graph library (e.g., NetworkX).

### 4.5. Use-Case Identification Module
- **Responsibility:** Analyzes code structure and potentially comments/documentation strings to identify core functionalities (initially using pattern matching).

### 4.6. Diagram Generation Module
- **Responsibility:** Takes structured data (like the dependency graph or identified flows) and generates textual representations for Mermaid or PlantUML using templating.

### 4.7. Shared Utilities
- **File System Utilities:** Functions for traversing directories, reading files, etc.
- **Language Detection:** Logic to identify the programming language of a file.
- **Code Parser:** Utilities for parsing code (AST for deeper analysis, regex for simpler tasks like finding imports).
- **Graph Library:** Wrapper around NetworkX for creating and manipulating graph structures.
- **Diagram Templating:** Generates Mermaid/PlantUML syntax from data.
- **Pattern Matching Engine:** Logic for finding specific patterns in code relevant to use-cases.

## 5. Data Flow

1.  **CLI:** Receives command (e.g., `analyze <path>`).
2.  **Core:** Invokes `Repository Analysis Module` with the path.
3.  **Analysis Module:** Scans files, detects languages, returns file list and language info.
4.  **Core:** (If command is `map-deps`) Invokes `Dependency Mapping Module` with file list.
5.  **Dependency Module:** Parses files, builds graph, returns graph data.
6.  **Core:** (If command involves diagrams) Invokes `Diagram Generation Module` with graph data.
7.  **Diagram Module:** Generates Mermaid/PlantUML text.
8.  **Core:** Passes results back to CLI for display.

## 6. Technology Choices (Initial)

- **Language:** Python 3.x
- **CLI Framework:** `click` (preferred for its composability)
- **Graphing:** `networkx`
- **Parsing:** Python's built-in `ast` module, `regex`
- **Diagramming:** String templating for Mermaid/PlantUML

## 7. Future Considerations

- Support for more languages (requires extending Parser and Language Detection).
- Integration with specific framework conventions.
- More sophisticated use-case analysis (ML).
- Alternative output formats (e.g., static images via `matplotlib` or `graphviz`).