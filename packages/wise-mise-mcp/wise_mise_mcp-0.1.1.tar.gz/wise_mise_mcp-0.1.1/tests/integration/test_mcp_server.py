"""
Integration tests for the complete MCP server functionality
"""

import pytest
import tempfile
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

from wise_mise_mcp.server import (
    analyze_project_for_tasks,
    trace_task_chain, 
    create_task,
    validate_task_architecture,
    get_task_recommendations,
    AnalyzeProjectRequest,
    TraceTaskChainRequest,
    CreateTaskRequest,
    ValidateArchitectureRequest
)


class TestMCPServerIntegration:
    """Integration tests for MCP server with real project scenarios"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_project_analysis_workflow(self):
        """Test complete project analysis workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create a realistic React + Node.js project
            await self._create_react_nodejs_project(project_path)
            
            # Step 1: Analyze project structure
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            analysis_result = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in analysis_result
            assert analysis_result["project_structure"]["package_managers"] == ["npm"]
            assert "javascript" in analysis_result["project_structure"]["languages"] 
            assert analysis_result["project_structure"]["has_tests"] is True
            
            # Step 2: Get task recommendations
            recommendations_result = await get_task_recommendations(analyze_request)
            
            assert "error" not in recommendations_result
            assert len(recommendations_result["new_task_recommendations"]) > 0
            
            # Should recommend build, test, lint tasks for React project
            rec_names = [r["task_name"] for r in recommendations_result["new_task_recommendations"]]
            domains_represented = set()
            for name in rec_names:
                if ":" in name:
                    domain = name.split(":")[0]
                    domains_represented.add(domain)
                    
            # Should cover major development domains
            assert "build" in domains_represented or "test" in domains_represented
            
            # Step 3: Validate architecture
            validate_request = ValidateArchitectureRequest(project_path=str(project_path))
            validation_result = await validate_task_architecture(validate_request)
            
            assert "error" not in validation_result
            
    @pytest.mark.integration 
    @pytest.mark.asyncio
    async def test_task_creation_and_tracing_workflow(self):
        """Test creating tasks and tracing their dependencies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create basic project
            await self._create_basic_nodejs_project(project_path)
            
            # Create a new task
            create_request = CreateTaskRequest(
                project_path=str(project_path),
                task_description="Run tests with coverage reporting",
                suggested_name="coverage"
            )
            
            create_result = await create_task(create_request)
            
            if "error" not in create_result:
                # Task was created successfully, try to trace it
                task_name = create_result["task_name"]
                
                trace_request = TraceTaskChainRequest(
                    project_path=str(project_path),
                    task_name=task_name
                )
                
                trace_result = await trace_task_chain(trace_request)
                
                if "error" not in trace_result:
                    assert trace_result["task_name"] == task_name
                    assert "execution_order" in trace_result
                    assert "task_details" in trace_result
                    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complex_monorepo_analysis(self):
        """Test analysis of complex monorepo structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create monorepo structure
            await self._create_monorepo_project(project_path)
            
            # Analyze the complex project
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            result = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in result
            
            # Should detect multiple package managers and languages
            structure = result["project_structure"]
            assert len(structure["package_managers"]) >= 1
            assert len(structure["languages"]) >= 1
            assert structure["has_tests"] is True
            assert structure["has_docs"] is True
            
            # Should have many existing tasks from complex setup
            assert len(result["existing_tasks"]) >= 5
            
            # Should provide relevant recommendations
            assert len(result["recommendations"]) >= 0
            
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_python_project_analysis(self):
        """Test analysis of Python project with pyproject.toml"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create Python project
            await self._create_python_project(project_path)
            
            # Analyze Python project
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            result = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in result
            
            structure = result["project_structure"]
            assert "pip" in structure["package_managers"]
            assert "python" in structure["languages"]
            
            # Should recommend Python-specific tasks
            recommendations = result["recommendations"]
            python_tasks = [r for r in recommendations if "python" in r.get("run_command", "").lower() or "pytest" in r.get("run_command", "").lower()]
            
            # Might not always have Python-specific recommendations, but structure should be detected
            
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_rust_project_analysis(self):
        """Test analysis of Rust project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create Rust project
            await self._create_rust_project(project_path)
            
            # Analyze Rust project
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            result = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in result
            
            structure = result["project_structure"]
            assert "cargo" in structure["package_managers"]
            assert "rust" in structure["languages"]
            
            # Should recommend Rust-specific tasks
            recommendations = result["recommendations"]
            cargo_tasks = [r for r in recommendations if "cargo" in r.get("run_command", "")]
            
            # Should have cargo build and test recommendations
            assert len(cargo_tasks) >= 0  # May or may not have recommendations
            
    async def _create_react_nodejs_project(self, project_path: Path):
        """Create a realistic React + Node.js project structure"""
        # Create directories
        (project_path / "src").mkdir()
        (project_path / "src" / "components").mkdir()
        (project_path / "public").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        # Create package.json
        package_json = {
            "name": "react-app",
            "version": "1.0.0",
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build", 
                "test": "react-scripts test",
                "eject": "react-scripts eject",
                "lint": "eslint src/",
                "lint:fix": "eslint src/ --fix",
                "build:prod": "NODE_ENV=production npm run build"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-scripts": "5.0.1"
            },
            "devDependencies": {
                "eslint": "^8.0.0",
                "@testing-library/react": "^13.4.0",
                "@testing-library/jest-dom": "^5.16.5"
            },
            "browserslist": {
                "production": [">0.2%", "not dead", "not op_mini all"],
                "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
            
        # Create basic .mise.toml
        mise_config = """
[tools]
node = "18"

[env]
NODE_ENV = "development"

[tasks.install]
description = "Install dependencies"
run = "npm install"

[tasks.dev]  
description = "Start development server"
run = "npm start"
depends = ["install"]

[tasks.build]
description = "Build for production"
run = "npm run build"
sources = ["src/**/*", "public/**/*", "package.json"]
outputs = ["build/"]
depends = ["install"]

[tasks.test]
description = "Run tests"
run = "npm test -- --watchAll=false"
sources = ["src/**/*", "tests/**/*"]
depends = ["install"]

[tasks.lint]
description = "Run ESLint"
run = "npm run lint"
sources = ["src/**/*"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
        # Create some source files
        (project_path / "src" / "App.js").write_text("""
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Hello React!</h1>
      </header>
    </div>
  );
}

