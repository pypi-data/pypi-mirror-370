"""Pytest configuration and fixtures for Rxiv-Maker tests."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import pytest

# --- Helper Class for Engine Abstraction ---


class ExecutionEngine:
    """A helper class to abstract command execution."""

    def __init__(self, engine_type: str, container_id: str | None = None):
        self.engine_type = engine_type
        self.container_id = container_id
        print(f"\n✅ Engine initialized: type={self.engine_type}, container_id={self.container_id}")

    def run(self, command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
        """Runs a command in the selected engine."""
        # Extract check parameter, default to True
        check = kwargs.pop("check", True)

        # Extract timeout parameter, default to 600 seconds (10 minutes) for long operations
        timeout = kwargs.pop("timeout", 600)

        # Common kwargs for all engines
        run_kwargs = {"text": True, "capture_output": True, "check": check, "timeout": timeout, **kwargs}

        if self.engine_type == "local":
            return subprocess.run(command, **run_kwargs)

        # Assumes podman commands are compatible with docker for exec
        if self.engine_type in ["docker", "podman"]:
            if self.container_id is None:
                raise ValueError(f"Container ID required for {self.engine_type} engine")

            # For containerized engines, handle cwd by using sh -c with cd
            if "cwd" in kwargs:
                cwd = kwargs.pop("cwd")
                # Remove cwd from run_kwargs since it doesn't apply to host execution of docker
                if "cwd" in run_kwargs:
                    del run_kwargs["cwd"]
                # Properly quote command arguments for shell
                import shlex

                quoted_command = " ".join(shlex.quote(arg) for arg in command)
                # Use sh -c to change directory before executing command
                shell_command = f"cd {shlex.quote(cwd)} && {quoted_command}"
                base_command = [
                    self.engine_type,
                    "exec",
                    self.container_id,
                    "sh",
                    "-c",
                    shell_command,
                ]
                return subprocess.run(base_command, **run_kwargs)
            else:
                base_command = [self.engine_type, "exec", self.container_id]
                full_command = base_command + command
                return subprocess.run(full_command, **run_kwargs)

        raise ValueError(f"Unsupported engine type: {self.engine_type}")

    def rxiv_command(self, *args, **kwargs) -> subprocess.CompletedProcess:
        """Standardized rxiv command execution across engines."""
        import sys

        if self.engine_type == "local":
            try:
                # Try uv run first (modern approach)
                cmd = ["uv", "run", "rxiv"] + list(args)
                return self.run(cmd, **kwargs)
            except (FileNotFoundError, subprocess.CalledProcessError):
                # Fallback to python module
                cmd = [sys.executable, "-m", "rxiv_maker.cli"] + list(args)
                return self.run(cmd, **kwargs)
        else:
            # In containers, rxiv should be installed
            cmd = ["rxiv"] + list(args)
            return self.run(cmd, **kwargs)


# --- Pytest Hooks and Fixtures ---


def pytest_addoption(parser):
    """Adds the --engine command-line option to pytest."""
    parser.addoption(
        "--engine",
        action="store",
        default="local",
        help="Specify the execution engine: local, docker, podman",
    )


@pytest.fixture(scope="session")
def execution_engine(request):
    """
    A session-scoped fixture that sets up and tears down the
    specified execution engine (e.g., a Docker container).
    """
    engine_name = request.config.getoption("--engine")

    if engine_name == "local":
        yield ExecutionEngine("local")
        return

    # --- Containerized Engines (Docker, Podman, etc.) ---
    container_id = None
    try:
        if engine_name in ["docker", "podman"]:
            # Use the existing rxiv-maker base image from Docker Hub
            docker_image = "henriqueslab/rxiv-maker-base:latest"

            print(f"\n🐳 Pulling {engine_name} image: {docker_image}")
            subprocess.run([engine_name, "pull", docker_image], check=True)

            # Run the container in detached mode with workspace mounted
            result = subprocess.run(
                [
                    engine_name,
                    "run",
                    "-d",
                    "--rm",
                    "-v",
                    f"{Path.cwd()}:/workspace",
                    "-w",
                    "/workspace",
                    docker_image,
                    "sleep",
                    "infinity",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            container_id = result.stdout.strip()
            print(f"\n🚀 Started {engine_name} container: {container_id[:12]}")

            # Install rxiv-maker in the container
            print("\n📦 Installing rxiv-maker in container...")
            subprocess.run(
                [
                    engine_name,
                    "exec",
                    container_id,
                    "pip",
                    "install",
                    "-e",
                    "/workspace",
                ],
                check=True,
            )

            yield ExecutionEngine(engine_name, container_id)
        else:
            pytest.fail(f"Unsupported engine: {engine_name}")

    finally:
        if container_id:
            print(f"\n🛑 Stopping {engine_name} container: {container_id[:12]}")
            subprocess.run([engine_name, "stop", container_id], check=False, capture_output=True)


# --- Optimized Temporary Directory Fixtures ---


@pytest.fixture(scope="session")
def session_temp_dir():
    """Session-scoped temporary directory for read-only test data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture(scope="class")
