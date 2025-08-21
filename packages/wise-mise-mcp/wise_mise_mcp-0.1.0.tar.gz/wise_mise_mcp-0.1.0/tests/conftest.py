"""
pytest configuration and shared fixtures for wise-mise-mcp tests
"""

import pytest
import tempfile
import json
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, AsyncMock

from wise_mise_mcp.models import (
    TaskDefinition, 
    TaskDomain, 
    TaskComplexity, 
    MiseConfig, 
    ProjectStructure
)
from wise_mise_mcp.analyzer import TaskAnalyzer
from wise_mise_mcp.manager import TaskManager


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create basic project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        # Create package.json for JavaScript project
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "scripts": {
                "build": "webpack build",
                "test": "jest",
                "dev": "webpack serve",
                "lint": "eslint ."
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "eslint": "^8.0.0",
                "webpack": "^5.0.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
        
        # Create basic .mise.toml
        mise_config = """
[tools]
node = "20"

[env]
NODE_ENV = "development"

[tasks.build]
description = "Build the project"
run = "npm run build"
sources = ["src/**/*", "package.json"]
outputs = ["dist/"]

[tasks.test]
description = "Run tests"
run = "npm test"
sources = ["src/**/*", "tests/**/*"]
depends = ["build"]

[tasks.lint]
description = "Run linting"
run = "npm run lint"
sources = ["src/**/*"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
        
        yield project_path


@pytest.fixture
def sample_task_definition():
    """Create a sample task definition for testing"""
    return TaskDefinition(
        name="test:unit",
        domain=TaskDomain.TEST,
        description="Run unit tests",
        run="pytest tests/unit",
        sources=["src/**/*.py", "tests/unit/**/*.py"],
        outputs=[],
        depends=["build"],
        complexity=TaskComplexity.SIMPLE
    )


@pytest.fixture
def sample_project_structure(temp_project_dir):
    """Create a sample project structure for testing"""
    return ProjectStructure.analyze(temp_project_dir)


@pytest.fixture
def sample_mise_config():
    """Create a sample mise configuration for testing"""
    return MiseConfig(
        tools={"node": "20", "python": "3.11"},
        env={"NODE_ENV": "development"},
        tasks={
            "build": {
                "description": "Build the project",
                "run": "npm run build",
                "sources": ["src/**/*"],
                "outputs": ["dist/"]
            },
            "test": {
                "description": "Run tests", 
                "run": "npm test",
                "depends": ["build"]
            }
        }
    )


@pytest.fixture
def mock_task_analyzer(temp_project_dir):
    """Create a mock task analyzer for testing"""
    analyzer = TaskAnalyzer(temp_project_dir)
    return analyzer


@pytest.fixture
def mock_task_manager(temp_project_dir):
    """Create a mock task manager for testing"""
    manager = TaskManager(temp_project_dir)
    return manager


@pytest.fixture
def complex_project_structure():
    """Create a complex project structure with multiple languages and frameworks"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        
        # Create multi-language project structure
        (project_path / "frontend" / "src").mkdir(parents=True)
        (project_path / "backend" / "src").mkdir(parents=True)
        (project_path / "tests" / "unit").mkdir(parents=True)
        (project_path / "tests" / "integration").mkdir(parents=True)
        (project_path / "docs").mkdir()
        (project_path / ".github" / "workflows").mkdir(parents=True)
        
        # Frontend package.json
        frontend_package = {
            "name": "frontend",
            "version": "1.0.0",
            "scripts": {
                "build": "vite build",
                "test": "vitest",
                "dev": "vite serve",
                "lint": "eslint src",
                "e2e": "playwright test"
            },
            "devDependencies": {
                "vite": "^4.0.0",
                "vitest": "^0.30.0",
                "eslint": "^8.0.0",
                "playwright": "^1.30.0"
            }
        }
        
        with open(project_path / "frontend" / "package.json", "w") as f:
            json.dump(frontend_package, f, indent=2)
        
        # Backend pyproject.toml
        pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "backend"
version = "1.0.0"
dependencies = ["fastapi", "uvicorn"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
"""
        
        with open(project_path / "backend" / "pyproject.toml", "w") as f:
            f.write(pyproject_content.strip())
        
        # Root .mise.toml with complex task structure
        complex_mise_config = """
[tools]
node = "20"
python = "3.11"

[env]
NODE_ENV = "development" 
PYTHONPATH = "backend/src"

[tasks.install]
description = "Install all dependencies"
run = [
    "cd frontend && npm install",
    "cd backend && pip install -e .[dev]"
]

[tasks."build:frontend"]
description = "Build frontend assets"
run = "cd frontend && npm run build"
sources = ["frontend/src/**/*", "frontend/package.json"]
outputs = ["frontend/dist/"]

[tasks."build:backend"]
description = "Build backend package"
run = "cd backend && python -m build"
sources = ["backend/src/**/*.py", "backend/pyproject.toml"]
outputs = ["backend/dist/"]

[tasks.build]
description = "Build entire project"
depends = ["build:frontend", "build:backend"]

[tasks."test:frontend"]
description = "Run frontend unit tests"
run = "cd frontend && npm test"
sources = ["frontend/src/**/*", "frontend/tests/**/*"]

[tasks."test:backend"] 
description = "Run backend unit tests"
run = "cd backend && pytest tests/unit"
sources = ["backend/src/**/*.py", "backend/tests/unit/**/*.py"]

[tasks."test:integration"]
description = "Run integration tests"
run = "pytest tests/integration"
sources = ["frontend/dist/**/*", "backend/src/**/*.py", "tests/integration/**/*.py"]
depends = ["build"]

[tasks."test:e2e"]
description = "Run end-to-end tests"
run = "cd frontend && npm run e2e"
depends = ["build", "dev:backend"]

[tasks.test]
description = "Run all tests"
depends = ["test:frontend", "test:backend", "test:integration"]

[tasks."lint:frontend"]
description = "Lint frontend code"
run = "cd frontend && npm run lint"
sources = ["frontend/src/**/*"]

[tasks."lint:backend"]
description = "Lint backend code"
run = "cd backend && ruff check src"
sources = ["backend/src/**/*.py"]

[tasks."lint:types"]
description = "Check TypeScript and Python types"
run = [
    "cd frontend && npx tsc --noEmit",
    "cd backend && mypy src"
]
sources = ["frontend/src/**/*.ts", "backend/src/**/*.py"]

[tasks.lint]
description = "Run all linting"
depends = ["lint:frontend", "lint:backend", "lint:types"]

[tasks."dev:frontend"]
description = "Start frontend dev server"
run = "cd frontend && npm run dev"

[tasks."dev:backend"] 
description = "Start backend dev server"
run = "cd backend && uvicorn src.main:app --reload"

[tasks.dev]
description = "Start all development servers"
run = "mise run --parallel dev:frontend dev:backend"

[tasks.ci]
description = "Run full CI pipeline"
depends = ["lint", "test", "build"]

[tasks.clean]
description = "Clean build artifacts"
run = [
    "rm -rf frontend/dist",
    "rm -rf backend/dist", 
    "rm -rf backend/build",
    "find . -name '*.pyc' -delete",
    "find . -name '__pycache__' -delete"
]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(complex_mise_config.strip())
        
        yield project_path


@pytest.fixture
def mock_fastmcp_app():
    """Create a mock FastMCP app for testing"""
    mock_app = Mock()
    mock_app.tool = Mock(return_value=lambda f: f)
    mock_app.prompt = Mock(return_value=lambda f: f)
    mock_app.run = AsyncMock()
    return mock_app


class MockDomainExpert:
    """Mock domain expert for testing"""
    
    def __init__(self, domain: TaskDomain):
        self._domain = domain
        
    @property 
    def domain(self) -> TaskDomain:
        return self._domain
        
    def analyze_project(self, structure):
        return []
        
    def can_handle_task(self, description: str) -> bool:
        return self._domain.value in description.lower()


@pytest.fixture
def mock_domain_experts():
    """Create mock domain experts for testing"""
    return [
        MockDomainExpert(TaskDomain.BUILD),
        MockDomainExpert(TaskDomain.TEST), 
        MockDomainExpert(TaskDomain.LINT),
        MockDomainExpert(TaskDomain.DEV)
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests" 
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )


# Test collection configuration
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on location"""
    for item in items:
        # Add unit marker to unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        # Add integration marker to integration tests
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)