"""
Test fixtures for creating sample projects with various configurations
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any


class SampleProjectFactory:
    """Factory for creating various types of sample projects for testing"""
    
    @staticmethod
    def create_simple_javascript_project(project_path: Path) -> None:
        """Create a simple JavaScript project with basic tasks"""
        # Create directory structure
        (project_path / "src").mkdir(parents=True)
        (project_path / "tests").mkdir(parents=True)
        (project_path / "public").mkdir(parents=True)
        
        # Create package.json
        package_json = {
            "name": "simple-js-app",
            "version": "1.0.0",
            "description": "A simple JavaScript application",
            "main": "src/index.js",
            "scripts": {
                "build": "webpack --mode=production",
                "dev": "webpack serve --mode=development", 
                "test": "jest",
                "lint": "eslint src/"
            },
            "dependencies": {
                "lodash": "^4.17.21"
            },
            "devDependencies": {
                "webpack": "^5.88.0",
                "webpack-cli": "^5.1.4",
                "webpack-dev-server": "^4.15.1",
                "jest": "^29.5.0",
                "eslint": "^8.44.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
            
        # Create .mise.toml
        mise_config = """
[tools]
node = "20"

[env]
NODE_ENV = "development"

[tasks.install]
description = "Install dependencies"
run = "npm install"

[tasks.build]
description = "Build for production"
run = "npm run build"
sources = ["src/**/*", "package.json", "webpack.config.js"]
outputs = ["dist/"]
depends = ["install"]

[tasks.test]
description = "Run test suite"
run = "npm test"
sources = ["src/**/*", "tests/**/*"]
depends = ["install"]

[tasks.dev]
description = "Start development server"
run = "npm run dev"
depends = ["install"]

[tasks.lint]
description = "Run ESLint"
run = "npm run lint"
sources = ["src/**/*", ".eslintrc.*"]
depends = ["install"]

[tasks.ci]
description = "Run CI pipeline"
depends = ["lint", "test", "build"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
        # Create sample source files
        (project_path / "src" / "index.js").write_text("""
const _ = require('lodash');

function greet(name) {
    return `Hello, ${_.capitalize(name)}!`;
}

module.exports = { greet };
""")
        
        (project_path / "tests" / "index.test.js").write_text("""
const { greet } = require('../src/index');

describe('greet function', () => {
    test('should greet with capitalized name', () => {
        expect(greet('world')).toBe('Hello, World!');
    });
    
    test('should handle empty name', () => {
        expect(greet('')).toBe('Hello, !');
    });
});
""")
        
        # Create webpack config
        (project_path / "webpack.config.js").write_text("""
const path = require('path');

module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dist'),
    },
    devServer: {
        contentBase: './public',
        port: 3000,
    },
};
""")
    
    @staticmethod
    def create_python_project(project_path: Path) -> None:
        """Create a Python project with pyproject.toml"""
        # Create directory structure
        (project_path / "src" / "mypackage").mkdir(parents=True)
        (project_path / "tests").mkdir(parents=True)
        (project_path / "docs").mkdir(parents=True)
        
        # Create pyproject.toml
        pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mypackage"
version = "0.1.0"
description = "A sample Python package"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Test Author", email = "test@example.com"}
]
dependencies = [
    "requests>=2.25.0",
    "click>=8.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "black>=23.0.0"
]

[project.scripts]
mypackage = "mypackage.cli:main"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=mypackage --cov-report=html --cov-report=term-missing"

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.black]
line-length = 100
target-version = ['py311']
"""
        
        with open(project_path / "pyproject.toml", "w") as f:
            f.write(pyproject_content.strip())
            
        # Create .mise.toml
        mise_config = """
[tools]
python = "3.11"

[env]
PYTHONPATH = "src"

[tasks.install]
description = "Install package in development mode"
run = "pip install -e .[dev]"

[tasks.build]
description = "Build wheel package"
run = "python -m build"
sources = ["src/**/*.py", "pyproject.toml", "README.md"]
outputs = ["dist/"]
depends = ["install"]