def class_temp_dir():
    """Class-scoped temporary directory for test class isolation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_dir(class_temp_dir):
    """Test-scoped subdirectory within class temp directory."""
    import uuid

    test_dir = class_temp_dir / f"test_{uuid.uuid4().hex[:8]}"
    test_dir.mkdir()
    return test_dir


@pytest.fixture
def sample_markdown():
    """Sample markdown content for testing."""
    return """---
title: "Test Article"
authors:
  - name: "John Doe"
    affiliation: "Test University"
    email: "john@test.com"
keywords: ["test", "article"]
---

# Introduction

This is a test article with **bold** and *italic* text.

## Methods

We used @testcitation2023 for our methodology.

## Results

See @fig:test for results.

![Test Figure](FIGURES/test.png){#fig:test width="0.8"}
"""


@pytest.fixture
def sample_yaml_metadata():
    """Sample YAML metadata for testing."""
    return {
        "title": "Test Article",
        "authors": [
            {
                "name": "John Doe",
                "affiliation": "Test University",
                "email": "john@test.com",
            }
        ],
        "keywords": ["test", "article"],
    }


@pytest.fixture
def sample_tex_template():
    """Sample LaTeX template for testing."""
    return """\\documentclass{article}
\\title{<PY-RPL:LONG-TITLE-STR>}
\\author{<PY-RPL:AUTHORS-AND-AFFILIATIONS>}
\\begin{document}
\\maketitle
\\begin{abstract}
<PY-RPL:ABSTRACT>
\\end{abstract}
<PY-RPL:MAIN-CONTENT>
\\end{document}
"""


# --- Optimized Manuscript Fixtures ---


@pytest.fixture(scope="session")
def example_manuscript_template():
    """Session-scoped read-only reference to EXAMPLE_MANUSCRIPT."""
    return Path("EXAMPLE_MANUSCRIPT")


@pytest.fixture
def example_manuscript_copy(example_manuscript_template, temp_dir):
    """Fast copy of example manuscript using optimized copying."""
    dst = temp_dir / "manuscript"
    copy_tree_optimized(example_manuscript_template, dst)
    return dst


@pytest.fixture(scope="class")
def class_example_manuscript_copy(example_manuscript_template, class_temp_dir):
    """Class-scoped copy of example manuscript for shared use."""
    dst = class_temp_dir / "class_manuscript"
    copy_tree_optimized(example_manuscript_template, dst)
    return dst


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Auto-mark tests based on path patterns to simplify selection and CI runtime."""
    from pathlib import PurePath

    for item in items:
        p = PurePath(item.nodeid)

        # Mark test categories by directory structure
        if "tests/unit/" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.fast)  # Unit tests should be fast

        if "tests/integration/" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)  # Integration tests are typically slower

        if "tests/system/" in item.nodeid:
            item.add_marker(pytest.mark.system)
            item.add_marker(pytest.mark.slow)
            item.add_marker(pytest.mark.ci_exclude)  # System tests excluded from regular CI

        if "tests/cli/" in item.nodeid:
            item.add_marker(pytest.mark.cli)
            item.add_marker(pytest.mark.integration)  # CLI tests are integration-level

        # Mark binary tests (now in system directory)
        if any(pattern in str(p) for pattern in ["test_ci_matrix", "test_end_to_end", "test_package_managers"]):
            item.add_marker(pytest.mark.binary)

        # Mark tests that require specific dependencies
        test_name_lower = item.name.lower()
        test_file = str(p).lower()

        # LaTeX dependency detection
        if (
            "latex" in test_name_lower
            or "pdf" in test_name_lower
            or "pdflatex" in test_name_lower
            or "tex" in test_name_lower
            or "test_install_verification" in test_file
        ):
            item.add_marker(requires_latex)

        # Docker dependency detection
        if "docker" in test_name_lower or "container" in test_name_lower or "docker_engine" in test_file:
            item.add_marker(requires_docker)

        # Podman dependency detection
        if "podman" in test_name_lower or "podman_engine" in test_file:
            item.add_marker(requires_podman)

        # R dependency detection
        if "r_" in test_name_lower or "_r_" in test_name_lower or "test_r" in test_name_lower:
            item.add_marker(requires_r)

        # Heavier or brittle unit tests to exclude by default in CI
        heavy_unit_files = {
            "tests/unit/test_docker_engine_mode.py",
            "tests/unit/test_platform_detector.py",
            "tests/unit/test_figure_generator.py",
            "tests/unit/test_github_actions_integration.py",
            "tests/unit/test_error_handling_scenarios.py",
        }
        if any(str(p).endswith(name) for name in heavy_unit_files):
            item.add_marker(pytest.mark.ci_exclude)

        # Mark slow integration tests that involve network calls or heavy processing
        slow_integration_patterns = {"doi_validation", "network", "api", "download", "install_verification"}
        if any(pattern in test_file for pattern in slow_integration_patterns):
            item.add_marker(pytest.mark.slow)


