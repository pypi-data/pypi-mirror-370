"""
Unit tests for wise_mise_mcp.manager module
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from wise_mise_mcp.manager import TaskManager
from wise_mise_mcp.models import (
    TaskDefinition, 
    TaskDomain, 
    TaskComplexity, 
    MiseConfig
)


class TestTaskManager:
    """Test TaskManager class"""
    
    def test_manager_initialization(self, temp_project_dir):
        """Test TaskManager initialization"""
        manager = TaskManager(temp_project_dir)
        
        assert manager.project_path == temp_project_dir
        assert manager.mise_config_path == temp_project_dir / ".mise.toml"
        assert manager.mise_dir == temp_project_dir / ".mise"
        assert manager.tasks_dir == temp_project_dir / ".mise" / "tasks"
        
    def test_ensure_structure(self, temp_project_dir):
        """Test ensuring proper directory structure"""
        manager = TaskManager(temp_project_dir)
        manager.ensure_structure()
        
        # Verify directories were created
        assert manager.mise_dir.exists()
        assert manager.tasks_dir.exists()
        
        # Verify domain subdirectories
        for domain in TaskDomain:
            domain_dir = manager.tasks_dir / domain.value
            assert domain_dir.exists()
            
    def test_determine_complexity(self, temp_project_dir):
        """Test task complexity determination"""
        manager = TaskManager(temp_project_dir)
        
        # Test simple task
        simple_desc = "Build the project"
        assert manager._determine_complexity(simple_desc) == TaskComplexity.SIMPLE
        
        # Test moderate task  
        moderate_desc = "Build and test the project"
        assert manager._determine_complexity(moderate_desc) == TaskComplexity.MODERATE
        
        # Test complex task
        complex_desc = "Run multiple steps with conditional logic and validation"
        assert manager._determine_complexity(complex_desc) == TaskComplexity.COMPLEX
        
    def test_generate_task_name(self, temp_project_dir):
        """Test task name generation from description"""
        manager = TaskManager(temp_project_dir)
        
        # Test simple description
        name = manager._generate_task_name("Build frontend assets", TaskDomain.BUILD)
        assert len(name) > 0
        assert "build" in name.lower() or "frontend" in name.lower() or "assets" in name.lower()
        
        # Test with stop words
        name = manager._generate_task_name("Run the linting process", TaskDomain.LINT)
        assert "the" not in name  # Stop words should be removed
        
        # Test long description
        long_desc = "This is a very long description with many words that should be truncated"
        name = manager._generate_task_name(long_desc, TaskDomain.TEST)
        assert len(name) <= 20  # Should be limited in length
        
    def test_generate_run_command_build_domain(self, temp_project_dir):
        """Test run command generation for build domain"""
        manager = TaskManager(temp_project_dir)
        
        # Test npm build
        cmd = manager._generate_run_command(TaskDomain.BUILD, "Build with npm", "build")
        assert cmd == "npm run build"
        
        # Test cargo build
        cmd = manager._generate_run_command(TaskDomain.BUILD, "Build rust project", "build")
        assert cmd == "cargo build"
        
        # Test python build
        cmd = manager._generate_run_command(TaskDomain.BUILD, "Build python package", "build")
        assert cmd == "python -m build"
        
        # Test fallback
        cmd = manager._generate_run_command(TaskDomain.BUILD, "Build something", "build")
        assert "TODO" in cmd
        
    def test_generate_run_command_test_domain(self, temp_project_dir):
        """Test run command generation for test domain"""
        manager = TaskManager(temp_project_dir)
        
        # Test npm test
        cmd = manager._generate_run_command(TaskDomain.TEST, "Run jest tests", "test")
        assert cmd == "npm test"
        
        # Test cargo test
        cmd = manager._generate_run_command(TaskDomain.TEST, "Run cargo tests", "test")  
        assert cmd == "cargo test"
        
        # Test pytest
        cmd = manager._generate_run_command(TaskDomain.TEST, "Run pytest", "test")
        assert cmd == "pytest"
        
    def test_generate_run_command_lint_domain(self, temp_project_dir):
        """Test run command generation for lint domain"""
        manager = TaskManager(temp_project_dir)
        
        # Test eslint
        cmd = manager._generate_run_command(TaskDomain.LINT, "Run eslint", "lint")
        assert cmd == "npx eslint ."
        
        # Test clippy
        cmd = manager._generate_run_command(TaskDomain.LINT, "Run clippy", "lint")
        assert cmd == "cargo clippy"
        
        # Test ruff
        cmd = manager._generate_run_command(TaskDomain.LINT, "Run ruff", "lint")
        assert cmd == "ruff check ."
        
    def test_generate_sources_outputs(self, temp_project_dir):
        """Test sources and outputs generation"""
        manager = TaskManager(temp_project_dir)
        
        # Mock project structure with npm
        with patch.object(manager.analyzer, 'analyze_project_structure') as mock_analyze:
            mock_structure = Mock()
            mock_structure.package_managers = {"npm"}
            mock_structure.source_dirs = ["src", "lib"]
            mock_analyze.return_value = mock_structure
            
            # Test build domain
            sources, outputs = manager._generate_sources_outputs(TaskDomain.BUILD)
            
            assert "src/**/*" in sources
            assert "lib/**/*" in sources
            assert "package.json" in sources
            assert "dist/" in outputs or "build/" in outputs
            
    def test_create_task_definition(self, temp_project_dir):
        """Test task definition creation"""
        manager = TaskManager(temp_project_dir)
        
        with patch.object(manager, '_generate_run_command', return_value="npm test"):
            with patch.object(manager, '_generate_sources_outputs', return_value=(["src/**/*"], ["coverage/"])):
                task_def = manager._create_task_definition(
                    "test:unit", 
                    TaskDomain.TEST, 
                    "Run unit tests",
                    TaskComplexity.SIMPLE
                )
                
                assert task_def.name == "test:unit"
                assert task_def.domain == TaskDomain.TEST
                assert task_def.description == "Run unit tests"
                assert task_def.run == "npm test"
                assert task_def.sources == ["src/**/*"]
                assert task_def.outputs == ["coverage/"]
                assert task_def.complexity == TaskComplexity.SIMPLE
                
    def test_create_file_task(self, temp_project_dir):
        """Test file task creation"""
        manager = TaskManager(temp_project_dir)
        manager.ensure_structure()
        
        # Create a complex task definition
        task_def = TaskDefinition(
            name="deploy:production",
            domain=TaskDomain.DEPLOY,
            description="Deploy to production environment",
            run="./deploy.sh prod",
            sources=["dist/**/*"],
            depends=["build", "test"],
            complexity=TaskComplexity.COMPLEX
        )
        
        with patch.object(manager, '_generate_script_content', return_value="#!/bin/bash\necho test"):
            file_path = manager._create_file_task(task_def)
            
            assert file_path.exists()
            assert file_path.is_file()
            assert os.access(file_path, os.X_OK)  # Should be executable
            
    def test_generate_script_content(self, temp_project_dir):
        """Test script content generation"""
        manager = TaskManager(temp_project_dir)
        
        task_def = TaskDefinition(
            name="deploy:staging",
            domain=TaskDomain.DEPLOY,
            description="Deploy to staging environment",
            run="./deploy.sh staging",
            sources=["dist/**/*", "package.json"],
            outputs=["logs/deploy.log"],
            depends=["build"]
        )
        
        content = manager._generate_script_content(task_def)
        
        assert "#!/usr/bin/env bash" in content
        assert task_def.description in content
        assert "dist/**/*" in content and "package.json" in content  # Sources
        assert "logs/deploy.log" in content  # Outputs  
        assert "build" in content  # Dependencies
        assert "./deploy.sh staging" in content  # Run command
        assert "set -euo pipefail" in content  # Safety flags
        
    def test_add_toml_task_to_config(self, temp_project_dir):
        """Test adding TOML task to configuration"""
        manager = TaskManager(temp_project_dir)
        
        task_def = TaskDefinition(
            name="test:coverage",
            domain=TaskDomain.TEST,
            description="Run tests with coverage",
            run="npm test -- --coverage",
            sources=["src/**/*", "tests/**/*"],
            outputs=["coverage/"],
            depends=["build"],
            alias="tc"
        )
        
        result = manager._add_task_to_config(task_def)
        
        assert result["success"] is True
        assert result["type"] == "toml_task"
        assert "test:coverage" in result["task_name"]
        
        # Verify task was added to configuration
        config = MiseConfig.load_from_file(manager.mise_config_path)
        assert "test:coverage" in config.tasks
        task_config = config.tasks["test:coverage"]
        assert task_config["description"] == "Run tests with coverage"
        assert task_config["run"] == "npm test -- --coverage"
        assert task_config["depends"] == ["build"]
        assert task_config["alias"] == "tc"
        
    def test_add_file_task_to_config(self, temp_project_dir):
        """Test adding file task (no config changes needed)"""
        manager = TaskManager(temp_project_dir)
        manager.ensure_structure()
        
        task_def = TaskDefinition(
            name="deploy:prod",
            domain=TaskDomain.DEPLOY,
            description="Deploy to production",
            run="./deploy.sh",
            complexity=TaskComplexity.COMPLEX,
            file_path=Path("/test/path/deploy")
        )
        
        result = manager._add_task_to_config(task_def)
        
        assert result["success"] is True
        assert result["type"] == "file_task"
        assert "deploy:prod" in result["task_name"]
        
    def test_create_task_intelligently_simple(self, temp_project_dir):
        """Test intelligent task creation for simple task"""
        manager = TaskManager(temp_project_dir)
        
        with patch.object(manager.analyzer, 'find_expert_for_task') as mock_expert:
            mock_expert.return_value = Mock(domain=TaskDomain.TEST)
            
            with patch.object(manager.analyzer, 'extract_existing_tasks', return_value=[]):
                result = manager.create_task_intelligently(
                    task_description="Run unit tests",
                    suggested_name="unit"
                )
                
                assert result.get("success") is True
                assert "test:unit" in result.get("task_name", "")
                
    def test_create_task_intelligently_duplicate(self, temp_project_dir):
        """Test intelligent task creation with duplicate name"""
        manager = TaskManager(temp_project_dir)
        
        # Mock existing task
        existing_task = TaskDefinition(
            name="test:unit",
            domain=TaskDomain.TEST,
            description="Existing test",
            run="npm test"
        )
        
        with patch.object(manager.analyzer, 'find_expert_for_task') as mock_expert:
            mock_expert.return_value = Mock(domain=TaskDomain.TEST)
            
            with patch.object(manager.analyzer, 'extract_existing_tasks', return_value=[existing_task]):
                result = manager.create_task_intelligently(
                    task_description="Run unit tests",
                    suggested_name="unit"
                )
                
                assert "error" in result
                assert "already exists" in result["error"]
                
    def test_create_task_intelligently_no_expert(self, temp_project_dir):
        """Test intelligent task creation when no expert found"""
        manager = TaskManager(temp_project_dir)
        
        with patch.object(manager.analyzer, 'find_expert_for_task', return_value=None):
            result = manager.create_task_intelligently(
                task_description="Do something mysterious"
            )
            
            assert "error" in result
            assert "domain" in result["error"].lower()
            
    def test_create_task_intelligently_forced_complexity(self, temp_project_dir):
        """Test intelligent task creation with forced complexity"""
        manager = TaskManager(temp_project_dir)
        
        with patch.object(manager.analyzer, 'find_expert_for_task') as mock_expert:
            mock_expert.return_value = Mock(domain=TaskDomain.DEPLOY)
            
            with patch.object(manager.analyzer, 'extract_existing_tasks', return_value=[]):
                with patch.object(manager, '_add_task_to_config') as mock_add:
                    mock_add.return_value = {"success": True, "type": "file_task"}
                    
                    result = manager.create_task_intelligently(
                        task_description="Simple deployment",
                        force_complexity=TaskComplexity.COMPLEX
                    )
                    
                    assert result.get("success") is True
                    
    def test_remove_toml_task(self, temp_project_dir):
        """Test removing TOML task"""
        manager = TaskManager(temp_project_dir)
        
        # First add a task
        config = MiseConfig.load_from_file(manager.mise_config_path)
        config.tasks["temp_task"] = {"run": "echo temp"}
        config.save_to_file(manager.mise_config_path)
        
        # Now remove it
        result = manager.remove_task("temp_task")
        
        assert result["success"] is True
        assert "TOML task" in result["message"]
        
        # Verify it was removed
        updated_config = MiseConfig.load_from_file(manager.mise_config_path)
        assert "temp_task" not in updated_config.tasks
        
    def test_remove_file_task(self, temp_project_dir):
        """Test removing file task"""
        manager = TaskManager(temp_project_dir)
        manager.ensure_structure()
        
        # Create a file task
        test_file = manager.tasks_dir / "test" / "example"
        test_file.parent.mkdir(exist_ok=True)
        test_file.write_text("#!/bin/bash\necho test")
        
        result = manager.remove_task("test:example")
        
        assert result["success"] is True
        assert "file task" in result["message"]
        assert not test_file.exists()
        
    def test_remove_nonexistent_task(self, temp_project_dir):
        """Test removing non-existent task"""
        manager = TaskManager(temp_project_dir)
        
        result = manager.remove_task("nonexistent")
        
        assert "error" in result
        assert "not found" in result["error"]
        
    def test_find_task_file(self, temp_project_dir):
        """Test finding task files"""
        manager = TaskManager(temp_project_dir)
        manager.ensure_structure()
        
        # Create test files
        domain_file = manager.tasks_dir / "build" / "webpack"
        domain_file.write_text("#!/bin/bash\necho build")
        
        root_file = manager.tasks_dir / "global"
        root_file.write_text("#!/bin/bash\necho global")
        
        # Test finding domain-specific file
        found_file = manager._find_task_file("build:webpack")
        assert found_file == domain_file
        
        # Test finding root file
        found_file = manager._find_task_file("global")
        assert found_file == root_file
        
        # Test non-existent file
        found_file = manager._find_task_file("nonexistent")
        assert found_file is None
        
    def test_update_task_documentation(self, temp_project_dir):
        """Test task documentation update"""
        manager = TaskManager(temp_project_dir)
        
        with patch.object(manager.analyzer, 'extract_existing_tasks') as mock_extract:
            mock_tasks = [
                TaskDefinition(
                    name="build",
                    domain=TaskDomain.BUILD,
                    description="Build the project",
                    run="npm run build"
                ),
                TaskDefinition(
                    name="test:unit", 
                    domain=TaskDomain.TEST,
                    description="Run unit tests",
                    run="npm test",
                    alias="tu"
                )
            ]
            mock_extract.return_value = mock_tasks
            
            manager._update_task_documentation()
            
            # Verify documentation was created
            docs_dir = manager.mise_dir / "docs"
            assert docs_dir.exists()
            
            readme_path = docs_dir / "tasks.md"
            assert readme_path.exists()
            
            content = readme_path.read_text()
            assert "Build the project" in content
            assert "Run unit tests" in content
            assert "mise run build" in content
            assert "mise run test:unit" in content


class TestTaskManagerErrorHandling:
    """Test error handling and edge cases"""
    
    def test_create_task_with_invalid_complexity(self, temp_project_dir):
        """Test task creation with invalid complexity"""
        manager = TaskManager(temp_project_dir)
        
        result = manager.create_task_intelligently(
            task_description="Test task",
            force_complexity="invalid"
        )
        
        assert "error" in result
        assert "Invalid complexity" in result["error"]
        
    def test_file_task_creation_permission_error(self, temp_project_dir):
        """Test file task creation with permission error"""
        manager = TaskManager(temp_project_dir)
        
        task_def = TaskDefinition(
            name="test:perm",
            domain=TaskDomain.TEST,
            description="Permission test",
            run="echo test",
            complexity=TaskComplexity.COMPLEX
        )
        
        # Mock permission error during file creation
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            with pytest.raises(PermissionError):
                manager._create_file_task(task_def)
                
    def test_config_save_error_handling(self, temp_project_dir):
        """Test handling of config save errors"""
        manager = TaskManager(temp_project_dir)
        
        task_def = TaskDefinition(
            name="test:error",
            domain=TaskDomain.TEST,
            description="Error test",
            run="echo test"
        )
        
        # Mock save error
        with patch.object(MiseConfig, 'save_to_file', side_effect=Exception("Save failed")):
            result = manager._add_task_to_config(task_def)
            
            assert "error" in result
            assert "Save failed" in result["error"]
            
    def test_missing_mise_config_handling(self, temp_project_dir):
        """Test handling when .mise.toml doesn't exist"""
        # Remove the existing .mise.toml
        (temp_project_dir / ".mise.toml").unlink()
        
        manager = TaskManager(temp_project_dir)
        
        # Should create empty config and work normally
        result = manager.create_task_intelligently(
            task_description="Build project"
        )
        
        # Might fail due to no expert, but shouldn't crash
        assert isinstance(result, dict)