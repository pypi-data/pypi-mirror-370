import os
import sys
import json
import mimetypes
import pathlib
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime

import typer
import pyperclip
import pathspec
import tiktoken
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table
from rich.prompt import Confirm

app = typer.Typer(
    help="An intelligent code context generator that converts project structure and file contents into LLM-friendly format.",
    rich_markup_mode="rich",
    add_completion=True,
)
console = Console()


# Supported encoders
class TokenizerModel(str, Enum):
    CL100K = "cl100k_base"  # GPT-4, GPT-3.5-turbo
    P50K = "p50k_base"  # Codex models
    R50K = "r50k_base"  # GPT-3 models


# Output formats
class OutputFormat(str, Enum):
    STANDARD = "standard"
    MARKDOWN = "markdown"
    JSON = "json"
    XML = "xml"


# Common binary file extensions
BINARY_EXTENSIONS = {
    # Executables
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".app",
    ".deb",
    ".rpm",
    # Compiled files
    ".o",
    ".obj",
    ".a",
    ".lib",
    ".pyc",
    ".pyo",
    ".class",
    ".jar",
    ".war",
    # Archives
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".7z",
    ".rar",
    ".xz",
    # Media files
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".ico",
    ".svg",
    ".webp",
    ".mp3",
    ".mp4",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".mkv",
    ".webm",
    ".wav",
    ".flac",
    ".aac",
    ".ogg",
    # Documents
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    # Databases
    ".db",
    ".sqlite",
    ".sqlite3",
    # Fonts
    ".ttf",
    ".otf",
    ".woff",
    ".woff2",
    ".eot",
    # Others
    ".bin",
    ".dat",
    ".dump",
    ".img",
    ".iso",
}

# Text file extensions (explicitly marked as text)
TEXT_EXTENSIONS = {
    # Code files
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".php",
    ".rb",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".scala",
    ".r",
    ".m",
    ".mm",
    ".sh",
    ".bash",
    ".zsh",
    ".fish",
    ".ps1",
    ".bat",
    ".cmd",
    # Markup languages
    ".html",
    ".htm",
    ".xml",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".config",
    # Documentation
    ".md",
    ".markdown",
    ".rst",
    ".txt",
    ".text",
    ".log",
    # Web
    ".css",
    ".scss",
    ".sass",
    ".less",
    ".vue",
    ".svelte",
    # Configuration
    ".env",
    ".gitignore",
    ".dockerignore",
    ".editorconfig",
    ".eslintrc",
    ".prettierrc",
    ".babelrc",
    # Others
    ".sql",
    ".graphql",
    ".proto",
    ".lock",
}

# Default ignore patterns
DEFAULT_IGNORE_PATTERNS = [
    # Version Control
    ".git/",
    ".svn/",
    ".hg/",
    ".bzr/",
    # IDE & System Files
    ".vscode/",
    ".idea/",
    ".vs/",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini",
    # Python
    "__pycache__/",
    "*.py[cod]",
    "*$py.class",
    "*.so",
    ".Python",
    "*.egg",
    "*.egg-info/",
    ".pytest_cache/",
    ".coverage",
    ".coverage.*",
    "htmlcov/",
    ".tox/",
    ".nox/",
    ".hypothesis/",
    ".mypy_cache/",
    ".dmypy.json",
    "dmypy.json",
    ".pyre/",
    ".ruff_cache/",
    # Virtual Environments
    "env/",
    "venv/",
    "ENV/",
    "env.bak/",
    "venv.bak/",
    ".venv/",
    ".virtualenv/",
    "pipenv/",
    # JavaScript/Node
    "node_modules/",
    "bower_components/",
    "jspm_packages/",
    "npm-debug.log*",
    "yarn-debug.log*",
    "yarn-error.log*",
    "lerna-debug.log*",
    ".npm",
    ".yarn",
    ".pnpm-store/",
    # Build artifacts
    "dist/",
    "build/",
    "target/",
    "out/",
    "_build/",
    "*.o",
    "*.a",
    "*.lib",
    "*.dll",
    "*.exe",
    "*.app",
    # Documentation
    "docs/_build/",
    "site/",
    ".docusaurus/",
    # Logs and databases
    "*.log",
    "*.sql",
    "*.sqlite",
    "*.sqlite3",
    "*.db",
    "*.db-journal",
    # Environment and secrets
    ".env",
    ".env.*",
    "!.env.example",
    "!.env.template",
    ".env.local",
    ".env.*.local",
    "*.pem",
    "*.key",
    "*.cert",
    "*.crt",
    "secrets/",
    # Package manager locks (configurable)
    "poetry.lock",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "uv.lock",
    "Cargo.lock",
    "Gemfile.lock",
    "composer.lock",
    # Media files (configurable)
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.ico",
    "*.pdf",
    "*.zip",
    "*.tar.gz",
    "*.rar",
    "*.7z",
    # This tool's own files
    ".promptignore",
    ".ctxgenrc",
    ".ctxgen/",
]