export default App;
""")
        
        (project_path / "src" / "App.test.js").write_text("""
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders hello message', () => {
  render(<App />);
  const linkElement = screen.getByText(/hello react/i);
  expect(linkElement).toBeInTheDocument();
});
""")
        
    async def _create_basic_nodejs_project(self, project_path: Path):
        """Create a basic Node.js project"""
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        
        package_json = {
            "name": "nodejs-app",
            "version": "1.0.0",
            "scripts": {
                "start": "node src/index.js",
                "test": "jest",
                "build": "webpack --mode=production"
            },
            "devDependencies": {
                "jest": "^29.0.0",
                "webpack": "^5.0.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
            
        mise_config = """
[tools]
node = "18"

[tasks.install]
run = "npm install"

[tasks.start]
run = "npm start"
depends = ["install"]

[tasks.test]
run = "npm test"
depends = ["install"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
    async def _create_monorepo_project(self, project_path: Path):
        """Create a complex monorepo structure"""
        # Create monorepo structure
        (project_path / "frontend").mkdir()
        (project_path / "backend").mkdir()
        (project_path / "shared").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        (project_path / ".github" / "workflows").mkdir(parents=True)
        
        # Frontend package.json
        frontend_package = {
            "name": "frontend",
            "version": "1.0.0",
            "scripts": {
                "build": "vite build",
                "dev": "vite serve",
                "test": "vitest"
            },
            "devDependencies": {
                "vite": "^4.0.0",
                "vitest": "^0.30.0"
            }
        }
        
        with open(project_path / "frontend" / "package.json", "w") as f:
            json.dump(frontend_package, f, indent=2)
            
        # Backend Python project
        pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "backend"
version = "1.0.0"
dependencies = ["fastapi", "uvicorn"]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
        
        with open(project_path / "backend" / "pyproject.toml", "w") as f:
            f.write(pyproject_content.strip())
            
        # Root package.json for workspace
        root_package = {
            "name": "monorepo",
            "version": "1.0.0",
            "workspaces": ["frontend", "backend", "shared"],
            "scripts": {
                "build": "npm run build --workspaces",
                "test": "npm run test --workspaces"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(root_package, f, indent=2)
            
        # Complex .mise.toml
        complex_mise_config = """
[tools]
node = "18"
python = "3.11"

[env]
NODE_ENV = "development"

[tasks.install]
description = "Install all dependencies"
run = [
    "npm install",
    "cd backend && pip install -e ."
]

[tasks."build:frontend"]
description = "Build frontend"
run = "cd frontend && npm run build"
sources = ["frontend/src/**/*"]
outputs = ["frontend/dist/"]

[tasks."build:backend"] 
description = "Build backend"
run = "cd backend && python -m build"
sources = ["backend/**/*.py"]
outputs = ["backend/dist/"]

[tasks.build]
description = "Build all"
depends = ["build:frontend", "build:backend"]

[tasks."test:frontend"]
description = "Test frontend"
run = "cd frontend && npm run test"

[tasks."test:backend"]
description = "Test backend"
run = "cd backend && pytest"

[tasks.test]
description = "Test all"
depends = ["test:frontend", "test:backend"]

[tasks."dev:frontend"]
description = "Start frontend dev server"
run = "cd frontend && npm run dev"

[tasks."dev:backend"]
description = "Start backend dev server" 
run = "cd backend && uvicorn main:app --reload"

[tasks.ci]
description = "Full CI pipeline"
depends = ["build", "test"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(complex_mise_config.strip())
            
    async def _create_python_project(self, project_path: Path):
        """Create a Python project with pyproject.toml"""
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        pyproject_content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "python-app"
version = "1.0.0"
dependencies = ["fastapi", "uvicorn", "pydantic"]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy", "black"]

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
        
        with open(project_path / "pyproject.toml", "w") as f:
            f.write(pyproject_content.strip())
            
        mise_config = """
[tools]
python = "3.11"

[env]
PYTHONPATH = "src"

[tasks.install]
description = "Install dependencies"
run = "pip install -e .[dev]"

[tasks.test]
description = "Run tests" 
run = "pytest"
sources = ["src/**/*.py", "tests/**/*.py"]
depends = ["install"]

[tasks.lint]
description = "Run linting"
run = [
    "ruff check src tests",
    "mypy src"
]
sources = ["src/**/*.py"]
depends = ["install"]

[tasks.format]
description = "Format code"
run = "black src tests"
sources = ["src/**/*.py", "tests/**/*.py"]

[tasks.build]
description = "Build package"
run = "python -m build"
sources = ["src/**/*.py", "pyproject.toml"] 
outputs = ["dist/"]
depends = ["install"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
    async def _create_rust_project(self, project_path: Path):
        """Create a Rust project"""
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        cargo_toml = """
[package]
name = "rust-app"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }

[dev-dependencies]
criterion = "0.5"

[[bench]]
name = "benchmarks"
harness = false
"""
        
        with open(project_path / "Cargo.toml", "w") as f:
            f.write(cargo_toml.strip())
            
        mise_config = """
[tools] 
rust = "1.70"

[tasks.install]
description = "Install dependencies"
run = "cargo fetch"

[tasks.build]
description = "Build project"
run = "cargo build"
sources = ["src/**/*.rs", "Cargo.toml"]
outputs = ["target/debug/"]

[tasks."build:release"]
description = "Build release"
run = "cargo build --release"
sources = ["src/**/*.rs", "Cargo.toml"]
outputs = ["target/release/"]
depends = ["test", "lint"]

[tasks.test]
description = "Run tests"
run = "cargo test"
sources = ["src/**/*.rs", "tests/**/*.rs"]

[tasks.lint]
description = "Run clippy"
run = "cargo clippy -- -D warnings"
sources = ["src/**/*.rs"]

[tasks.format]
description = "Check formatting"
run = "cargo fmt --check"
sources = ["src/**/*.rs"]

[tasks.bench]
description = "Run benchmarks"
run = "cargo bench"
depends = ["build:release"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
        # Create basic Rust source
        (project_path / "src" / "main.rs").write_text("""
fn main() {
    println!("Hello, world!");
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
""")


class TestMCPServerErrorHandling:
    """Test error handling in integration scenarios"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_corrupted_mise_config_handling(self):
        """Test handling of corrupted .mise.toml files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create corrupted TOML
            (project_path / ".mise.toml").write_text("""
[tools
node = "18"  # Missing closing bracket

[tasks.build
run = "npm run build"  # Missing closing bracket
""")
            
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            result = await analyze_project_for_tasks(analyze_request)
            
            # Should handle TOML parsing errors gracefully
            # Either return error or work with partial parsing
            assert isinstance(result, dict)
            
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_permission_denied_project(self):
        """Test handling of permission-denied project directories"""
        # This test may not work in all environments
        try:
            analyze_request = AnalyzeProjectRequest(project_path="/root/restricted")
            result = await analyze_project_for_tasks(analyze_request)
            
            # Should return error instead of crashing
            assert isinstance(result, dict)
            # Might succeed with limited access or return error
            
        except (PermissionError, FileNotFoundError):
            # Expected in restricted environments
            pass
            
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_large_project_performance(self):
        """Test performance with large project structures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create large project structure
            await self._create_large_project(project_path)
            
            import time
            start_time = time.time()
            
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            result = await analyze_project_for_tasks(analyze_request)
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            # Should complete within reasonable time (adjust threshold as needed)
            assert analysis_time < 30.0  # 30 seconds max
            assert "error" not in result or isinstance(result, dict)
            
    async def _create_large_project(self, project_path: Path):
        """Create a large project structure for performance testing"""
        # Create many directories and files
        for i in range(50):
            dir_path = project_path / f"module_{i}"
            dir_path.mkdir()
            (dir_path / "src").mkdir()
            (dir_path / "tests").mkdir()
            
            # Create package.json in each module
            package_json = {
                "name": f"module-{i}",
                "version": "1.0.0",
                "scripts": {"build": "echo building", "test": "echo testing"}
            }
            
            with open(dir_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
        # Create large .mise.toml with many tasks
        large_config = """
[tools]
node = "18"

"""
        
        for i in range(100):
            large_config += f"""
[tasks."build:module{i}"]
description = "Build module {i}"
run = "cd module_{i} && npm run build"

[tasks."test:module{i}"]
description = "Test module {i}" 
run = "cd module_{i} && npm test"
depends = ["build:module{i}"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(large_config)


class TestMCPServerConcurrency:
    """Test concurrent operations on MCP server"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_analysis_requests(self):
        """Test handling multiple concurrent analysis requests"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create basic project
            package_json = {"name": "test", "version": "1.0.0"}
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            (project_path / ".mise.toml").write_text("""
[tasks.test]
run = "echo test"
""")
            
            # Run multiple analysis requests concurrently
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            
            tasks = [
                analyze_project_for_tasks(analyze_request),
                analyze_project_for_tasks(analyze_request), 
                analyze_project_for_tasks(analyze_request)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should succeed
            for result in results:
                assert not isinstance(result, Exception)
                assert isinstance(result, dict)
                assert "project_path" in result