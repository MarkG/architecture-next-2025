# CodeValue Architect Assistant creation instructions

Create a command line tool called CodeValue Architect Assistant. The tool should assist software architects in reverse engineering existing projects. 

# The main functionalities to be included are as follows:

## Repository Analysis:

Scan and analyze existing code repositories.
Identify and catalog all files, directories, and their contents.
Detect programming languages used and significant libraries/frameworks incorporated in the project.

## Dependency Map Creation:

Analyze dependencies within the project.
Generate a comprehensive dependency map outlining relationships between files, modules, packages, and external libraries.
Present dependency data visually.

## Core Use-Cases Identification:

Identify and summarize core use-cases of the application.
Highlight key functionalities and features of the project.
Offer insights into user interactions and system processes.

## Flow and Sequence Diagram Generation:

Generate flow diagrams to illustrate the overall system processes.
Create sequence diagrams detailing the interactions between different parts of the system over time.
Utilize formats like Mermaid or PlantUML.

## Technical Specifications:

The tool should be developed in a high-level programming language suitable for command line applications, such as Python or Node.js.
Ensure compatibility with popular version control systems such as Git.
Provide options for visual output formats (Mermaid, PlantUML).
Include clear documentation on installation, configuration, and usage.

# Implementation Detail:

## Repository Analysis:

Use libraries like os, pathlib, and subprocess for file system operations and Git integration.
Parse code files to gather language-specific details using regular expressions or AST (Abstract Syntax Tree) parsing.
Dependency Map Creation:

Integrate libraries like networkx for graph creation and matplotlib for visualization (Python) or similar in Node.js.
Detect and map dependencies by analyzing import/require statements and corresponding modules.

## Core Use-Cases Identification:

Apply pattern matching algorithms to discover use-cases within codebases.
Leverage machine learning techniques to highlight key functionalities automatically.

## Flow and Sequence Diagram Generation:

Use text templates to describe Mermaid or PlantUML diagrams.
Convert internal data structures representing the diagrams into textual descriptions for Mermaid/PlantUML.

# Command Line Interface Structure:

Provide commands and flags to specify directories, output formats, and other configurations.
Example commands: arch-assist analyze <repository_path>, arch-assist map-deps <repository_path>, arch-assist find-use-cases <repository_path>, arch-assist generate-diagrams <repository_path> --format mermaid.

# User Experience:

Ensure the tool is user-friendly with clear and concise feedback during operations.
Implement error handling and logging functionalities.