@dataclass
class FileInfo:
    """File information data class"""

    path: pathlib.Path
    size: int
    tokens: int
    content: str
    is_binary: bool = False
    encoding: str = "utf-8"
    mime_type: Optional[str] = None


@dataclass
class ScanResult:
    """Scan result data class"""

    files: List[FileInfo]
    skipped_files: List[Tuple[pathlib.Path, str]]  # (path, reason)
    total_size: int
    total_tokens: int
    total_files: int
    binary_files_count: int = 0
    scan_time: float = 0.0


@dataclass
class Config:
    """Configuration data class"""

    ignore_patterns: List[str] = field(default_factory=list)
    max_file_size: int = 1024 * 1024  # 1MB
    max_total_tokens: int = 100000
    skip_binary: bool = True
    include_hidden: bool = False
    tokenizer_model: str = "cl100k_base"
    output_format: str = "standard"

    @classmethod
    def from_file(cls, config_file: pathlib.Path) -> "Config":
        """Load configuration from file"""
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                return cls(**config_data)
        return cls()

    def save(self, config_file: pathlib.Path):
        """Save configuration to file"""
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2)


class BinaryFileDetector:
    """Binary file detector"""

    @staticmethod
    def is_binary_by_extension(file_path: pathlib.Path) -> bool:
        """Check if file is binary by extension"""
        return file_path.suffix.lower() in BINARY_EXTENSIONS

    @staticmethod
    def is_text_by_extension(file_path: pathlib.Path) -> bool:
        """Check if file is text by extension"""
        return file_path.suffix.lower() in TEXT_EXTENSIONS

    @staticmethod
    def is_binary_by_content(file_path: pathlib.Path, sample_size: int = 8192) -> bool:
        """Check if file is binary by content"""
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(sample_size)

                # Empty files are treated as text files
                if not chunk:
                    return False

                # Check for NULL bytes
                if b"\x00" in chunk:
                    return True

                # Check proportion of non-text characters
                text_chars = bytearray(
                    {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100))
                )
                non_text_count = sum(1 for byte in chunk if byte not in text_chars)

                # If non-text characters exceed 30%, consider it binary
                return non_text_count / len(chunk) > 0.3

        except Exception:
            return True

    @staticmethod
    def detect(file_path: pathlib.Path) -> Tuple[bool, Optional[str]]:
        """
        Detect if file is binary
        Returns: (is_binary, mime_type)
        """
        # First check if explicitly text file
        if BinaryFileDetector.is_text_by_extension(file_path):
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return False, mime_type

        # Check if explicitly binary file
        if BinaryFileDetector.is_binary_by_extension(file_path):
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return True, mime_type

        # For unknown extensions, check content
        mime_type, _ = mimetypes.guess_type(str(file_path))
        is_binary = BinaryFileDetector.is_binary_by_content(file_path)

        return is_binary, mime_type


