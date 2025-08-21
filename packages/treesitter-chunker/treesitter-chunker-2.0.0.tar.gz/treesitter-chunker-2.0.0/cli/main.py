from __future__ import annotations

import fnmatch
import json
import os
import sys
import tomllib
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Any

import typer
from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, TimeRemainingColumn
from rich.table import Table

# Ensure language configs are loaded
from chunker import chunk_file, chunk_text
from chunker.exceptions import ChunkerError
from chunker.parser import list_languages

# Import debug commands conditionally
try:
    from .debug import commands as debug_commands
    HAS_DEBUG = True
except ImportError as e:
    if "graphviz" in str(e):
        HAS_DEBUG = False
        DEBUG_ERROR = "graphviz"
    else:
        HAS_DEBUG = False
        DEBUG_ERROR = "unknown"

# Import repo commands
from .repo_command import app as repo_app

app = typer.Typer(help="Tree‑sitter‑based code‑chunker CLI")
console = Console()

if HAS_DEBUG:
    app.add_typer(debug_commands.app, name="debug", help="Debug and visualization tools")
else:
    @app.command()
    def debug():
        """Debug and visualization tools (requires graphviz dependency)"""
        if DEBUG_ERROR == "graphviz":
            console.print("[yellow]Debug commands require the 'viz' extra: pip install treesitter-chunker[viz][/yellow]")
            console.print("[blue]Or install graphviz system package:[/blue]")
            console.print("  Ubuntu/Debian: sudo apt-get install graphviz")
            console.print("  macOS: brew install graphviz")
            console.print("  Windows: choco install graphviz")
        else:
            console.print("[red]Debug commands failed to load: {DEBUG_ERROR}[/red]")
        raise typer.Exit(1)

if TYPE_CHECKING:
    from collections.abc import Iterator

app.add_typer(repo_app, name="repo", help="Repository processing commands")


def load_config(
    config_path: Path | None = None,
    *,
    for_path: Path | None = None,
) -> dict[str, Any]:
    """Load configuration from a `.chunkerrc` file.

    Preference order:
    1) Explicit `config_path` if provided
    2) Nearest `.chunkerrc` found by walking up from `for_path` (file or directory)
    3) Fallback to current working directory, then home directory
    """
    config: dict[str, Any] = {}

    # 1) Explicit path always wins
    if config_path:
        config_files = [config_path]
    else:
        # 2) Determine search roots
        search_roots: list[Path] = []
        if for_path is not None:
            root = for_path if for_path.is_dir() else for_path.parent
            # Walk up to filesystem root
            current = root.resolve()
            while True:
                search_roots.append(current)
                if current.parent == current:
                    break
                current = current.parent
        # 3) Fallbacks
        if not search_roots:
            search_roots = [Path.cwd()]

        config_files = [p / ".chunkerrc" for p in search_roots] + [
            Path.home() / ".chunkerrc",
        ]

    for config_file in config_files:
        if config_file.exists():
            try:
                with Path(config_file).open("rb") as f:
                    config = tomllib.load(f)
                break
            except (
                OSError,
                FileNotFoundError,
                IndexError,
                tomllib.TOMLDecodeError,
            ) as e:
                if not os.environ.get("CHUNKER_QUIET"):
                    console.print(
                        f"[yellow]Warning: Failed to load config from {config_file}: {e}[/yellow]",
                    )

    return config


def get_files_from_patterns(
    patterns: list[str],
    base_path: Path = Path.cwd(),
) -> Iterator[Path]:
    """Get files matching glob patterns."""
    for pattern in patterns:
        # Handle recursive glob patterns
        if "**" in pattern:
            for path in base_path.rglob(pattern.replace("**/", "")):
                if path.is_file():
                    yield path
        else:
            for path in base_path.glob(pattern):
                if path.is_file():
                    yield path


def should_include_file(
    file_path: Path,
    include_patterns: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
) -> bool:
    """Check if file_path should be included based on patterns."""
    file_str = str(file_path)

    # If include patterns specified, file_path must match at least one
    if include_patterns and not any(
        fnmatch.fnmatch(file_str, pattern) for pattern in include_patterns
    ):
        return False

    # If exclude patterns specified, file_path must not match any
    return not (
        exclude_patterns
        and any(fnmatch.fnmatch(file_str, pattern) for pattern in exclude_patterns)
    )


