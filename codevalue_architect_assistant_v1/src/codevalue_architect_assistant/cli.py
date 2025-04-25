# -*- coding: utf-8 -*-
"""
Main command-line interface for the CodeValue Architect Assistant.
"""
print("DEBUG: cli.py module loaded") # Added for debugging

import click
import logging
from pathlib import Path
import os # For getting file size
from typing import List # Added for type hinting

# Import necessary components from the project
from .utils.filesystem import scan_repository
from .analysis.language import detect_language
from .analysis.dependency_resolver import resolve_all_dependencies
from .analysis.usecase_finder import find_potential_usecases, UseCaseMatch # Added
from .models import ProjectFile, AnalysisResult, DependencyMap
# Import diagram generators
from .diagrams.mermaid_generator import generate_mermaid_diagram
from .diagrams.plantuml_generator import generate_plantuml_diagram

# Configure basic logging
# Increase level for more detailed output during development if needed
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Function for Core Analysis ---
def _perform_analysis(repository_path: Path) -> AnalysisResult:
    """
    Performs the core repository scanning and file analysis.
    """
    logging.info(f"Performing core analysis for: {repository_path}")
    analysis_result = AnalysisResult(repository_root=repository_path)

    for file_path in scan_repository(repository_path):
        language = detect_language(file_path)
        # Ensure relative_path calculation is robust
        try:
            relative_path = file_path.relative_to(repository_path)
        except ValueError:
             logging.warning(f"File {file_path} seems outside the repository root {repository_path}. Skipping.")
             continue # Skip files outside the root

        size_bytes = None
        try:
            size_bytes = file_path.stat().st_size
        except OSError as e:
            logging.warning(f"Could not get size for file {file_path}: {e}")

        project_file = ProjectFile(
            path=file_path,
            relative_path=relative_path,
            language=language,
            size_bytes=size_bytes
        )
        analysis_result.files.append(project_file)

        if language:
            analysis_result.languages_detected[language] = analysis_result.languages_detected.get(language, 0) + 1

    logging.info(f"Core analysis found {len(analysis_result.files)} files.")
    return analysis_result

# --- CLI Command Group ---
@click.group()
@click.version_option(package_name='codevalue_architect_assistant')
def cli():
    """
    CodeValue Architect Assistant: Analyze and visualize code repositories.
    """
    pass # Entry point for the command group


# --- Analyze Command ---
@cli.command("analyze")
@click.argument(
    "repository_path_str",
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    metavar="REPOSITORY_PATH",
)
def analyze(repository_path_str):
    """
    Analyze a repository: identify files, languages, etc.
    """
    print("DEBUG: Entering analyze function") # Added for debugging
    repository_path = Path(repository_path_str)
    logging.info(f"Starting analysis command for repository: {repository_path}")
    click.echo(f"Analyzing repository at: {repository_path}", err=True) # Use stderr for progress

    try:
        analysis_result = _perform_analysis(repository_path)

        # --- Print Summary ---
        click.echo("-" * 20)
        click.echo(f"Analysis Summary for: {repository_path}")
        click.echo(f"Total files scanned: {len(analysis_result.files)}")
        click.echo("Language Distribution:")
        if analysis_result.languages_detected:
            for lang, count in sorted(analysis_result.languages_detected.items()):
                click.echo(f"  - {lang.capitalize()}: {count}")
        else:
            click.echo("  (No specific languages detected based on extensions)")
        click.echo("-" * 20)

    except Exception as e:
        logging.error(f"An error occurred during analysis: {e}", exc_info=True)
        click.echo(f"Error during analysis: {e}", err=True)

    logging.info(f"Analysis command finished for: {repository_path}")