class ContextGenerator:
    """Core context generator class"""

    def __init__(self, target_dir: pathlib.Path, config: Optional[Config] = None):
        self.target_dir = target_dir
        self.config = config or Config()
        self.tokenizer = self._init_tokenizer()
        self.stats = {
            "total_files_scanned": 0,
            "files_included": 0,
            "files_skipped": 0,
            "directories_scanned": 0,
        }

    def _init_tokenizer(self):
        """Initialize tokenizer"""
        try:
            return tiktoken.get_encoding(self.config.tokenizer_model)
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to load tiktoken encoder: {e}"
            )
            raise typer.Exit(1)

    def get_ignore_spec(
        self,
        cli_ignore_file: Optional[pathlib.Path] = None,
        no_ignore: bool = False,
        use_default_ignore: bool = False,
    ) -> Tuple[pathspec.PathSpec, str]:
        """Load ignore rules by priority"""
        if no_ignore:
            console.print(
                "⚙️ [yellow]Ignore rules disabled. All files will be included.[/yellow]"
            )
            return pathspec.PathSpec.from_lines(
                "gitwildmatch", []
            ), "Disabled via --no-ignore"

        patterns = []
        source = ""

        # Check configuration file
        config_file = self.target_dir / ".ctxgenrc"
        if config_file.exists() and not use_default_ignore and not cli_ignore_file:
            try:
                config = Config.from_file(config_file)
                if config.ignore_patterns:
                    patterns = config.ignore_patterns
                    source = "Config file: .ctxgenrc"
            except Exception as e:
                console.print(
                    f"[yellow]Warning: Failed to load config file: {e}[/yellow]"
                )

        if not patterns:
            # Priority order processing
            if use_default_ignore:
                source = "Forced built-in defaults"
                patterns = DEFAULT_IGNORE_PATTERNS
            elif cli_ignore_file and cli_ignore_file.is_file():
                source = f"CLI specified: {cli_ignore_file.name}"
                patterns = cli_ignore_file.read_text(encoding="utf-8").splitlines()
            else:
                # Look for ignore files in project
                for ignore_file, desc in [
                    (".promptignore", "Project file: .promptignore"),
                    (".ctxignore", "Project file: .ctxignore"),
                    (".gitignore", "Fallback: .gitignore"),
                ]:
                    ignore_path = self.target_dir / ignore_file
                    if ignore_path.is_file():
                        source = desc
                        patterns = ignore_path.read_text(encoding="utf-8").splitlines()
                        break
                else:
                    source = "Built-in defaults (auto)"
                    patterns = DEFAULT_IGNORE_PATTERNS

        console.print(f"⚙️ [bold blue]Ignore rules source:[/bold blue] {source}")
        return pathspec.PathSpec.from_lines("gitwildmatch", patterns), source

    def should_skip_file(self, file_path: pathlib.Path) -> Optional[str]:
        """
        Check if file should be skipped
        Returns skip reason, or None if not skipped
        """
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size > self.config.max_file_size:
                return f"File too large ({format_size(file_size)})"
        except Exception:
            return "Unable to get file info"

        # Check if hidden file
        if not self.config.include_hidden and file_path.name.startswith("."):
            return "Hidden file"

        # Check if binary file
        if self.config.skip_binary:
            is_binary, _ = BinaryFileDetector.detect(file_path)
            if is_binary:
                return "Binary file"

        return None

    def scan_files(
        self, spec: pathspec.PathSpec
    ) -> Tuple[List[pathlib.Path], List[Tuple[pathlib.Path, str]]]:
        """Scan and filter files"""
        included_files = []
        skipped_files = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Scanning files...", total=None)

            for root, dirs, files in os.walk(self.target_dir, topdown=True):
                root_path = pathlib.Path(root)
                rel_root = root_path.relative_to(self.target_dir)

                self.stats["directories_scanned"] += 1

                # Filter directories
                dirs[:] = [
                    d for d in dirs if not spec.match_file((rel_root / d).as_posix())
                ]

                # Handle hidden directories
                if not self.config.include_hidden:
                    dirs[:] = [d for d in dirs if not d.startswith(".")]

                # Filter files
                for file in files:
                    self.stats["total_files_scanned"] += 1
                    file_path = root_path / file
                    relative_path = file_path.relative_to(self.target_dir)

                    # Check ignore rules
                    if spec.match_file(relative_path.as_posix()):
                        skipped_files.append((relative_path, "Matched ignore pattern"))
                        continue

                    # Check if should skip
                    skip_reason = self.should_skip_file(file_path)
                    if skip_reason:
                        skipped_files.append((relative_path, skip_reason))
                        self.stats["files_skipped"] += 1
                    else:
                        included_files.append(relative_path)
                        self.stats["files_included"] += 1

                    progress.update(
                        task,
                        description=f"[cyan]Scanning files... ({len(included_files)} files found)",
                    )

        return sorted(included_files), skipped_files

    def read_files(self, file_paths: List[pathlib.Path]) -> ScanResult:
        """Read file contents and collect information"""
        import time

        start_time = time.time()

        files = []
        skipped_files = []
        total_size = 0
        total_tokens = 0
        binary_count = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                f"[cyan]Reading {len(file_paths)} files...", total=len(file_paths)
            )

            for rel_path in file_paths:
                progress.update(task, advance=1)

                try:
                    full_path = self.target_dir / rel_path

                    # Detect file type
                    is_binary, mime_type = BinaryFileDetector.detect(full_path)

                    if is_binary and self.config.skip_binary:
                        skipped_files.append(
                            (rel_path, "Binary file (detected during read)")
                        )
                        binary_count += 1
                        continue

                    # Try to read file
                    encoding = "utf-8"
                    content = ""

                    if not is_binary:
                        try:
                            content = full_path.read_text(encoding="utf-8")
                        except UnicodeDecodeError:
                            # Try other encodings
                            for enc in ["latin-1", "cp1252", "gbk"]:
                                try:
                                    content = full_path.read_text(encoding=enc)
                                    encoding = enc
                                    break
                                except UnicodeDecodeError:
                                    continue
                            else:
                                # If all encodings fail, mark as binary
                                is_binary = True
                                skipped_files.append(
                                    (rel_path, "Unable to decode file")
                                )
                                binary_count += 1
                                continue

                    size = full_path.stat().st_size
                    tokens = len(self.tokenizer.encode(content)) if content else 0

                    # Check token limit
                    if total_tokens + tokens > self.config.max_total_tokens:
                        console.print(
                            f"⚠️ [yellow]Token limit reached ({self.config.max_total_tokens:,}), "
                            f"skipping remaining files[/yellow]"
                        )
                        remaining = file_paths[file_paths.index(rel_path) :]
                        for path in remaining:
                            skipped_files.append((path, "Token limit exceeded"))
                        break

                    files.append(
                        FileInfo(
                            path=rel_path,
                            size=size,
                            tokens=tokens,
                            content=content,
                            is_binary=is_binary,
                            encoding=encoding,
                            mime_type=mime_type,
                        )
                    )

                    total_size += size
                    total_tokens += tokens

                    if is_binary:
                        binary_count += 1

                except Exception as e:
                    skipped_files.append((rel_path, f"Read error: {str(e)[:50]}"))

        scan_time = time.time() - start_time

        return ScanResult(
            files=files,
            skipped_files=skipped_files,
            total_size=total_size,
            total_tokens=total_tokens,
            total_files=len(files),
            binary_files_count=binary_count,
            scan_time=scan_time,
        )

    def build_tree_structure(self, files: List[FileInfo]) -> Dict[str, Any]:
        """Build file tree structure"""
        tree = {}
        for file_info in files:
            parts = file_info.path.as_posix().split("/")
            current_level = tree

            for part in parts[:-1]:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

            current_level[parts[-1]] = {
                "size": file_info.size,
                "tokens": file_info.tokens,
                "is_binary": file_info.is_binary,
                "encoding": file_info.encoding,
            }

        return tree