def process_file(
    file_path: Path,
    language: str | None,
    chunk_types: list[str] | None = None,
    min_size: int | None = None,
    max_size: int | None = None,
) -> list[dict[str, Any]]:
    """Process a single file_path and return chunks."""
    # Auto-detect language if not specified
    if not language:
        ext_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".c": "c",
            ".h": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".hpp": "cpp",
            ".rs": "rust",
        }
        ext = file_path.suffix.lower()
        language = ext_map.get(ext)
        if not language:
            return []

    try:
        chunks = chunk_file(file_path, language)
        results = []

        # Debug: print chunk count
        # print(f"DEBUG: Found {len(chunks)} chunks for {file_path}")

        for chunk in chunks:
            # Apply chunk type filter
            if chunk_types and chunk.node_type not in chunk_types:
                continue

            # Apply size filters
            chunk_size = chunk.end_line - chunk.start_line + 1
            if min_size and chunk_size < min_size:
                continue
            if max_size and chunk_size > max_size:
                continue

            results.append(
                {
                    "file_path": str(file_path),
                    "language": language,
                    "node_type": chunk.node_type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "size": chunk_size,
                    "parent_context": chunk.parent_context,
                    "content": chunk.content,
                },
            )

        return results
    except ChunkerError as e:
        console.print(f"[red]Error processing {file_path}: {e}[/red]")
        return []


@app.command()
def chunk(
    file_path: Path | None = typer.Argument(None, exists=True, readable=True),
    *,
    language: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language name (auto-detect if not specified)",
    ),
    json_out: bool = typer.Option(
        False,
        "--json",
        help="Output JSON instead of Rich table",
    ),
    output_format: str = typer.Option(
        "table",
        "--output-format",
        "-o",
        help="Output format: table, json, jsonl, minimal",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Quiet mode - suppress all non-essential output",
    ),
    chunk_types: str | None = typer.Option(
        None,
        "--types",
        "-t",
        help="Comma-separated list of chunk types to include",
    ),
    min_size: int | None = typer.Option(
        None,
        "--min-size",
        help="Minimum chunk size in lines",
    ),
    max_size: int | None = typer.Option(
        None,
        "--max-size",
        help="Maximum chunk size in lines",
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file_path",
    ),
    stdin: bool = typer.Option(
        False,
        "--stdin",
        help="Read source code from stdin instead of file",
    ),
):
    """Chunk a single source file or stdin input."""
    # Check input source
    if stdin:
        # Read from stdin
        content = sys.stdin.read()
        if not language:
            if not quiet:
                console.print(
                    "[red]Error: --lang is required when reading from stdin[/red]",
                )
            sys.exit(1)

        # Use chunk_text from the simplified API
        try:
            chunks = chunk_text(content, language)
            results = []
            # Apply filters
            cfg = load_config(config, for_path=Path.cwd())
            types_list = None
            if chunk_types:
                types_list = [t.strip() for t in chunk_types.split(",")]
            elif "chunk_types" in cfg:
                types_list = cfg["chunk_types"]

            # Get size limits from config if not specified
            if min_size is None and "min_chunk_size" in cfg:
                min_size = cfg["min_chunk_size"]
            if max_size is None and "max_chunk_size" in cfg:
                max_size = cfg["max_chunk_size"]

            for chunk in chunks:
                chunk_size = chunk.end_line - chunk.start_line + 1
                if types_list and chunk.node_type not in types_list:
                    continue
                if min_size and chunk_size < min_size:
                    continue
                if max_size and chunk_size > max_size:
                    continue
                results.append(
                    {
                        "file_path": "<stdin>",
                        "language": language,
                        "node_type": chunk.node_type,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "size": chunk_size,
                        "parent_context": chunk.parent_context,
                        "content": chunk.content,
                    },
                )
        except Exception as e:
            if not quiet:
                console.print(f"[red]Error processing stdin: {e}[/red]")
            sys.exit(1)
    else:
        # Process from file
        if not file_path:
            if not quiet:
                console.print(
                    "[red]Error: Either provide a file path or use --stdin[/red]",
                )
            sys.exit(1)

        # Load config
        # Load config relative to the file being processed
        cfg = load_config(config, for_path=file_path)

        # Parse chunk types
        types_list = None
        if chunk_types:
            types_list = [t.strip() for t in chunk_types.split(",")]
        elif "chunk_types" in cfg:
            types_list = cfg["chunk_types"]

        # Get size limits from config if not specified
        if min_size is None and "min_chunk_size" in cfg:
            min_size = cfg["min_chunk_size"]
        if max_size is None and "max_chunk_size" in cfg:
            max_size = cfg["max_chunk_size"]

        results = process_file(file_path, language, types_list, min_size, max_size)

    # Handle output format
    if json_out or output_format == "json":
        print(json.dumps(results, indent=2))
    elif output_format == "jsonl":
        for result in results:
            print(json.dumps(result, separators=(",", ":")))
    elif output_format == "minimal":
        # Minimal format for easy parsing by other tools
        for chunk in results:
            print(
                f"{chunk['file_path']}:{chunk['start_line']}-{chunk['end_line']}:{chunk['node_type']}",
            )
    elif not quiet:
        # Table format (default)
        tbl = Table(title=f"Chunks in {file_path}")
        tbl.add_column("#", justify="right")
        tbl.add_column("Node")
        tbl.add_column("Lines")
        tbl.add_column("Size", justify="right")
        tbl.add_column("Parent")
        for i, chunk in enumerate(results, 1):
            tbl.add_row(
                str(i),
                chunk["node_type"],
                f"{chunk['start_line']}-{chunk['end_line']}",
                str(chunk["size"]),
                chunk["parent_context"],
            )
        console.print(tbl)

    # Exit with appropriate code
    # For machine-readable outputs (json/jsonl/minimal), do not treat
    # empty results as an error to allow chaining
    if not results and not quiet:
        if not (json_out or output_format in {"json", "jsonl", "minimal"}):
            console.print("[yellow]No chunks found[/yellow]")
            sys.exit(1)


