"""
Core models and data structures for mise task management
"""

from typing import Dict, List, Optional, Set, Union, Any
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib
import tomli_w


class TaskDomain(Enum):
    """Core mise task domains"""

    BUILD = "build"
    TEST = "test"
    LINT = "lint"
    DEV = "dev"
    DEPLOY = "deploy"
    DB = "db"
    CI = "ci"
    DOCS = "docs"
    CLEAN = "clean"
    SETUP = "setup"


class TaskComplexity(Enum):
    """Task complexity levels for determining implementation approach"""

    SIMPLE = "simple"  # Single command, inline in TOML
    MODERATE = "moderate"  # Multiple commands, still in TOML
    COMPLEX = "complex"  # Requires file task with script


@dataclass
class TaskDefinition:
    """Represents a mise task definition"""

    name: str
    domain: TaskDomain
    description: str
    run: Union[str, List[str]]
    depends: List[str] = field(default_factory=list)
    depends_post: List[str] = field(default_factory=list)
    wait_for: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)
    dir: Optional[str] = None
    alias: Optional[str] = None
    hide: bool = False
    confirm: Optional[str] = None
    complexity: TaskComplexity = TaskComplexity.SIMPLE
    file_path: Optional[Path] = None  # For file tasks

    @property
    def full_name(self) -> str:
        """Get the full task name with domain prefix"""
        if ":" in self.name:
            return self.name
        return f"{self.domain.value}:{self.name}"

    @property
    def is_file_task(self) -> bool:
        """Check if this is a file-based task"""
        return self.file_path is not None


@dataclass
class MiseConfig:
    """Represents a mise.toml configuration"""

    tools: Dict[str, str] = field(default_factory=dict)
    env: Dict[str, str] = field(default_factory=dict)
    tasks: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    vars: Dict[str, str] = field(default_factory=dict)
    task_config: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def load_from_file(cls, path: Path) -> "MiseConfig":
        """Load mise configuration from a TOML file"""
        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        return cls(
            tools=data.get("tools", {}),
            env=data.get("env", {}),
            tasks=data.get("tasks", {}),
            vars=data.get("vars", {}),
            task_config=data.get("task_config", {}),
        )

    def save_to_file(self, path: Path) -> None:
        """Save mise configuration to a TOML file"""
        data = {}

        if self.tools:
            data["tools"] = self.tools
        if self.env:
            data["env"] = self.env
        if self.tasks:
            data["tasks"] = self.tasks
        if self.vars:
            data["vars"] = self.vars
        if self.task_config:
            data["task_config"] = self.task_config

        with open(path, "wb") as f:
            tomli_w.dump(data, f)


@dataclass
class ProjectStructure:
    """Represents the structure of a project for analysis"""

    root_path: Path
    package_managers: Set[str] = field(default_factory=set)  # npm, cargo, pip, etc.
    languages: Set[str] = field(default_factory=set)  # js, rust, python, etc.
    frameworks: Set[str] = field(default_factory=set)  # react, fastapi, etc.
    has_tests: bool = False
    has_docs: bool = False
    has_ci: bool = False
    has_database: bool = False
    build_artifacts: List[str] = field(default_factory=list)
    source_dirs: List[str] = field(default_factory=list)

    @classmethod
    def analyze(cls, path: Path) -> "ProjectStructure":
        """Analyze a project directory structure"""
        structure = cls(root_path=path)

        # Check for package managers
        if (path / "package.json").exists():
            structure.package_managers.add("npm")
            structure.languages.add("javascript")
        if (path / "Cargo.toml").exists():
            structure.package_managers.add("cargo")
            structure.languages.add("rust")
        if (path / "pyproject.toml").exists() or (path / "setup.py").exists():
            structure.package_managers.add("pip")
            structure.languages.add("python")
        if (path / "go.mod").exists():
            structure.package_managers.add("go")
            structure.languages.add("go")

        # Check for common directories
        if (path / "src").exists():
            structure.source_dirs.append("src")
        if (path / "lib").exists():
            structure.source_dirs.append("lib")
        if (path / "app").exists():
            structure.source_dirs.append("app")

        # Check for tests
        test_dirs = ["tests", "test", "__tests__", "spec"]
        structure.has_tests = any((path / test_dir).exists() for test_dir in test_dirs)

        # Check for docs
        doc_dirs = ["docs", "doc", "documentation"]
        structure.has_docs = any((path / doc_dir).exists() for doc_dir in doc_dirs)

        # Check for CI
        ci_files = [".github/workflows", ".gitlab-ci.yml", "Jenkinsfile", ".circleci"]
        structure.has_ci = any((path / ci_file).exists() for ci_file in ci_files)

        # Check for database
        db_files = ["migrations", "schema.sql", "models", "alembic"]
        structure.has_database = any((path / db_file).exists() for db_file in db_files)

        return structure


@dataclass
class TaskRecommendation:
    """Represents a recommended task to add or modify"""

    task: TaskDefinition
    reasoning: str
    priority: int  # 1-10, higher = more important
    estimated_effort: str  # "low", "medium", "high"
    dependencies_needed: List[str] = field(default_factory=list)
