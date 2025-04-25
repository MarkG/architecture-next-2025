# CodeValue Architect Assistant (`arch-assist`)

A command-line tool to assist software architects in reverse-engineering existing projects by analyzing code repositories, mapping dependencies, and identifying potential use-cases.

## Features (Current)

*   **Repository Analysis:** Scans directories, identifies Python and JavaScript files.
*   **Dependency Mapping:**
    *   Analyzes `import` statements in Python (using AST).
    *   Analyzes `require` and `import` statements in JavaScript (using Regex).
    *   Builds an internal dependency graph (`networkx`).
    *   Outputs dependency information as a summary, Mermaid diagram, or PlantUML diagram.
*   **Use-Case Identification:** Scans Python and JavaScript code for potential use-case indicators based on function names and comment tags (using Regex).

## Installation

1.  **Prerequisites:**
    *   Python 3.8 or higher.
    *   `pip` (Python package installer).
    *   Git (optional, but recommended for cloning).

2.  **Clone the repository (Optional):**
    ```bash
    git clone <repository-url>
    cd codevalue-architect-assistant
    ```
    *(Replace `<repository-url>` with the actual URL)*

3.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv .venv
    # Activate the environment:
    # Windows (cmd.exe): .venv\Scripts\activate.bat
    # Windows (PowerShell): .venv\Scripts\Activate.ps1
    # Windows (Git Bash): source .venv/Scripts/activate
    # macOS/Linux (bash/zsh): source .venv/bin/activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Install the Tool (Editable Mode Recommended for Development):**
    This makes the `arch-assist` command available in your environment.
    ```bash
    pip install -e .
    ```
    *(Run this from the project root directory where `pyproject.toml` is located)*

## Usage

After installing the tool (preferably in editable mode using `pip install -e .`), you can run it using the `arch-assist` command:

```bash
arch-assist [OPTIONS] COMMAND [ARGS]...
```

**Available Commands:**

*   **`analyze`**: Scans a repository and provides a summary of files and languages.
    ```bash
    arch-assist analyze /path/to/your/repository
    ```

*   **`map-deps`**: Analyzes dependencies and generates a map or diagram.
    ```bash
    # Show summary (default)
    arch-assist map-deps /path/to/your/repository

    # Generate Mermaid diagram (printed to console)
    arch-assist map-deps /path/to/your/repository --format mermaid

    # Generate Mermaid diagram (Top-Down)
    arch-assist map-deps /path/to/your/repository --format mermaid --mermaid-direction TD

    # Generate PlantUML diagram (printed to console)
    arch-assist map-deps /path/to/your/repository --format plantuml
    ```
    *(You can redirect the output `>` to a file, e.g., `... > diagram.md` or `... > diagram.puml`)*

*   **`find-use-cases`**: Scans code for potential use-case indicators.
    ```bash
    arch-assist find-use-cases /path/to/your/repository
    ```

**General Options:**

*   `--version`: Show the version and exit.
*   `--help`: Show help message and exit.

## Development

1.  Follow the installation steps above, including installing in editable mode (`pip install -e .`).
2.  Install development dependencies:
    ```bash
    pip install -r requirements-dev.txt
    ```
3.  Run tests using `pytest`:
    ```bash
    pytest
    ```

## TODO / Future Enhancements

*   Add proper packaging (`setup.py` or `pyproject.toml`).
*   Implement Phase 7: Flow/Sequence Diagram Generation.
*   Improve JavaScript dependency resolution (handle `node_modules`, `package.json`).
*   Improve use-case identification (AST analysis, ML).
*   Add support for more languages.
*   Add framework-specific analysis.
*   Add `--output-file` option for diagrams.
*   Refine CLI options and feedback.
*   Add comprehensive integration tests.

## Contributing

*(Placeholder for contribution guidelines)*

## License

*(Placeholder for license information - e.g., MIT, Apache 2.0)*