@app.command()
def batch(
    paths: list[Path] | None = typer.Argument(
        None,
        help="Files or directories to process",
    ),
    *,
    pattern: str | None = typer.Option(
        None,
        "--pattern",
        "-p",
        help="Glob pattern for files",
    ),
    language: str | None = typer.Option(
        None,
        "--lang",
        "-l",
        help="Language name (auto-detect if not specified)",
    ),
    json_out: bool = typer.Option(False, "--json", help="Output JSON/JSONL"),
    jsonl: bool = typer.Option(
        False,
        "--jsonl",
        help="Output as JSONL (one JSON per line)",
    ),
    output_format: str = typer.Option(
        "summary",
        "--output-format",
        "-o",
        help="Output format: summary, json, jsonl, minimal, csv",
    ),
    chunk_types: str | None = typer.Option(
        None,
        "--types",
        "-t",
        help="Comma-separated list of chunk types",
    ),
    min_size: int | None = typer.Option(
        None,
        "--min-size",
        help="Minimum chunk size in lines",
    ),
    max_size: int | None = typer.Option(
        None,
        "--max-size",
        help="Maximum chunk size in lines",
    ),
    include: str | None = typer.Option(
        None,
        "--include",
        "-i",
        help="Include file_path patterns (comma-separated)",
    ),
    exclude: str | None = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Exclude file_path patterns (comma-separated)",
    ),
    recursive: bool = typer.Option(
        True,
        "--recursive/--no-recursive",
        "-r/-R",
        help="Recursively process directories",
    ),
    parallel: int | None = typer.Option(
        None,
        "--parallel",
        "-j",
        help="Number of parallel workers",
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to config file_path",
    ),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress progress output"),
    from_stdin: bool = typer.Option(
        False,
        "--stdin",
        help="Read file_path paths from stdin",
    ),
):
    """Process multiple files with batch operations."""
    # Load config
    # For batch, prefer configs relative to provided paths if any
    prefer_path = None
    if paths and len(paths) > 0:
        # Use the first path as the reference for discovering config
        prefer_path = paths[0]
    elif pattern:
        # Use the current working directory for pattern-based discovery
        prefer_path = Path.cwd()
    cfg = load_config(config, for_path=prefer_path)

    # Parse options
    types_list = None
    if chunk_types:
        types_list = [t.strip() for t in chunk_types.split(",")]
    elif "chunk_types" in cfg:
        types_list = cfg["chunk_types"]

    include_patterns = None
    if include:
        include_patterns = [p.strip() for p in include.split(",")]
    elif "include_patterns" in cfg:
        include_patterns = cfg["include_patterns"]

    exclude_patterns = None
    if exclude:
        exclude_patterns = [p.strip() for p in exclude.split(",")]
    elif "exclude_patterns" in cfg:
        exclude_patterns = cfg["exclude_patterns"]

    # Get size limits
    if min_size is None and "min_chunk_size" in cfg:
        min_size = cfg["min_chunk_size"]
    if max_size is None and "max_chunk_size" in cfg:
        max_size = cfg["max_chunk_size"]

    # Get parallel workers
    if parallel is None:
        parallel = cfg.get("parallel_workers", os.cpu_count() or 1)

    # Collect files to process
    files_to_process = []

    if from_stdin:
        # Read file_path paths from stdin
        for line in sys.stdin:
            path = Path(line.strip())
            if (
                path.exists()
                and path.is_file()
                and should_include_file(path, include_patterns, exclude_patterns)
            ):
                files_to_process.append(path)
    # Process provided paths
    elif not paths and pattern:
        # Use pattern to find files
        files_to_process.extend(
            file_path
            for file_path in get_files_from_patterns([pattern])
            if should_include_file(file_path, include_patterns, exclude_patterns)
        )
    elif paths:
        # Process provided paths
        for path in paths:
            if path.is_file() and should_include_file(
                path,
                include_patterns,
                exclude_patterns,
            ):
                files_to_process.append(path)
            elif path.is_dir():
                # Process directory
                if recursive:
                    files_to_process.extend(
                        file_path
                        for file_path in path.rglob("*")
                        if file_path.is_file()
                        and should_include_file(
                            file_path,
                            include_patterns,
                            exclude_patterns,
                        )
                    )
                else:
                    files_to_process.extend(
                        file_path
                        for file_path in path.iterdir()
                        if file_path.is_file()
                        and should_include_file(
                            file_path,
                            include_patterns,
                            exclude_patterns,
                        )
                    )
    else:
        console.print(
            "[red]Error: No files specified. Use paths, --pattern, or --stdin[/red]",
        )
        raise typer.Exit(1)

    if not files_to_process:
        console.print("[yellow]No files to process[/yellow]")
        return

    # Process files
    all_results = []

    def process_with_progress(file_path: Path):
        return process_file(file_path, language, types_list, min_size, max_size)

    if quiet:
        # Process without progress bar
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = {
                executor.submit(process_with_progress, f): f for f in files_to_process
            }
            for future in as_completed(futures):
                results = future.result()
                all_results.extend(results)
    else:
        # Process with progress bar
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            MofNCompleteColumn(),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Processing files...",
                total=len(files_to_process),
            )

            with ThreadPoolExecutor(max_workers=parallel) as executor:
                futures = {
                    executor.submit(process_with_progress, f): f
                    for f in files_to_process
                }
                for future in as_completed(futures):
                    results = future.result()
                    all_results.extend(results)
                    progress.advance(task)

    # Output results based on format
    if jsonl or output_format == "jsonl":
        for result in all_results:
            print(json.dumps(result, separators=(",", ":")))
    elif json_out or output_format == "json":
        print(json.dumps(all_results, indent=2))
    elif output_format == "minimal":
        # Minimal format for easy parsing
        for result in all_results:
            print(
                f"{result['file_path']}:{result['start_line']}-{result['end_line']}:{result['node_type']}",
            )
    elif output_format == "csv":
        # CSV format with headers
        if all_results:
            print(
                "file_path,language,node_type,start_line,end_line,size,parent_context",
            )
            for result in all_results:
                parent = result["parent_context"] or ""
                print(
                    f"{result['file_path']},{result['language']},{result['node_type']},{result['start_line']},{result['end_line']},{result['size']},{parent}",
                )
    elif not quiet:
        # Summary table (default)
        summary = {}
        total_chunks = len(all_results)

        for result in all_results:
            lang = result["language"]
            node_type = result["node_type"]
            key = f"{lang}:{node_type}"
            summary[key] = summary.get(key, 0) + 1

        tbl = Table(
            title=f"Chunk Summary ({total_chunks} total chunks from {len(files_to_process)} files)",
        )
        tbl.add_column("Language", style="cyan")
        tbl.add_column("Node Type", style="green")
        tbl.add_column("Count", justify="right", style="yellow")

        for key in sorted(summary.keys()):
            lang, node_type = key.split(":", 1)
            tbl.add_row(lang, node_type, str(summary[key]))

        console.print(tbl)


@app.command()
def languages():
    """List available languages."""
    try:
        langs = list_languages()
        tbl = Table(title="Available Languages")
        tbl.add_column("Language", style="cyan")
        tbl.add_column("Status", style="green")

        for lang in sorted(langs):
            tbl.add_row(lang, "✓ Available")

        console.print(tbl)
    except (IndexError, KeyError, TypeError) as e:
        console.print(f"[red]Error listing languages: {e}[/red]")


if __name__ == "__main__":
    app()