def copy_tree_optimized(src: Path, dst: Path, use_hardlinks: bool = True):
    """Enhanced optimized tree copying with better hardlink strategy."""
    import os

    dst.mkdir(parents=True, exist_ok=True)

    # Static file extensions that can use hardlinks safely
    STATIC_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".eps", ".gif"}
    # Text file extensions that should be copied (may be modified)
    TEXT_EXTENSIONS = {".md", ".yml", ".yaml", ".bib", ".tex", ".cls", ".bst", ".txt"}

    for item in src.rglob("*"):
        if item.is_file():
            rel_path = item.relative_to(src)
            dst_item = dst / rel_path
            dst_item.parent.mkdir(parents=True, exist_ok=True)

            # Strategy selection based on file type and size
            if use_hardlinks and item.suffix.lower() in STATIC_EXTENSIONS:
                # Use hardlinks for static binary files
                try:
                    os.link(item, dst_item)
                    continue
                except (OSError, AttributeError):
                    pass
            elif item.suffix.lower() in TEXT_EXTENSIONS:
                # Always copy text files (they may be modified)
                shutil.copy2(item, dst_item)
                continue
            elif use_hardlinks and item.stat().st_size > 1024:  # Files > 1KB
                # Use hardlinks for large files to save space/time
                try:
                    os.link(item, dst_item)
                    continue
                except (OSError, AttributeError):
                    pass

            # Fallback to regular copy
            shutil.copy2(item, dst_item)


@pytest.fixture(scope="session")
def minimal_manuscript_template():
    """Session-scoped minimal manuscript template for fast tests."""
    return {
        "config": """title: "Test Article"
authors:
  - name: "Test Author"
    affiliation: "Test University"
    email: "test@example.com"
keywords: ["test"]
""",
        "content": """# Introduction

This is a minimal test manuscript.

## Methods

Simple methodology section.

## Results

Test results here.
""",
        "bibliography": """@article{test2023,
  title={Test Article},
  author={Test Author},
  year={2023}
}""",
    }