# --- Map Dependencies Command ---
@cli.command('map-deps')
@click.argument('repository_path_str', type=click.Path(exists=True, file_okay=False, resolve_path=True), metavar='REPOSITORY_PATH')
@click.option(
    '--format', 'output_format',
    type=click.Choice(['summary', 'mermaid', 'plantuml'], case_sensitive=False),
    default='summary',
    help='Output format for the dependency map.'
)
@click.option(
    '--mermaid-direction',
    type=click.Choice(['LR', 'TD', 'RL', 'BT'], case_sensitive=False),
    default='LR',
    help='Direction for Mermaid graph layout (LR, TD, etc.). Only used if format is mermaid.'
)
@click.option(
    '-o', '--output', 'output_file',
    type=click.Path(dir_okay=False, writable=True, resolve_path=True),
    default=None,
    help='Path to save the output diagram (Mermaid/PlantUML). If not provided, prints to console.'
)
def map_deps(repository_path_str, output_format, mermaid_direction, output_file):
    """
    Analyze dependencies (Python & JS) and generate a dependency map or diagram.
    """
    repository_path = Path(repository_path_str)
    logging.info(f"Starting dependency mapping for repository: {repository_path} (Format: {output_format})")
    click.echo(f"Mapping dependencies for repository at: {repository_path}", err=True)

    try:
        # 1. Perform initial analysis
        analysis_result = _perform_analysis(repository_path)
        if not analysis_result.files:
            click.echo("No files found to analyze.", err=True)
            return

        # 2. Resolve Dependencies (Python & JS)
        all_deps = resolve_all_dependencies(analysis_result, repository_path)

        # 3. Build Dependency Map
        dep_map = DependencyMap(repository_root=repository_path)
        for dep in all_deps:
            dep_map.add_dependency(dep)

        # 4. Generate Output based on format
        if output_format == 'summary':
            click.echo("-" * 20)
            click.echo(f"Dependency Map Summary for: {repository_path}")
            click.echo(f"Total Nodes (Files): {dep_map.graph.number_of_nodes()}")
            click.echo(f"Total Edges (Resolved Dependencies): {dep_map.graph.number_of_edges()}")
            click.echo(f"Unresolved Dependencies (External/StdLib/Errors): {len(dep_map.unresolved_dependencies)}")
            if dep_map.unresolved_dependencies:
                 click.echo("  Examples of unresolved:")
                 sorted_unresolved = sorted(dep_map.unresolved_dependencies, key=lambda d: d.source_file)
                 for i, unresolved in enumerate(sorted_unresolved[:10]):
                     click.echo(f"    - {unresolved.target_module} (from {unresolved.source_file})")
                 if len(dep_map.unresolved_dependencies) > 10:
                     click.echo("    - ...")
            click.echo("-" * 20)
        elif output_format in ['mermaid', 'plantuml']:
            output_syntax = ""
            if output_format == 'mermaid':
                output_syntax = generate_mermaid_diagram(dep_map, direction=mermaid_direction)
            elif output_format == 'plantuml':
                output_syntax = generate_plantuml_diagram(dep_map)

            if output_file:
                try:
                    output_path = Path(output_file)
                    output_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
                    output_path.write_text(output_syntax, encoding='utf-8')
                    click.echo(f"Diagram saved to: {output_path}", err=True)
                except Exception as write_err:
                    logging.error(f"Failed to write diagram to {output_file}: {write_err}", exc_info=True)
                    click.echo(f"Error: Failed to write diagram to {output_file}: {write_err}", err=True)
                    # Optionally print to console as fallback?
                    # click.echo("\n--- Diagram Syntax ---")
                    # click.echo(output_syntax)
            else:
                # Print diagram syntax to stdout if no output file specified
                click.echo(output_syntax)

    except Exception as e:
        logging.error(f"An error occurred during dependency mapping: {e}", exc_info=True)
        click.echo(f"Error during dependency mapping: {e}", err=True)

    logging.info(f"Dependency mapping finished for: {repository_path}")

# --- Find Use Cases Command ---
@cli.command('find-use-cases')
@click.argument('repository_path_str', type=click.Path(exists=True, file_okay=False, resolve_path=True), metavar='REPOSITORY_PATH')
def find_use_cases(repository_path_str):
    """
    Find potential use-cases by scanning code for patterns.
    """
    repository_path = Path(repository_path_str)
    logging.info(f"Starting use-case finding for repository: {repository_path}")
    click.echo(f"Scanning for potential use-cases in: {repository_path}", err=True)

    all_matches: List[UseCaseMatch] = []
    processed_files = 0
    supported_languages = PATTERNS_BY_LANG.keys() # Get languages with defined patterns

    try:
        for file_path in scan_repository(repository_path):
            language = detect_language(file_path)
            if language in supported_languages:
                processed_files += 1
                logging.debug(f"Scanning file for use-cases: {file_path}")
                try:
                    # Read file content, handle potential encoding issues
                    content = None
                    encodings_to_try = ['utf-8', 'latin-1']
                    for encoding in encodings_to_try:
                        try:
                            content = file_path.read_text(encoding=encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                        except Exception as read_err:
                             logging.warning(f"Could not read file {file_path} for use-case scan: {read_err}")
                             break # Stop trying encodings for this file

                    if content is not None:
                        relative_path = file_path.relative_to(repository_path)
                        matches = find_potential_usecases(content, relative_path, language)
                        all_matches.extend(matches)
                    else:
                        logging.warning(f"Could not decode file {file_path} for use-case scan.")

                except Exception as scan_err:
                    logging.error(f"Error scanning file {file_path} for use-cases: {scan_err}", exc_info=True)

        # --- Print Results ---
        click.echo("-" * 20)
        click.echo(f"Potential Use-Case Scan Summary for: {repository_path}")
        click.echo(f"Files scanned (Python/JS): {processed_files}")
        click.echo(f"Potential use-case indicators found: {len(all_matches)}")
        click.echo("-" * 20)

        if all_matches:
            # Sort matches for consistent output
            all_matches.sort(key=lambda m: (m.file_path, m.line_number))
            for match in all_matches:
                click.echo(f"{match.file_path}:{match.line_number} [{match.match_type}] => {match.matched_text}")
                # Optionally print context: click.echo(f"  Context: {match.context}")
        else:
            click.echo("No potential use-case indicators found based on current patterns.")


    except Exception as e:
        logging.error(f"An error occurred during use-case finding: {e}", exc_info=True)
        click.echo(f"Error during use-case finding: {e}", err=True)

    logging.info(f"Use-case finding finished for: {repository_path}")


# Add other commands here as they are developed
# @cli.command()
# def generate_diagrams(...): ... # Placeholder for sequence/flow

if __name__ == '__main__':
    print("DEBUG: cli.py running as main script") # Added for debugging
    cli()

# Need to import PATTERNS_BY_LANG from usecase_finder
from .analysis.usecase_finder import PATTERNS_BY_LANG