def format_size(size_bytes: int) -> str:
    """Format file size"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f}TB"


def generate_rich_tree(node: Dict[str, Any], tree_obj: Tree) -> None:
    """Generate Rich terminal tree display"""
    sorted_items = sorted(
        node.items(), key=lambda x: (isinstance(x[1], dict) and "size" in x[1], x[0])
    )

    for name, item in sorted_items:
        is_file = isinstance(item, dict) and "size" in item

        if is_file:
            size_str = format_size(item["size"])
            token_count = item["tokens"]
            is_binary = item.get("is_binary", False)
            encoding = item.get("encoding", "utf-8")

            if is_binary:
                icon = "🔒"
                extra = f"[red](binary, {size_str})[/red]"
            else:
                icon = "📄"
                extra = f"[dim]({size_str}, ~{token_count:,} tokens"
                if encoding != "utf-8":
                    extra += f", {encoding}"
                extra += ")[/dim]"

            display_text = f"{icon} {name} {extra}"
            tree_obj.add(display_text)
        else:
            branch = tree_obj.add(f"📂 {name}")
            generate_rich_tree(item, branch)


def generate_string_tree(node: Dict[str, Any], indent: str = "") -> str:
    """Generate plain text tree structure"""
    tree_str = ""
    sorted_items = sorted(
        node.items(), key=lambda x: (isinstance(x[1], dict) and "size" in x[1], x[0])
    )

    for i, (name, item) in enumerate(sorted_items):
        is_last = i == len(sorted_items) - 1
        connector = "└── " if is_last else "├── "

        tree_str += f"{indent}{connector}{name}\n"

        if not (isinstance(item, dict) and "size" in item):
            child_indent = indent + ("    " if is_last else "│   ")
            tree_str += generate_string_tree(item, child_indent)

    return tree_str


def format_output(
    scan_result: ScanResult,
    tree_str: str,
    output_format: OutputFormat,
    target_dir: pathlib.Path,
) -> str:
    """Generate output content in specified format"""

    if output_format == OutputFormat.JSON:
        # JSON format output
        output_data = {
            "project": str(target_dir),
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_files": scan_result.total_files,
                "total_size": scan_result.total_size,
                "total_tokens": scan_result.total_tokens,
                "scan_time": scan_result.scan_time,
            },
            "files": [
                {
                    "path": str(file_info.path),
                    "size": file_info.size,
                    "tokens": file_info.tokens,
                    "encoding": file_info.encoding,
                    "content": file_info.content,
                }
                for file_info in scan_result.files
            ],
        }
        return json.dumps(output_data, indent=2, ensure_ascii=False)

    elif output_format == OutputFormat.XML:
        # XML format output
        from xml.etree.ElementTree import Element, SubElement, tostring
        from xml.dom import minidom

        root = Element("project", name=str(target_dir))

        # Add statistics
        stats = SubElement(root, "statistics")
        SubElement(stats, "total_files").text = str(scan_result.total_files)
        SubElement(stats, "total_size").text = str(scan_result.total_size)
        SubElement(stats, "total_tokens").text = str(scan_result.total_tokens)

        # Add file contents
        files_elem = SubElement(root, "files")
        for file_info in scan_result.files:
            file_elem = SubElement(files_elem, "file")
            SubElement(file_elem, "path").text = str(file_info.path)
            SubElement(file_elem, "size").text = str(file_info.size)
            SubElement(file_elem, "tokens").text = str(file_info.tokens)
            SubElement(file_elem, "content").text = file_info.content

        # Pretty print XML
        xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
        return xml_str

    elif output_format == OutputFormat.MARKDOWN:
        # Markdown format output
        content_parts = [
            f"# Project: {target_dir.name}",
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## Project Structure\n",
            "```",
            tree_str,
            "```\n",
            "## Statistics\n",
            f"- Total files: {scan_result.total_files}",
            f"- Total size: {format_size(scan_result.total_size)}",
            f"- Estimated tokens: {scan_result.total_tokens:,}",
            f"- Scan time: {scan_result.scan_time:.2f} seconds\n",
            "## File Contents\n",
        ]

        for file_info in scan_result.files:
            # Try to detect language
            lang = ""
            suffix_map = {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".java": "java",
                ".cpp": "cpp",
                ".c": "c",
                ".cs": "csharp",
                ".go": "go",
                ".rs": "rust",
                ".rb": "ruby",
                ".php": "php",
                ".swift": "swift",
                ".kt": "kotlin",
                ".scala": "scala",
                ".r": "r",
                ".sql": "sql",
                ".sh": "bash",
                ".yaml": "yaml",
                ".yml": "yaml",
                ".json": "json",
                ".xml": "xml",
                ".html": "html",
                ".css": "css",
                ".md": "markdown",
            }
            lang = suffix_map.get(file_info.path.suffix.lower(), "")

            content_parts.append(f"### {file_info.path}\n")
            content_parts.append(f"```{lang}")
            content_parts.append(file_info.content)
            content_parts.append("```\n")

        return "\n".join(content_parts)

    else:  # STANDARD format
        content_parts = []
        for file_info in scan_result.files:
            content_parts.append(
                f"--- File: {file_info.path.as_posix()} ---\n{file_info.content}"
            )

        return f"Project structure:\n\n{tree_str}\n\nFile contents:\n\n" + "\n\n".join(
            content_parts
        )


def generate_logic(
    target_dir: pathlib.Path,
    ignore_file: Optional[pathlib.Path],
    no_ignore: bool,
    use_default_ignore: bool,
    skip_binary: bool,
    include_hidden: bool,
    max_file_size: Optional[int],
    max_tokens: Optional[int],
    tokenizer: TokenizerModel,
    output_format: OutputFormat,
    output_file: Optional[pathlib.Path],
    show_tree_only: bool,
    show_skipped: bool,
    save_config: bool,
):
    """
    Scan directory, generate project structure and file contents.

    Priority order:
    1. --no-ignore: Disable all ignore rules
    2. --use-default-ignore: Force use of built-in defaults
    3. --ignore-file: Use specified ignore file
    4. .ctxgenrc: Project configuration file
    5. .promptignore/.ctxignore: Project ignore files
    6. .gitignore: Git ignore file
    7. Built-in defaults
    """
    console.print(f"🔍 [bold cyan]Scanning directory:[/bold cyan] {target_dir}")

    # Create configuration
    config = Config(
        max_file_size=max_file_size or 1024 * 1024,
        max_total_tokens=max_tokens or 100000,
        skip_binary=skip_binary,
        include_hidden=include_hidden,
        tokenizer_model=tokenizer.value,
        output_format=output_format.value,
    )

    # Save configuration
    if save_config:
        config_file = target_dir / ".ctxgenrc"
        config.save(config_file)
        console.print(f"✅ [green]Configuration saved to: {config_file}[/green]")

    # Initialize generator
    generator = ContextGenerator(target_dir=target_dir, config=config)

    # Get ignore rules
    spec, source_desc = generator.get_ignore_spec(
        cli_ignore_file=ignore_file,
        no_ignore=no_ignore,
        use_default_ignore=use_default_ignore,
    )

    # Scan files
    file_paths, skipped_in_scan = generator.scan_files(spec)

    if not file_paths:
        console.print("[bold red]Error:[/bold red] No matching files found.")

        if show_skipped and skipped_in_scan:
            console.print("\n[yellow]Skipped files:[/yellow]")
            for path, reason in skipped_in_scan[:20]:  # Show max 20
                console.print(f"  - {path}: {reason}")
            if len(skipped_in_scan) > 20:
                console.print(f"  ... and {len(skipped_in_scan) - 20} more")

        raise typer.Exit(1)

    # Read file contents
    scan_result = generator.read_files(file_paths)

    # Merge skipped files lists
    all_skipped = skipped_in_scan + scan_result.skipped_files

    # Build tree structure
    tree_dict = generator.build_tree_structure(scan_result.files)

    # Generate display tree
    rich_tree = Tree(f"[bold green]Project Structure: {target_dir.name}[/bold green]")
    generate_rich_tree(tree_dict, rich_tree)
    console.print(rich_tree)

    # Show skipped files
    if show_skipped and all_skipped:
        console.print("\n[yellow]Skipped files:[/yellow]")

        # Group by reason
        skip_reasons: Dict[str, List[pathlib.Path]] = {}
        for path, reason in all_skipped:
            if reason not in skip_reasons:
                skip_reasons[reason] = []
            skip_reasons[reason].append(path)

        for reason, paths in skip_reasons.items():
            console.print(f"\n  [bold]{reason}:[/bold] ({len(paths)} files)")
            for path in paths[:5]:  # Show max 5 files per reason
                console.print(f"    - {path}")
            if len(paths) > 5:
                console.print(f"    ... and {len(paths) - 5} more")

    # Generate text tree
    text_tree = generate_string_tree(tree_dict).strip()

    # Generate final content
    if show_tree_only:
        final_content = text_tree
    else:
        final_content = format_output(scan_result, text_tree, output_format, target_dir)

    # Output handling
    success_msg = ""  # Initialize success_msg
    if output_file:
        try:
            output_file.write_text(final_content, encoding="utf-8")
            success_msg = f"✅ [green]Content saved to: {output_file}[/green]"
            console.print(success_msg)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] Failed to write file: {e}")
            raise typer.Exit(1)
    else:
        try:
            pyperclip.copy(final_content)
            success_msg = (
                "✅ [bold green]Context successfully copied to clipboard![/bold green]"
            )
        except pyperclip.PyperclipException:
            console.print(
                "[bold yellow]Warning:[/bold yellow] Unable to access system clipboard."
            )
            # Provide fallback
            temp_file = (
                pathlib.Path.cwd()
                / f"context_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            temp_file.write_text(final_content, encoding="utf-8")
            success_msg = f"✅ [green]Content saved to: {temp_file}[/green]"

    # Display statistics table
    stats_table = Table(
        title="Scan Statistics", show_header=True, header_style="bold cyan"
    )
    stats_table.add_column("Metric", style="cyan", no_wrap=True)
    stats_table.add_column("Value", style="magenta")

    stats_table.add_row(
        "Directories scanned", f"{generator.stats['directories_scanned']:,}"
    )
    stats_table.add_row(
        "Total files scanned", f"{generator.stats['total_files_scanned']:,}"
    )
    stats_table.add_row("Files included", f"{scan_result.total_files:,}")
    stats_table.add_row("Files skipped", f"{len(all_skipped):,}")

    if not skip_binary and scan_result.binary_files_count > 0:
        stats_table.add_row("Binary files", f"{scan_result.binary_files_count:,}")

    stats_table.add_row("Total size", format_size(scan_result.total_size))
    stats_table.add_row("Estimated tokens", f"{scan_result.total_tokens:,}")
    stats_table.add_row("Scan time", f"{scan_result.scan_time:.2f} seconds")

    console.print(stats_table)

    # Display summary
    summary_panel = Panel(
        f"{success_msg}\n"
        f"   [cyan]Ignore source:[/cyan] {source_desc}\n"
        f"   [cyan]Output format:[/cyan] {output_format.value}\n"
        f"   [cyan]Tokenizer:[/cyan] {tokenizer.value}",
        title="[bold]Complete[/bold]",
        border_style="green",
        expand=False,
    )
    console.print(summary_panel)


@app.command()
def generate(
    target_dir: pathlib.Path = typer.Argument(
        ".",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Target directory to scan.",
    ),
    ignore_file: Optional[pathlib.Path] = typer.Option(
        None,
        "--ignore-file",
        "-i",
        help="Explicitly specify an ignore file.",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    no_ignore: bool = typer.Option(
        False,
        "--no-ignore",
        help="Disable all ignore rules.",
        is_flag=True,
    ),
    use_default_ignore: bool = typer.Option(
        False,
        "--use-default-ignore",
        "-d",
        help="Force use of built-in default ignore rules.",
        is_flag=True,
    ),
    skip_binary: bool = typer.Option(
        True,
        "--skip-binary/--include-binary",
        help="Whether to skip binary files. Default: skip.",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        "-a",
        help="Include hidden files and directories (starting with .).",
        is_flag=True,
    ),
    max_file_size: Optional[int] = typer.Option(
        None,
        "--max-file-size",
        "-s",
        help="Maximum size for a single file (bytes). Default: 1MB",
    ),
    max_tokens: Optional[int] = typer.Option(
        None,
        "--max-tokens",
        "-t",
        help="Maximum total token count. Default: 100,000",
    ),
    tokenizer: TokenizerModel = typer.Option(
        TokenizerModel.CL100K,
        "--tokenizer",
        help="Tokenizer model to use.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.STANDARD,
        "--format",
        "-f",
        help="Output format.",
    ),
    output_file: Optional[pathlib.Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output to file instead of clipboard.",
    ),
    show_tree_only: bool = typer.Option(
        False,
        "--tree-only",
        help="Show only file tree structure, no file contents.",
        is_flag=True,
    ),
    show_skipped: bool = typer.Option(
        False,
        "--show-skipped",
        help="Show list of skipped files.",
        is_flag=True,
    ),
    save_config: bool = typer.Option(
        False,
        "--save-config",
        help="Save current configuration to .ctxgenrc file.",
        is_flag=True,
    ),
):
    """
    Scan directory, generate project structure and file contents.
    """
    generate_logic(
        target_dir,
        ignore_file,
        no_ignore,
        use_default_ignore,
        skip_binary,
        include_hidden,
        max_file_size,
        max_tokens,
        tokenizer,
        output_format,
        output_file,
        show_tree_only,
        show_skipped,
        save_config,
    )


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    target_dir: pathlib.Path = typer.Option(
        ".",
        "--target-dir",
        help="Target directory to scan.",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    ignore_file: Optional[pathlib.Path] = typer.Option(
        None,
        "--ignore-file",
        "-i",
        help="Explicitly specify an ignore file.",
        exists=True,
        dir_okay=False,
        resolve_path=True,
    ),
    no_ignore: bool = typer.Option(
        False,
        "--no-ignore",
        help="Disable all ignore rules.",
        is_flag=True,
    ),
    use_default_ignore: bool = typer.Option(
        False,
        "--use-default-ignore",
        "-d",
        help="Force use of built-in default ignore rules.",
        is_flag=True,
    ),
    skip_binary: bool = typer.Option(
        True,
        "--skip-binary/--include-binary",
        help="Whether to skip binary files. Default: skip.",
    ),
    include_hidden: bool = typer.Option(
        False,
        "--include-hidden",
        "-a",
        help="Include hidden files and directories (starting with .).",
        is_flag=True,
    ),
    max_file_size: Optional[int] = typer.Option(
        None,
        "--max-file-size",
        "-s",
        help="Maximum size for a single file (bytes). Default: 1MB",
    ),
    max_tokens: Optional[int] = typer.Option(
        None,
        "--max-tokens",
        "-t",
        help="Maximum total token count. Default: 100,000",
    ),
    tokenizer: TokenizerModel = typer.Option(
        TokenizerModel.CL100K,
        "--tokenizer",
        help="Tokenizer model to use.",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.STANDARD,
        "--format",
        "-f",
        help="Output format.",
    ),
    output_file: Optional[pathlib.Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output to file instead of clipboard.",
    ),
    show_tree_only: bool = typer.Option(
        False,
        "--tree-only",
        help="Show only file tree structure, no file contents.",
        is_flag=True,
    ),
    show_skipped: bool = typer.Option(
        False,
        "--show-skipped",
        help="Show list of skipped files.",
        is_flag=True,
    ),
    save_config: bool = typer.Option(
        False,
        "--save-config",
        help="Save current configuration to .ctxgenrc file.",
        is_flag=True,
    ),
):
    """
    Scan directory, generate project structure and file contents.
    Priority order:
    1. --no-ignore: Disable all ignore rules
    2. --use-default-ignore: Force use of built-in defaults
    3. --ignore-file: Use specified ignore file
    4. .ctxgenrc: Project configuration file
    5. .promptignore/.ctxignore: Project ignore files
    6. .gitignore: Git ignore file
    7. Built-in defaults
    """
    if ctx.invoked_subcommand is None:
        # 执行默认的 generate 逻辑
        generate_logic(
            target_dir,
            ignore_file,
            no_ignore,
            use_default_ignore,
            skip_binary,
            include_hidden,
            max_file_size,
            max_tokens,
            tokenizer,
            output_format,
            output_file,
            show_tree_only,
            show_skipped,
            save_config,
        )


@app.command()
def init(
    target_dir: pathlib.Path = typer.Argument(
        ".",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Target directory to initialize.",
    ),
    interactive: bool = typer.Option(
        True,
        "--interactive/--no-interactive",
        help="Interactive configuration.",
    ),
):
    """Initialize project configuration file"""
    console.print(f"📝 [bold cyan]Initializing configuration:[/bold cyan] {target_dir}")

    config = Config()

    if interactive:
        # Interactive configuration
        from rich.prompt import IntPrompt, Prompt

        # Maximum file size
        config.max_file_size = IntPrompt.ask(
            "Maximum file size (bytes)", default=1024 * 1024
        )

        # Maximum tokens
        config.max_total_tokens = IntPrompt.ask("Maximum total tokens", default=100000)

        # Skip binary files
        config.skip_binary = Confirm.ask("Skip binary files?", default=True)

        # Include hidden files
        config.include_hidden = Confirm.ask("Include hidden files?", default=False)

        # Tokenizer model
        console.print("\nTokenizer model options:")
        console.print("  1. cl100k_base (GPT-4, GPT-3.5)")
        console.print("  2. p50k_base (Codex)")
        console.print("  3. r50k_base (GPT-3)")

        model_choice = Prompt.ask(
            "Choose tokenizer model", choices=["1", "2", "3"], default="1"
        )

        model_map = {"1": "cl100k_base", "2": "p50k_base", "3": "r50k_base"}
        config.tokenizer_model = model_map[model_choice]

    # Create .promptignore file
    promptignore_path = target_dir / ".promptignore"
    if not promptignore_path.exists():
        if not interactive or Confirm.ask("Create .promptignore file?", default=True):
            promptignore_path.write_text(
                "# ctx-gen ignore file\n"
                "# This file uses gitignore syntax\n\n"
                + "\n".join(DEFAULT_IGNORE_PATTERNS),
                encoding="utf-8",
            )
            console.print("✅ [green]Created .promptignore file[/green]")

    # Save configuration
    config_file = target_dir / ".ctxgenrc"
    config.save(config_file)
    console.print(f"✅ [green]Configuration saved to: {config_file}[/green]")

    # Display configuration summary
    console.print("\n[bold]Configuration Summary:[/bold]")
    console.print(f"  Max file size: {format_size(config.max_file_size)}")
    console.print(f"  Max total tokens: {config.max_total_tokens:,}")
    console.print(f"  Skip binary files: {config.skip_binary}")
    console.print(f"  Include hidden files: {config.include_hidden}")
    console.print(f"  Tokenizer model: {config.tokenizer_model}")


@app.command()
def stats(
    target_dir: pathlib.Path = typer.Argument(
        ".",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
        help="Target directory to analyze.",
    ),
):
    """Show project statistics"""
    console.print(f"📊 [bold cyan]Analyzing directory:[/bold cyan] {target_dir}")

    # Statistics data
    file_types: Dict[str, Dict[str, int]] = {}  # extension -> {count, size}
    total_files = 0
    total_size = 0
    binary_files = 0
    text_files = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Analyzing files...", total=None)

        for root, _, files in os.walk(target_dir):
            for file in files:
                file_path = pathlib.Path(root) / file

                try:
                    size = file_path.stat().st_size
                    ext = file_path.suffix.lower() or "(no extension)"

                    if ext not in file_types:
                        file_types[ext] = {"count": 0, "size": 0}

                    file_types[ext]["count"] += 1
                    file_types[ext]["size"] += size

                    total_files += 1
                    total_size += size

                    # Detect file type
                    is_binary, _ = BinaryFileDetector.detect(file_path)
                    if is_binary:
                        binary_files += 1
                    else:
                        text_files += 1

                except Exception:
                    pass

                progress.update(
                    task,
                    description=f"[cyan]Analyzing files... ({total_files} files analyzed)",
                )

    # Sort by file count
    sorted_types = sorted(file_types.items(), key=lambda x: x[1]["count"], reverse=True)

    # Create table
    table = Table(
        title="File Type Statistics", show_header=True, header_style="bold cyan"
    )
    table.add_column("Extension", style="cyan", no_wrap=True)
    table.add_column("Files", style="magenta", justify="right")
    table.add_column("Total Size", style="green", justify="right")
    table.add_column("Avg Size", style="yellow", justify="right")

    # Show top 20
    for ext, stats in sorted_types[:20]:
        avg_size = stats["size"] / stats["count"] if stats["count"] > 0 else 0
        table.add_row(
            ext,
            f"{stats['count']:,}",
            format_size(stats["size"]),
            format_size(int(avg_size)),
        )

    if len(sorted_types) > 20:
        table.add_row("...", f"({len(sorted_types) - 20} more types)", "", "")

    console.print(table)

    # Display overall statistics
    summary = Panel(
        f"[bold]Overall Statistics[/bold]\n\n"
        f"  Total files: {total_files:,}\n"
        f"  Text files: {text_files:,} ({text_files / total_files * 100:.1f}%)\n"
        f"  Binary files: {binary_files:,} ({binary_files / total_files * 100:.1f}%)\n"
        f"  Total size: {format_size(total_size)}\n"
        f"  Average file size: {format_size(int(total_size / total_files) if total_files > 0 else 0)}\n"
        f"  File types: {len(file_types)}",
        border_style="green",
        expand=False,
    )
    console.print(summary)


@app.command()
def version():
    """Show version information"""
    try:
        from importlib.metadata import version as get_version, PackageNotFoundError
    except ImportError:
        # Python 3.7 compatibility
        from importlib_metadata import version as get_version, PackageNotFoundError  # type: ignore
    try:
        ver = get_version("ctx-gen")
    except PackageNotFoundError:
        ver = "Development version"

    # ASCII art title
    title = """
    ╔═══════════════════════════════╗
    ║       ctx-gen  🚀             ║
    ║   Context Generator for LLM   ║
    ╚═══════════════════════════════╝
    """

    console.print(title, style="bold cyan")
    console.print(f"    Version: [bold green]{ver}[/bold green]")
    console.print(f"    Python: {sys.version.split()[0]}")
    console.print(f"    Platform: {sys.platform}")

    # Show dependency versions
    console.print("\n[bold]Dependencies:[/bold]")
    deps = {
        "typer": typer.__version__,
        "rich": "13.0+",
        "tiktoken": "0.5+",
        "pathspec": "0.12+",
        "pyperclip": "1.9+",
    }

    for dep, ver in deps.items():
        console.print(f"  {dep}: {ver}")


if __name__ == "__main__":
    app()
