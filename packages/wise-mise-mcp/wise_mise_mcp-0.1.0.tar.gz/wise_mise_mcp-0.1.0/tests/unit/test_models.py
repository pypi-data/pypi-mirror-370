"""
Unit tests for wise_mise_mcp.models module
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

from wise_mise_mcp.models import (
    TaskDefinition,
    TaskDomain, 
    TaskComplexity,
    MiseConfig,
    ProjectStructure
)


class TestTaskDefinition:
    """Test TaskDefinition class"""
    
    def test_task_definition_creation(self):
        """Test basic task definition creation"""
        task = TaskDefinition(
            name="test:unit",
            domain=TaskDomain.TEST,
            description="Run unit tests",
            run="pytest tests/unit"
        )
        
        assert task.name == "test:unit"
        assert task.domain == TaskDomain.TEST
        assert task.description == "Run unit tests"
        assert task.run == "pytest tests/unit"
        assert task.complexity == TaskComplexity.SIMPLE
        assert not task.is_file_task
        
    def test_full_name_with_domain_prefix(self):
        """Test full_name property when name already has domain prefix"""
        task = TaskDefinition(
            name="test:unit",
            domain=TaskDomain.TEST,
            description="Run unit tests",
            run="pytest"
        )
        
        assert task.full_name == "test:unit"
        
    def test_full_name_without_domain_prefix(self):
        """Test full_name property when name needs domain prefix"""
        task = TaskDefinition(
            name="unit",
            domain=TaskDomain.TEST, 
            description="Run unit tests",
            run="pytest"
        )
        
        assert task.full_name == "test:unit"
        
    def test_is_file_task(self):
        """Test is_file_task property"""
        # Task without file path
        task1 = TaskDefinition(
            name="build",
            domain=TaskDomain.BUILD,
            description="Build project",
            run="npm run build"
        )
        assert not task1.is_file_task
        
        # Task with file path
        task2 = TaskDefinition(
            name="deploy",
            domain=TaskDomain.DEPLOY,
            description="Deploy to production", 
            run="./deploy.sh",
            file_path=Path("/project/.mise/tasks/deploy/production")
        )
        assert task2.is_file_task
        
    def test_task_with_dependencies(self):
        """Test task definition with various dependency types"""
        task = TaskDefinition(
            name="deploy:prod",
            domain=TaskDomain.DEPLOY,
            description="Deploy to production",
            run="./deploy.sh prod",
            depends=["build", "test"],
            depends_post=["notify:slack"],
            wait_for=["db:migrate"],
            sources=["src/**/*", "package.json"],
            outputs=["dist/"],
            env={"NODE_ENV": "production"},
            alias="dp"
        )
        
        assert task.depends == ["build", "test"]
        assert task.depends_post == ["notify:slack"] 
        assert task.wait_for == ["db:migrate"]
        assert task.sources == ["src/**/*", "package.json"]
        assert task.outputs == ["dist/"]
        assert task.env == {"NODE_ENV": "production"}
        assert task.alias == "dp"


class TestTaskDomain:
    """Test TaskDomain enum"""
    
    def test_all_domains_exist(self):
        """Test that all expected domains exist"""
        expected_domains = {
            "build", "test", "lint", "dev", "deploy", 
            "db", "ci", "docs", "clean", "setup"
        }
        
        actual_domains = {domain.value for domain in TaskDomain}
        assert actual_domains == expected_domains
        
    def test_domain_values(self):
        """Test specific domain values"""
        assert TaskDomain.BUILD.value == "build"
        assert TaskDomain.TEST.value == "test"
        assert TaskDomain.LINT.value == "lint"
        assert TaskDomain.DEV.value == "dev"
        assert TaskDomain.DEPLOY.value == "deploy"


class TestTaskComplexity:
    """Test TaskComplexity enum"""
    
    def test_complexity_values(self):
        """Test complexity enum values"""
        assert TaskComplexity.SIMPLE.value == "simple"
        assert TaskComplexity.MODERATE.value == "moderate" 
        assert TaskComplexity.COMPLEX.value == "complex"
        
    def test_complexity_ordering(self):
        """Test that complexity can be used for comparisons"""
        complexities = [TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX]
        assert len(complexities) == 3


class TestMiseConfig:
    """Test MiseConfig class"""
    
    def test_empty_config_creation(self):
        """Test creating empty mise config"""
        config = MiseConfig()
        
        assert config.tools == {}
        assert config.env == {}
        assert config.tasks == {}
        assert config.vars == {}
        assert config.task_config == {}
        
    def test_config_with_data(self):
        """Test creating config with data"""
        config = MiseConfig(
            tools={"node": "20", "python": "3.11"},
            env={"NODE_ENV": "development"},
            tasks={"build": {"run": "npm run build"}},
            vars={"PROJECT_NAME": "test-project"}
        )
        
        assert config.tools == {"node": "20", "python": "3.11"}
        assert config.env == {"NODE_ENV": "development"}
        assert config.tasks == {"build": {"run": "npm run build"}}
        assert config.vars == {"PROJECT_NAME": "test-project"}
        
    @patch("builtins.open", new_callable=mock_open, read_data="""