[tasks.test]
description = "Run test suite with coverage"
run = "pytest"
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks."test:watch"]
description = "Run tests in watch mode"
run = "pytest-watch"
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks.lint]
description = "Run code linting"
run = [
    "ruff check src tests",
    "mypy src"
]
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks.format]
description = "Format code with black"
run = "black src tests"
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks."format:check"]
description = "Check code formatting"
run = "black --check src tests"
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks.clean]
description = "Clean build artifacts"
run = [
    "rm -rf build/",
    "rm -rf dist/",
    "rm -rf *.egg-info/",
    "find . -name '__pycache__' -exec rm -rf {} +",
    "find . -name '*.pyc' -delete"
]

[tasks.ci]
description = "Run full CI pipeline"
depends = ["lint", "format:check", "test", "build"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
        # Create source files
        (project_path / "src" / "mypackage" / "__init__.py").write_text("""
'''A sample Python package'''

__version__ = "0.1.0"

from .core import hello_world

__all__ = ["hello_world"]
""")
        
        (project_path / "src" / "mypackage" / "core.py").write_text("""
'''Core functionality for mypackage'''

import requests
from typing import str


def hello_world(name: str = "World") -> str:
    '''Return a greeting message'''
    return f"Hello, {name}!"


def fetch_data(url: str) -> dict:
    '''Fetch data from a URL'''
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
""")
        
        (project_path / "src" / "mypackage" / "cli.py").write_text("""
'''Command line interface for mypackage'''

import click
from .core import hello_world


@click.command()
@click.option('--name', default='World', help='Name to greet')
def main(name: str) -> None:
    '''Main CLI entry point'''
    click.echo(hello_world(name))


if __name__ == '__main__':
    main()
""")
        
        # Create test files
        (project_path / "tests" / "__init__.py").touch()
        
        (project_path / "tests" / "test_core.py").write_text("""
'''Tests for core functionality'''

import pytest
from unittest.mock import Mock, patch
from mypackage.core import hello_world, fetch_data


def test_hello_world_default():
    '''Test hello_world with default name'''
    result = hello_world()
    assert result == "Hello, World!"


def test_hello_world_custom_name():
    '''Test hello_world with custom name'''
    result = hello_world("Python")
    assert result == "Hello, Python!"


@patch('mypackage.core.requests.get')
def test_fetch_data_success(mock_get):
    '''Test successful data fetching'''
    # Setup mock
    mock_response = Mock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    # Test
    result = fetch_data("https://api.example.com/data")
    
    # Verify
    assert result == {"key": "value"}
    mock_get.assert_called_once_with("https://api.example.com/data")


@patch('mypackage.core.requests.get')
def test_fetch_data_http_error(mock_get):
    '''Test handling of HTTP errors'''
    # Setup mock
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
    mock_get.return_value = mock_response
    
    # Test
    with pytest.raises(requests.HTTPError):
        fetch_data("https://api.example.com/notfound")
""")
        
        # Create README
        (project_path / "README.md").write_text("""
# MyPackage

A sample Python package for demonstration purposes.

## Installation

```bash
pip install -e .
```

## Usage

```python
from mypackage import hello_world

print(hello_world("Python"))
```

## Development

```bash
# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run linting
ruff check src tests
mypy src

# Format code
black src tests
```
""")
    
    @staticmethod
    def create_rust_project(project_path: Path) -> None:
        """Create a Rust project with Cargo.toml"""
        # Create directory structure
        (project_path / "src").mkdir(parents=True)
        (project_path / "tests").mkdir(parents=True)
        (project_path / "benches").mkdir(parents=True)
        (project_path / "examples").mkdir(parents=True)
        
        # Create Cargo.toml
        cargo_toml = """
[package]
name = "rust-app"
version = "0.1.0"
edition = "2021"
description = "A sample Rust application"
license = "MIT"
repository = "https://github.com/example/rust-app"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
clap = { version = "4.0", features = ["derive"] }

[dev-dependencies]
criterion = "0.5"
tempfile = "3.0"

[[bin]]
name = "rust-app"
path = "src/main.rs"

[[bench]]
name = "benchmarks"
harness = false

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
"""
        
        with open(project_path / "Cargo.toml", "w") as f:
            f.write(cargo_toml.strip())
            
        # Create .mise.toml
        mise_config = """
[tools]
rust = "1.75"

[tasks.install]
description = "Fetch dependencies"
run = "cargo fetch"

[tasks.build]
description = "Build debug version"
run = "cargo build"
sources = ["src/**/*.rs", "Cargo.toml"]
outputs = ["target/debug/"]

[tasks."build:release"]
description = "Build optimized release version"
run = "cargo build --release"
sources = ["src/**/*.rs", "Cargo.toml"]
outputs = ["target/release/"]
depends = ["test", "lint"]

[tasks.test]
description = "Run test suite"
run = "cargo test"
sources = ["src/**/*.rs", "tests/**/*.rs"]

[tasks."test:integration"]
description = "Run integration tests"
run = "cargo test --test '*'"
sources = ["src/**/*.rs", "tests/**/*.rs"]

[tasks.lint]
description = "Run Clippy linter"
run = "cargo clippy -- -D warnings"
sources = ["src/**/*.rs"]

[tasks.format]
description = "Format code with rustfmt"
run = "cargo fmt"
sources = ["src/**/*.rs"]

[tasks."format:check"]
description = "Check code formatting"
run = "cargo fmt -- --check"
sources = ["src/**/*.rs"]

[tasks.doc]
description = "Generate documentation"
run = "cargo doc --no-deps"
sources = ["src/**/*.rs"]
outputs = ["target/doc/"]

[tasks.bench]
description = "Run benchmarks"
run = "cargo bench"
sources = ["src/**/*.rs", "benches/**/*.rs"]
depends = ["build:release"]

[tasks.clean]
description = "Clean build artifacts"
run = "cargo clean"

[tasks.ci]
description = "Run full CI pipeline"
depends = ["lint", "format:check", "test", "build:release"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
        # Create source files
        (project_path / "src" / "main.rs").write_text("""
use clap::Parser;

mod lib;

use lib::greet;

#[derive(Parser)]
#[command(name = "rust-app")]
#[command(about = "A sample Rust application")]
struct Cli {
    /// Name to greet
    #[arg(short, long, default_value = "World")]
    name: String,
    
    /// Number of times to greet
    #[arg(short, long, default_value_t = 1)]
    count: usize,
}

fn main() {
    let cli = Cli::parse();
    
    for _ in 0..cli.count {
        println!("{}", greet(&cli.name));
    }
}
""")
        
        (project_path / "src" / "lib.rs").write_text("""
//! A sample Rust library

use serde::{Deserialize, Serialize};

/// Represents a greeting
#[derive(Debug, Serialize, Deserialize, PartialEq)]
pub struct Greeting {
    pub message: String,
    pub recipient: String,
}

impl Greeting {
    /// Create a new greeting
    pub fn new(recipient: &str) -> Self {
        Self {
            message: format!("Hello, {}!", recipient),
            recipient: recipient.to_string(),
        }
    }
}

/// Generate a greeting message
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

/// Calculate factorial (for demonstration)
pub fn factorial(n: u64) -> u64 {
    match n {
        0 | 1 => 1,
        _ => n * factorial(n - 1),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_greet() {
        assert_eq!(greet("Rust"), "Hello, Rust!");
        assert_eq!(greet("World"), "Hello, World!");
    }

    #[test]
    fn test_greeting_struct() {
        let greeting = Greeting::new("Rust");
        assert_eq!(greeting.recipient, "Rust");
        assert_eq!(greeting.message, "Hello, Rust!");
    }

    #[test]
    fn test_factorial() {
        assert_eq!(factorial(0), 1);
        assert_eq!(factorial(1), 1);
        assert_eq!(factorial(5), 120);
        assert_eq!(factorial(10), 3628800);
    }
}
""")
        
        # Create integration tests
        (project_path / "tests" / "integration_test.rs").write_text("""
use rust_app::{greet, factorial, Greeting};

#[test]
fn test_greet_integration() {
    let result = greet("Integration");
    assert!(result.contains("Integration"));
}

#[test]
fn test_factorial_large_numbers() {
    assert_eq!(factorial(12), 479001600);
}

#[test]
fn test_greeting_serialization() {
    let greeting = Greeting::new("Test");
    let json = serde_json::to_string(&greeting).unwrap();
    let deserialized: Greeting = serde_json::from_str(&json).unwrap();
    assert_eq!(greeting, deserialized);
}
""")
        
        # Create benchmark
        (project_path / "benches" / "benchmarks.rs").write_text("""
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use rust_app::factorial;

fn criterion_benchmark(c: &mut Criterion) {
    c.bench_function("factorial 10", |b| {
        b.iter(|| factorial(black_box(10)))
    });
    
    c.bench_function("factorial 15", |b| {
        b.iter(|| factorial(black_box(15)))
    });
}

criterion_group!(benches, criterion_benchmark);
criterion_main!(benches);
""")
        
        # Create example
        (project_path / "examples" / "basic_usage.rs").write_text("""
//! Basic usage example

use rust_app::{greet, Greeting};

fn main() {
    println!("{}", greet("Example"));
    
    let greeting = Greeting::new("Example");
    println!("Greeting struct: {:?}", greeting);
}
""")
    
    @staticmethod  
    def create_monorepo_project(project_path: Path) -> None:
        """Create a complex monorepo with multiple languages and services"""
        # Create structure
        services = {
            "frontend": "javascript",
            "backend": "python", 
            "auth-service": "rust",
            "shared": "typescript"
        }
        
        for service_name, language in services.items():
            service_path = project_path / service_name
            service_path.mkdir(parents=True)
            (service_path / "src").mkdir(parents=True)
            (service_path / "tests").mkdir(parents=True)
            
            if language == "javascript":
                SampleProjectFactory._create_js_service(service_path, service_name)
            elif language == "python":
                SampleProjectFactory._create_python_service(service_path, service_name)
            elif language == "rust":
                SampleProjectFactory._create_rust_service(service_path, service_name)
            elif language == "typescript":
                SampleProjectFactory._create_ts_service(service_path, service_name)
                
        # Root configuration
        (project_path / "docs").mkdir()
        (project_path / "scripts").mkdir()
        (project_path / ".github" / "workflows").mkdir(parents=True)
        
        # Root package.json for workspace
        root_package = {
            "name": "monorepo",
            "version": "1.0.0",
            "private": True,
            "workspaces": list(services.keys()),
            "scripts": {
                "build": "npm run build --workspaces",
                "test": "npm run test --workspaces",
                "lint": "npm run lint --workspaces"
            },
            "devDependencies": {
                "lerna": "^7.0.0",
                "concurrently": "^8.0.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(root_package, f, indent=2)
            
        # Complex .mise.toml
        complex_mise_config = f"""
[tools]
node = "20"
python = "3.11" 
rust = "1.75"

[env]
NODE_ENV = "development"
PYTHONPATH = "backend/src"

# Installation tasks
[tasks.install]
description = "Install all dependencies"
run = [
    "npm install",
    "cd backend && pip install -e .[dev]",
    "cd auth-service && cargo fetch"
]

# Individual service build tasks
{SampleProjectFactory._generate_service_tasks(services, "build")}

# Individual service test tasks  
{SampleProjectFactory._generate_service_tasks(services, "test")}

# Individual service dev tasks
{SampleProjectFactory._generate_service_tasks(services, "dev")}

# Aggregate tasks
[tasks."build:all"]
description = "Build all services"
depends = [{", ".join([f'"build:{service}"' for service in services.keys()])}]

[tasks."test:all"]
description = "Test all services"
depends = [{", ".join([f'"test:{service}"' for service in services.keys()])}]

[tasks."dev:all"]
description = "Start all development servers"
run = "mise run --parallel {' '.join([f'dev:{service}' for service in services.keys()])}"

# Linting tasks
[tasks."lint:frontend"]
description = "Lint frontend code"
run = "cd frontend && npm run lint"
sources = ["frontend/src/**/*"]

[tasks."lint:shared"]
description = "Lint shared TypeScript code"
run = "cd shared && npm run lint"
sources = ["shared/src/**/*"]

[tasks."lint:backend"]
description = "Lint backend Python code"
run = "cd backend && ruff check src && mypy src"
sources = ["backend/src/**/*"]

[tasks."lint:auth-service"]
description = "Lint auth service Rust code"
run = "cd auth-service && cargo clippy -- -D warnings"
sources = ["auth-service/src/**/*"]

[tasks."lint:all"]
description = "Lint all code"
depends = ["lint:frontend", "lint:shared", "lint:backend", "lint:auth-service"]

# Integration tasks
[tasks."test:integration"]
description = "Run integration tests"
run = "python scripts/run_integration_tests.py"
sources = ["*/src/**/*", "tests/integration/**/*"]
depends = ["build:all"]

[tasks."test:e2e"]
description = "Run end-to-end tests"
run = "cd frontend && npm run test:e2e"
depends = ["dev:all"]

# Deployment tasks
[tasks."deploy:staging"]
description = "Deploy to staging environment"
run = "python scripts/deploy.py --env staging"
depends = ["build:all", "test:all", "lint:all"]

[tasks."deploy:production"]
description = "Deploy to production environment"
run = "python scripts/deploy.py --env production"
depends = ["build:all", "test:all", "lint:all", "test:integration"]

# CI/CD
[tasks.ci]
description = "Full CI pipeline"
depends = ["lint:all", "test:all", "build:all", "test:integration"]

# Utility tasks
[tasks.clean]
description = "Clean all build artifacts"
run = [
    "rm -rf */dist */build */target */node_modules",
    "find . -name '__pycache__' -exec rm -rf {{}} +",
    "find . -name '*.pyc' -delete"
]

[tasks.docs]
description = "Generate documentation"
run = [
    "cd frontend && npm run docs",
    "cd backend && sphinx-build -b html docs docs/_build/html",
    "cd auth-service && cargo doc --no-deps"
]
depends = ["build:all"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(complex_mise_config.strip())
            
        # Create deployment script
        (project_path / "scripts" / "deploy.py").write_text("""
#!/usr/bin/env python3
'''Deployment script for monorepo'''

import sys
import argparse

def deploy(environment: str) -> None:
    print(f"Deploying to {environment} environment...")
    # Deployment logic would go here

def main():
    parser = argparse.ArgumentParser(description='Deploy monorepo')
    parser.add_argument('--env', required=True, choices=['staging', 'production'])
    args = parser.parse_args()
    
    deploy(args.env)

if __name__ == '__main__':
    main()
""")
        
        # Create integration test script
        (project_path / "scripts" / "run_integration_tests.py").write_text("""
#!/usr/bin/env python3
'''Run integration tests across services'''

import subprocess
import sys

def run_integration_tests() -> bool:
    print("Running integration tests...")
    
    # This would contain actual integration test logic
    tests_passed = True
    
    if tests_passed:
        print("✅ All integration tests passed")
        return True
    else:
        print("❌ Some integration tests failed")
        return False

if __name__ == '__main__':
    success = run_integration_tests()
    sys.exit(0 if success else 1)
""")
        
    @staticmethod
    def _create_js_service(service_path: Path, service_name: str) -> None:
        """Create a JavaScript service"""
        package_json = {
            "name": service_name,
            "version": "1.0.0",
            "scripts": {
                "build": "webpack --mode=production",
                "test": "jest",
                "dev": "webpack serve --mode=development",
                "lint": "eslint src/"
            },
            "devDependencies": {
                "webpack": "^5.88.0",
                "jest": "^29.5.0",
                "eslint": "^8.44.0"
            }
        }
        
        with open(service_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
    
    @staticmethod
    def _create_python_service(service_path: Path, service_name: str) -> None:
        """Create a Python service"""
        pyproject_content = f"""
[project]
name = "{service_name}"
version = "0.1.0"
dependencies = ["fastapi", "uvicorn"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]
"""
        
        with open(service_path / "pyproject.toml", "w") as f:
            f.write(pyproject_content.strip())
    
    @staticmethod
    def _create_rust_service(service_path: Path, service_name: str) -> None:
        """Create a Rust service"""
        cargo_toml = f"""
[package]
name = "{service_name}"
version = "0.1.0"
edition = "2021"

[dependencies]
tokio = {{ version = "1.0", features = ["full"] }}
serde = {{ version = "1.0", features = ["derive"] }}
"""
        
        with open(service_path / "Cargo.toml", "w") as f:
            f.write(cargo_toml.strip())
    
    @staticmethod
    def _create_ts_service(service_path: Path, service_name: str) -> None:
        """Create a TypeScript service"""
        package_json = {
            "name": service_name,
            "version": "1.0.0",
            "scripts": {
                "build": "tsc",
                "test": "jest",
                "dev": "tsc --watch",
                "lint": "eslint src/ --ext .ts"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "jest": "^29.5.0",
                "@types/jest": "^29.5.0",
                "eslint": "^8.44.0",
                "@typescript-eslint/parser": "^6.0.0"
            }
        }
        
        with open(service_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
    
    @staticmethod
    def _generate_service_tasks(services: Dict[str, str], task_type: str) -> str:
        """Generate mise tasks for services"""
        tasks = []
        
        for service_name, language in services.items():
            if task_type == "build":
                if language in ["javascript", "typescript"]:
                    run_cmd = f"cd {service_name} && npm run build"
                    sources = [f"{service_name}/src/**/*", f"{service_name}/package.json"]
                    outputs = [f"{service_name}/dist/"]
                elif language == "python":
                    run_cmd = f"cd {service_name} && python -m build"
                    sources = [f"{service_name}/src/**/*.py", f"{service_name}/pyproject.toml"]
                    outputs = [f"{service_name}/dist/"]
                elif language == "rust":
                    run_cmd = f"cd {service_name} && cargo build --release"
                    sources = [f"{service_name}/src/**/*.rs", f"{service_name}/Cargo.toml"]
                    outputs = [f"{service_name}/target/release/"]
                    
            elif task_type == "test":
                if language in ["javascript", "typescript"]:
                    run_cmd = f"cd {service_name} && npm test"
                elif language == "python":
                    run_cmd = f"cd {service_name} && pytest"
                elif language == "rust":
                    run_cmd = f"cd {service_name} && cargo test"
                sources = [f"{service_name}/src/**/*", f"{service_name}/tests/**/*"]
                outputs = []
                
            elif task_type == "dev":
                if language in ["javascript", "typescript"]:
                    run_cmd = f"cd {service_name} && npm run dev"
                elif language == "python":
                    run_cmd = f"cd {service_name} && uvicorn main:app --reload"
                elif language == "rust":
                    run_cmd = f"cd {service_name} && cargo run"
                sources = []
                outputs = []
            
            task = f'''[tasks."{task_type}:{service_name}"]
description = "{task_type.title()} {service_name}"
run = "{run_cmd}"'''
            
            if task_type in ["build", "test"]:
                sources_str = '", "'.join(sources)
                task += f'''
sources = ["{sources_str}"]'''
                
                if outputs:
                    outputs_str = '", "'.join(outputs)
                    task += f'''
outputs = ["{outputs_str}"]'''
            
            tasks.append(task)
        
        return "\n\n".join(tasks)


# Convenience functions for test fixtures
def create_temp_project(project_type: str) -> Path:
    """Create a temporary project of the specified type"""
    temp_dir = tempfile.mkdtemp()
    project_path = Path(temp_dir)
    
    factory = SampleProjectFactory()
    
    if project_type == "javascript":
        factory.create_simple_javascript_project(project_path)
    elif project_type == "python":
        factory.create_python_project(project_path)
    elif project_type == "rust":
        factory.create_rust_project(project_path)
    elif project_type == "monorepo":
        factory.create_monorepo_project(project_path)
    else:
        raise ValueError(f"Unknown project type: {project_type}")
    
    return project_path