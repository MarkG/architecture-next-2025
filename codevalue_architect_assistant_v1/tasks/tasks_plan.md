# Task Plan: CodeValue Architect Assistant

This document outlines the development tasks for the CodeValue Architect Assistant project.

## Status Legend

- **[TODO]**: Task not started.
- **[WIP]**: Task Work In Progress.
- **[DONE]**: Task completed.
- **[BLOCKED]**: Task blocked by another task or issue.

## Phase 1: Project Setup & Core Infrastructure

- **[DONE]** Setup Python project structure (directories, `__init__.py` files).
- **[DONE]** Initialize Git repository.
- **[TODO]** Setup virtual environment (`venv`). *(Note: This is a manual step for the user)*
- **[DONE]** Create initial `requirements.txt` (add `click`, `networkx`).
- **[DONE]** Implement basic CLI structure using `click` (main entry point, help command).
- **[DONE]** Implement basic logging setup. *(Integrated into cli.py)*
- **[DONE]** Define core data structures (e.g., for representing files, dependencies). *(In models.py)*
- **[DONE]** Create initial unit test setup (`pytest`). *(tests/ directory, requirements-dev.txt)*

## Phase 2: Repository Analysis Module

- **[DONE]** Implement file system utility for recursive directory scanning. *(utils/filesystem.py)*
- **[DONE]** Implement basic file filtering (e.g., ignore `.git`, `node_modules`, `__pycache__`). *(Integrated into scan_repository)*
- **[DONE]** Implement language detection logic for Python (`.py` files). *(analysis/language.py)*
- **[DONE]** Implement language detection logic for JavaScript (`.js`, `.mjs`, `.cjs` files). *(analysis/language.py)*
- **[DONE]** Integrate analysis logic into a `analyze` CLI command. *(cli.py)*
- **[DONE]** Add unit tests for file scanning and language detection. *(tests/utils/test_filesystem.py, tests/analysis/test_language.py)*

## Phase 3: Dependency Mapping Module (Python)

- **[DONE]** Implement Python AST parsing to find `import` and `from ... import` statements. *(analysis/python_parser.py)*
- **[DONE]** Implement logic to resolve module paths (relative and absolute imports within the project scope). *(analysis/dependency_resolver.py)*
- **[DONE]** Build dependency graph using `networkx` based on Python imports. *(Integrated into map-deps command in cli.py)*
- **[DONE]** Add unit tests for Python AST parsing and dependency resolution. *(tests/analysis/test_python_parser.py, tests/analysis/test_dependency_resolver.py)*

## Phase 4: Dependency Mapping Module (JavaScript)

- **[DONE]** Implement Regex parsing to find `require(...)` statements. *(analysis/javascript_parser.py)*
- **[DONE]** Implement Regex parsing to find `import ... from ...` statements (ES Modules). *(analysis/javascript_parser.py)*
- **[DONE]** Implement logic to resolve module paths for JavaScript (relative/absolute within project). *(analysis/dependency_resolver.py)*
- **[DONE]** Update dependency graph logic to handle JavaScript dependencies. *(Integrated via resolve_all_dependencies in cli.py)*
- **[DONE]** Add unit tests for JavaScript Regex parsing and dependency resolution. *(tests/analysis/test_javascript_parser.py, tests/analysis/test_dependency_resolver.py)*

## Phase 5: Diagram Generation Module

- **[DONE]** Create Mermaid diagram template for dependency graphs. *(diagrams/mermaid_generator.py)*
- **[DONE]** Implement function to convert `networkx` graph to Mermaid syntax. *(diagrams/mermaid_generator.py)*
- **[DONE]** Create PlantUML diagram template for dependency graphs. *(diagrams/plantuml_generator.py)*
- **[DONE]** Implement function to convert `networkx` graph to PlantUML syntax. *(diagrams/plantuml_generator.py)*
- **[DONE]** Integrate diagram generation into a `map-deps` CLI command with `--format` option (mermaid/plantuml). *(cli.py)*
- **[DONE]** Add unit tests for diagram generation. *(tests/diagrams/test_mermaid_generator.py, tests/diagrams/test_plantuml_generator.py)*

## Phase 6: Use-Case Identification Module (Initial Pattern Matching)

- **[DONE]** Define initial patterns for identifying potential use-cases in Python (e.g., function names like `handle_request`, `process_order`, comments). *(analysis/usecase_finder.py)*
- **[DONE]** Define initial patterns for identifying potential use-cases in JavaScript. *(analysis/usecase_finder.py)*
- **[DONE]** Implement pattern matching engine using Regex or string searching. *(analysis/usecase_finder.py)*
- **[DONE]** Integrate use-case identification into a `find-use-cases` CLI command. *(cli.py)*
- **[DONE]** Add unit tests for pattern matching. *(tests/analysis/test_usecase_finder.py)*

## Phase 7: Flow/Sequence Diagram Generation (Placeholder)

- **[TODO]** Research methods to automatically infer sequence/flow from code (This is complex, initial implementation might be manual or based on specific annotations).
- **[TODO]** Design data structures to represent flow/sequence information.
- **[TODO]** Implement basic generation of Mermaid/PlantUML sequence diagrams from the designed structures.
- **[TODO]** Integrate into a `generate-diagrams` CLI command (scope TBD).

## Phase 8: Documentation & Refinement

- **[DONE]** Write `README.md` with installation, configuration, and usage instructions.
- **[DONE]** Refine CLI commands, options, and user feedback. *(Added packaging, --output option)*
- **[DONE]** Improve error handling and logging. *(Reviewed, basic handling in place)*
- **[TODO]** Add more comprehensive integration tests.
- **[TODO]** Review and update all core memory files (`@product_requirement_docs.md`, `@architecture.md`, `@technical.md`, `@tasks_plan.md`, `@active_context.md`). *(Deferred until after initial completion)*

## Backlog / Future Enhancements

- **[TODO]** Add support for more languages (e.g., Java, C#, Go).
- **[TODO]** Implement framework-specific analysis (e.g., Django URLs, Flask routes, Express middleware).
- **[TODO]** Improve use-case identification (AST analysis, ML).
- **[TODO]** Add option for static image output for diagrams (matplotlib, graphviz).
- **[TODO]** Implement caching for analysis results.
- **[TODO]** Add configuration file support.
- **[TODO]** Deeper Git integration (e.g., analyze specific commits/branches).