[tools]
node = "20"
python = "3.11"

[env]
NODE_ENV = "development"

[tasks.build]
description = "Build the project"
run = "npm run build"
sources = ["src/**/*"]
outputs = ["dist/"]

[vars]
PROJECT_NAME = "test-project"
""")
    def test_load_from_file(self, mock_file):
        """Test loading config from TOML file"""
        config = MiseConfig.load_from_file(Path("/test/.mise.toml"))
        
        assert config.tools == {"node": "20", "python": "3.11"}
        assert config.env == {"NODE_ENV": "development"}
        assert "build" in config.tasks
        assert config.tasks["build"]["description"] == "Build the project"
        assert config.vars == {"PROJECT_NAME": "test-project"}
        
    def test_load_from_nonexistent_file(self):
        """Test loading config from non-existent file returns empty config"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = MiseConfig.load_from_file(Path(temp_dir) / "nonexistent.toml")
            
            assert config.tools == {}
            assert config.env == {}
            assert config.tasks == {}
            assert config.vars == {}
            
    def test_save_to_file(self):
        """Test saving config to TOML file"""
        config = MiseConfig(
            tools={"node": "20"},
            env={"NODE_ENV": "test"},
            tasks={"test": {"run": "npm test"}}
        )
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.toml', delete=False) as f:
            config.save_to_file(Path(f.name))
            
            # Verify file was written
            assert Path(f.name).exists()
            
            # Load it back to verify content
            loaded_config = MiseConfig.load_from_file(Path(f.name))
            assert loaded_config.tools == {"node": "20"}
            assert loaded_config.env == {"NODE_ENV": "test"}
            assert loaded_config.tasks == {"test": {"run": "npm test"}}


class TestProjectStructure:
    """Test ProjectStructure class"""
    
    def test_empty_project_structure(self):
        """Test creating empty project structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            structure = ProjectStructure.analyze(project_path)
            
            assert structure.root_path == project_path
            assert len(structure.package_managers) == 0
            assert len(structure.languages) == 0
            assert len(structure.frameworks) == 0
            assert not structure.has_tests
            assert not structure.has_docs
            assert not structure.has_ci
            assert not structure.has_database
            
    def test_javascript_project_detection(self):
        """Test detection of JavaScript project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json
            package_json = {"name": "test", "version": "1.0.0"}
            with open(project_path / "package.json", "w") as f:
                import json
                json.dump(package_json, f)
                
            structure = ProjectStructure.analyze(project_path)
            
            assert "npm" in structure.package_managers
            assert "javascript" in structure.languages
            
    def test_python_project_detection(self):
        """Test detection of Python project"""  
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create pyproject.toml
            (project_path / "pyproject.toml").write_text("""
[build-system]
requires = ["hatchling"]

[project]
name = "test"
version = "1.0.0"
""")
            
            structure = ProjectStructure.analyze(project_path)
            
            assert "pip" in structure.package_managers
            assert "python" in structure.languages
            
    def test_rust_project_detection(self):
        """Test detection of Rust project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create Cargo.toml
            (project_path / "Cargo.toml").write_text("""