@pytest.fixture(scope="session")
def lightweight_manuscript_template():
    """Ultra-lightweight manuscript for fast unit tests."""
    return {
        "config": "title: Fast Test\nauthors: [{name: Test, email: test@test.com}]",
        "content": "# Test\nSimple content.",
        "bibliography": "@article{test2023, title={Test}, year={2023}}",
    }


@pytest.fixture
def fast_manuscript(lightweight_manuscript_template, temp_dir):
    """Create minimal manuscript in <100ms."""
    manuscript_dir = temp_dir / "fast_manuscript"
    manuscript_dir.mkdir()

    # Create files with minimal content
    (manuscript_dir / "00_CONFIG.yml").write_text(lightweight_manuscript_template["config"])
    (manuscript_dir / "01_MAIN.md").write_text(lightweight_manuscript_template["content"])
    (manuscript_dir / "03_REFERENCES.bib").write_text(lightweight_manuscript_template["bibliography"])

    # Create minimal figures directory
    (manuscript_dir / "FIGURES").mkdir()

    return manuscript_dir


@pytest.fixture
def minimal_manuscript(minimal_manuscript_template, temp_dir):
    """Create minimal manuscript in temp directory for fast tests."""
    manuscript_dir = temp_dir / "minimal_manuscript"
    manuscript_dir.mkdir()

    # Create files
    (manuscript_dir / "00_CONFIG.yml").write_text(minimal_manuscript_template["config"])
    (manuscript_dir / "01_MAIN.md").write_text(minimal_manuscript_template["content"])
    (manuscript_dir / "03_REFERENCES.bib").write_text(minimal_manuscript_template["bibliography"])

    # Create basic figures directory
    figures_dir = manuscript_dir / "FIGURES"
    figures_dir.mkdir()

    return manuscript_dir


def check_latex_available():
    """Check if LaTeX is available in the system."""
    try:
        result = subprocess.run(["pdflatex", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_r_available():
    """Check if R is available in the system."""
    try:
        result = subprocess.run(["R", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_docker_available():
    """Check if Docker is available in the system."""
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


def check_podman_available():
    """Check if Podman is available in the system."""
    try:
        result = subprocess.run(["podman", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except (FileNotFoundError, OSError):
        return False


# Markers for conditional test execution
requires_latex = pytest.mark.skipif(not check_latex_available(), reason="LaTeX not available")
requires_r = pytest.mark.skipif(not check_r_available(), reason="R not available")
requires_docker = pytest.mark.skipif(not check_docker_available(), reason="Docker not available")
requires_podman = pytest.mark.skipif(not check_podman_available(), reason="Podman not available")

# Test category markers (don't skip, just mark for selection)
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration  # Already defined by auto-marking
pytest.mark.system = pytest.mark.system
pytest.mark.fast = pytest.mark.fast
pytest.mark.slow = pytest.mark.slow
pytest.mark.performance = pytest.mark.performance
pytest.mark.memory_test = pytest.mark.memory_test
pytest.mark.smoke = pytest.mark.smoke


# --- Class-Scoped Fixtures for Performance ---
# (Already defined above in optimized fixtures section)


@pytest.fixture(scope="class")
def class_manuscript_structure(class_temp_dir):
    """Create a standard manuscript directory structure for the entire test class."""
    manuscript_dir = class_temp_dir / "TEST_MANUSCRIPT"
    manuscript_dir.mkdir()

    # Create FIGURES directory
    figures_dir = manuscript_dir / "FIGURES"
    figures_dir.mkdir()

    class ManuscriptStructure:
        def __init__(self, manuscript_dir, figures_dir, temp_dir):
            self.manuscript_dir = manuscript_dir
            self.figures_dir = figures_dir
            self.temp_dir = temp_dir

        def create_valid_manuscript(self):
            """Create a complete valid manuscript for testing."""
            # Create config file
            config_content = """
title: "Integration Test Article"
authors:
  - name: "Test Author"
    affiliation: "Test University"
    email: "test@example.com"
abstract: "This is a test abstract for integration testing."
keywords: ["test", "integration", "validation"]
"""
            config_file = self.manuscript_dir / "00_CONFIG.yml"
            config_file.write_text(config_content)

            # Create main content file
            main_content = """
# Introduction

This is a test manuscript for integration testing.

## Methods

We used standard testing procedures.

## Results

All tests passed successfully.

## Conclusion

The validation workflow works correctly.
"""
            main_file = self.manuscript_dir / "01_MAIN.md"
            main_file.write_text(main_content)

            # Create bibliography file
            bib_content = """
@article{test2023,
    title = {Test Article for Integration},
    author = {Test Author},
    journal = {Test Journal},
    year = {2023},
    volume = {1},
    number = {1},
    pages = {1--10}
}
"""
            bib_file = self.manuscript_dir / "03_REFERENCES.bib"
            bib_file.write_text(bib_content)

        def create_invalid_manuscript(self):
            """Create an invalid manuscript for testing validation failures."""
            # Create incomplete config file (missing required fields)
            config_content = """
title: "Incomplete Test Article"
# Missing authors, abstract, etc.
"""
            config_file = self.manuscript_dir / "00_CONFIG.yml"
            config_file.write_text(config_content)

            # Create main content with issues
            main_content = """
# Introduction

This manuscript has validation issues.

[Missing reference here](@invalid_citation)

## Methods

Missing proper structure.
"""
            main_file = self.manuscript_dir / "01_MAIN.md"
            main_file.write_text(main_content)

    yield ManuscriptStructure(manuscript_dir, figures_dir, class_temp_dir)


@pytest.fixture(scope="class")
def class_execution_engine(request):
    """Class-scoped execution engine for tests that can share container setup."""
    engine_name = request.config.getoption("--engine")

    if engine_name == "local":
        yield ExecutionEngine("local")
        return

    # --- Containerized Engines (Docker, Podman, etc.) ---
    container_id = None
    try:
        if engine_name in ["docker", "podman"]:
            # Use the existing rxiv-maker base image from Docker Hub
            docker_image = "henriqueslab/rxiv-maker-base:latest"

            print(f"\n🐳 Pulling {engine_name} image: {docker_image}")
            subprocess.run([engine_name, "pull", docker_image], check=True)

            # Run the container in detached mode with workspace mounted
            result = subprocess.run(
                [
                    engine_name,
                    "run",
                    "-d",
                    "-v",
                    f"{Path.cwd()}:/workspace",
                    "--workdir",
                    "/workspace",
                    docker_image,
                    "sleep",
                    "3600",  # Keep container alive for 1 hour
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            container_id = result.stdout.strip()
            print(f"✅ Container started: {container_id[:12]}")

            # Install rxiv-maker in the container
            print("📦 Installing rxiv-maker in container...")
            subprocess.run(
                [
                    engine_name,
                    "exec",
                    container_id,
                    "pip",
                    "install",
                    "-e",
                    "/workspace",
                ],
                check=True,
            )
            print("✅ rxiv-maker installed successfully")

            yield ExecutionEngine(engine_name, container_id)

        else:
            raise ValueError(f"Unsupported engine: {engine_name}")

    finally:
        # Clean up container
        if container_id:
            print(f"\n🧹 Cleaning up container: {container_id[:12]}")
            subprocess.run([engine_name, "rm", "-f", container_id], check=False)


@pytest.fixture(autouse=True)
def test_isolation():
    """Ensure test isolation by cleaning up state."""
    # Pre-test setup
    yield
    # Post-test cleanup
    import gc
    import os

    # Clear any lingering environment variables
    test_env_vars = [var for var in os.environ if var.startswith("RXIV_TEST_")]
    for var in test_env_vars:
        os.environ.pop(var, None)

    # Force garbage collection
    gc.collect()