[package]
name = "test"
version = "0.1.0"
edition = "2021"
""")
            
            structure = ProjectStructure.analyze(project_path)
            
            assert "cargo" in structure.package_managers
            assert "rust" in structure.languages
            
    def test_go_project_detection(self):
        """Test detection of Go project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create go.mod
            (project_path / "go.mod").write_text("""
module test

go 1.21
""")
            
            structure = ProjectStructure.analyze(project_path)
            
            assert "go" in structure.package_managers  
            assert "go" in structure.languages
            
    def test_source_directory_detection(self):
        """Test detection of source directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create source directories
            (project_path / "src").mkdir()
            (project_path / "lib").mkdir()
            (project_path / "app").mkdir()
            
            structure = ProjectStructure.analyze(project_path)
            
            assert "src" in structure.source_dirs
            assert "lib" in structure.source_dirs
            assert "app" in structure.source_dirs
            
    def test_test_directory_detection(self):
        """Test detection of test directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create test directory
            (project_path / "tests").mkdir()
            
            structure = ProjectStructure.analyze(project_path)
            
            assert structure.has_tests
            
    def test_docs_directory_detection(self):
        """Test detection of docs directories"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create docs directory
            (project_path / "docs").mkdir()
            
            structure = ProjectStructure.analyze(project_path)
            
            assert structure.has_docs
            
    def test_ci_detection(self):
        """Test detection of CI configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create GitHub Actions workflow
            (project_path / ".github" / "workflows").mkdir(parents=True)
            
            structure = ProjectStructure.analyze(project_path)
            
            assert structure.has_ci
            
    def test_database_detection(self):
        """Test detection of database-related files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create migrations directory
            (project_path / "migrations").mkdir()
            
            structure = ProjectStructure.analyze(project_path)
            
            assert structure.has_database
            
    def test_complex_project_analysis(self):
        """Test analysis of complex multi-language project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create multi-language project
            import json
            
            # JavaScript frontend
            (project_path / "frontend").mkdir()
            package_json = {"name": "frontend", "version": "1.0.0"}
            with open(project_path / "frontend" / "package.json", "w") as f:
                json.dump(package_json, f)
                
            # Python backend
            (project_path / "backend").mkdir()
            (project_path / "backend" / "pyproject.toml").write_text("""
[project]
name = "backend"
version = "1.0.0"
""")
            
            # Common directories
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir() 
            (project_path / "docs").mkdir()
            (project_path / ".github" / "workflows").mkdir(parents=True)
            (project_path / "migrations").mkdir()
            
            structure = ProjectStructure.analyze(project_path)
            
            # Should detect both package managers
            assert "npm" in structure.package_managers
            assert "pip" in structure.package_managers
            
            # Should detect both languages  
            assert "javascript" in structure.languages
            assert "python" in structure.languages
            
            # Should detect all features
            assert structure.has_tests
            assert structure.has_docs
            assert structure.has_ci
            assert structure.has_database
            assert "src" in structure.source_dirs


class TestTaskRecommendation:
    """Test TaskRecommendation model"""
    
    def test_task_recommendation_creation(self):
        """Test creating task recommendation"""
        from wise_mise_mcp.models import TaskRecommendation
        
        task = TaskDefinition(
            name="test:e2e",
            domain=TaskDomain.TEST,
            description="Run end-to-end tests",
            run="playwright test"
        )
        
        recommendation = TaskRecommendation(
            task=task,
            reasoning="E2E testing framework detected in dependencies",
            priority=8,
            estimated_effort="medium",
            dependencies_needed=["build", "dev:serve"]
        )
        
        assert recommendation.task == task
        assert recommendation.reasoning == "E2E testing framework detected in dependencies"
        assert recommendation.priority == 8
        assert recommendation.estimated_effort == "medium"
        assert recommendation.dependencies_needed == ["build", "dev:serve"]