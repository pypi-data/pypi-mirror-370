"""
Unit tests for wise_mise_mcp.analyzer module
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from wise_mise_mcp.analyzer import TaskAnalyzer
from wise_mise_mcp.models import (
    TaskDefinition, 
    TaskDomain, 
    TaskComplexity, 
    MiseConfig, 
    ProjectStructure
)


class TestTaskAnalyzer:
    """Test TaskAnalyzer class"""
    
    def test_analyzer_initialization(self, temp_project_dir):
        """Test TaskAnalyzer initialization"""
        analyzer = TaskAnalyzer(temp_project_dir)
        
        assert analyzer.project_path == temp_project_dir
        assert isinstance(analyzer.mise_config, MiseConfig)
        assert len(analyzer.experts) == 10  # Should have all domain experts
        
    def test_analyze_project_structure(self, temp_project_dir):
        """Test project structure analysis"""
        analyzer = TaskAnalyzer(temp_project_dir)
        structure = analyzer.analyze_project_structure()
        
        assert isinstance(structure, ProjectStructure)
        assert structure.root_path == temp_project_dir
        assert "npm" in structure.package_managers
        assert "javascript" in structure.languages
        
    def test_extract_existing_tasks(self, temp_project_dir):
        """Test extraction of existing tasks from configuration"""
        analyzer = TaskAnalyzer(temp_project_dir)
        tasks = analyzer.extract_existing_tasks()
        
        assert len(tasks) == 3  # build, test, lint from fixture
        
        # Verify build task
        build_task = next((t for t in tasks if t.name == "build"), None)
        assert build_task is not None
        assert build_task.description == "Build the project"
        assert build_task.run == "npm run build"
        assert "src/**/*" in build_task.sources
        assert "dist/" in build_task.outputs
        
    def test_extract_domain_from_name(self, temp_project_dir):
        """Test domain extraction from task names"""
        analyzer = TaskAnalyzer(temp_project_dir)
        
        # Test explicit domain prefix
        assert analyzer._extract_domain_from_name("test:unit") == TaskDomain.TEST
        assert analyzer._extract_domain_from_name("build:frontend") == TaskDomain.BUILD
        assert analyzer._extract_domain_from_name("lint:eslint") == TaskDomain.LINT
        
        # Test keyword matching
        assert analyzer._extract_domain_from_name("test-coverage") == TaskDomain.TEST
        assert analyzer._extract_domain_from_name("build-assets") == TaskDomain.BUILD
        
        # Test fallback to BUILD
        assert analyzer._extract_domain_from_name("unknown-task") == TaskDomain.BUILD
        
    def test_build_dependency_graph(self, temp_project_dir):
        """Test building dependency graph from tasks"""
        analyzer = TaskAnalyzer(temp_project_dir)
        tasks = analyzer.extract_existing_tasks()
        graph = analyzer.build_dependency_graph(tasks)
        
        # Verify graph structure
        assert len(graph.nodes()) == 3
        assert "build" in graph.nodes()
        assert "test" in graph.nodes()
        assert "lint" in graph.nodes()
        
        # Verify dependency edge (test depends on build)
        assert graph.has_edge("build", "test")
        
    def test_trace_task_chain(self, temp_project_dir):
        """Test tracing task execution chain"""
        analyzer = TaskAnalyzer(temp_project_dir)
        trace_result = analyzer.trace_task_chain("test")
        
        assert trace_result["task_name"] == "test"
        assert "build" in trace_result["dependencies"]
        assert "build" in trace_result["execution_order"]
        assert "test" in trace_result["execution_order"]
        
        # build should execute before test
        execution_order = trace_result["execution_order"]
        build_index = execution_order.index("build")
        test_index = execution_order.index("test")
        assert build_index < test_index
        
    def test_trace_nonexistent_task(self, temp_project_dir):
        """Test tracing chain for non-existent task"""
        analyzer = TaskAnalyzer(temp_project_dir)
        result = analyzer.trace_task_chain("nonexistent")
        
        assert "error" in result
        assert "not found" in result["error"].lower()
        
    def test_find_parallel_groups(self, temp_project_dir):
        """Test finding parallel execution groups"""
        analyzer = TaskAnalyzer(temp_project_dir)
        tasks = analyzer.extract_existing_tasks()
        graph = analyzer.build_dependency_graph(tasks)
        
        parallel_groups = analyzer._find_parallel_groups(graph)
        
        # Should have at least 2 levels
        assert len(parallel_groups) >= 2
        
        # First level should include tasks with no dependencies
        first_level = parallel_groups[0]
        assert "build" in first_level or "lint" in first_level
        
    def test_get_task_recommendations(self, temp_project_dir):
        """Test getting task recommendations"""
        analyzer = TaskAnalyzer(temp_project_dir)
        recommendations = analyzer.get_task_recommendations()
        
        assert len(recommendations) > 0
        
        # Verify recommendation structure
        for rec in recommendations[:3]:  # Check first 3
            assert hasattr(rec, 'task')
            assert hasattr(rec, 'reasoning')
            assert hasattr(rec, 'priority')
            assert hasattr(rec, 'estimated_effort')
            assert isinstance(rec.priority, int)
            assert 1 <= rec.priority <= 10
            
    def test_find_expert_for_task(self, temp_project_dir):
        """Test finding appropriate expert for task description"""
        analyzer = TaskAnalyzer(temp_project_dir)
        
        # Test build task
        build_expert = analyzer.find_expert_for_task("Build the frontend assets")
        assert build_expert is not None
        assert build_expert.domain == TaskDomain.BUILD
        
        # Test test task
        test_expert = analyzer.find_expert_for_task("Run unit tests with coverage")
        assert test_expert is not None
        assert test_expert.domain == TaskDomain.TEST
        
        # Test lint task
        lint_expert = analyzer.find_expert_for_task("Run ESLint on source code")
        assert lint_expert is not None
        assert lint_expert.domain == TaskDomain.LINT
        
        # Test unknown task
        unknown_expert = analyzer.find_expert_for_task("Do something mysterious")
        # Should return None or a default expert
        
    def test_validate_task_architecture(self, temp_project_dir):
        """Test task architecture validation"""
        analyzer = TaskAnalyzer(temp_project_dir)
        validation = analyzer.validate_task_architecture()
        
        assert "total_tasks" in validation
        assert "domains_used" in validation
        assert "domain_distribution" in validation
        assert "has_cycles" in validation
        assert "issues" in validation
        assert "suggestions" in validation
        
        assert validation["total_tasks"] == 3
        assert not validation["has_cycles"]  # No circular dependencies
        assert isinstance(validation["issues"], list)
        assert isinstance(validation["suggestions"], list)
        
    def test_find_redundant_tasks(self, temp_project_dir):
        """Test finding redundant tasks"""
        analyzer = TaskAnalyzer(temp_project_dir)
        redundant = analyzer.find_redundant_tasks()
        
        assert isinstance(redundant, list)
        # With our simple fixture, there shouldn't be redundant tasks
        
    def test_calculate_task_similarity(self, temp_project_dir):
        """Test task similarity calculation"""
        analyzer = TaskAnalyzer(temp_project_dir)
        
        # Create similar tasks
        task1 = TaskDefinition(
            name="test:unit",
            domain=TaskDomain.TEST,
            description="Run unit tests",
            run="npm test",
            sources=["src/**/*", "tests/**/*"],
            outputs=[]
        )
        
        task2 = TaskDefinition(
            name="test:integration", 
            domain=TaskDomain.TEST,
            description="Run integration tests",
            run="npm test",  # Same run command
            sources=["src/**/*", "tests/**/*"],  # Same sources
            outputs=[]
        )
        
        similarity = analyzer._calculate_task_similarity(task1, task2)
        
        # Should be quite similar (same run command and sources)
        assert similarity > 0.5
        
    def test_complex_project_analysis(self, complex_project_structure):
        """Test analysis of complex multi-language project"""
        analyzer = TaskAnalyzer(complex_project_structure)
        
        # Test structure analysis
        structure = analyzer.analyze_project_structure()
        assert "npm" in structure.package_managers
        assert "pip" in structure.package_managers
        assert "javascript" in structure.languages
        assert "python" in structure.languages
        
        # Test task extraction
        tasks = analyzer.extract_existing_tasks()
        assert len(tasks) > 10  # Complex project should have many tasks
        
        # Verify hierarchical task naming
        task_names = [task.name for task in tasks]
        assert any("build:frontend" in name for name in task_names)
        assert any("build:backend" in name for name in task_names)
        assert any("test:frontend" in name for name in task_names)
        assert any("test:backend" in name for name in task_names)
        
        # Test dependency graph complexity
        graph = analyzer.build_dependency_graph(tasks)
        assert len(graph.nodes()) == len(tasks)
        assert len(graph.edges()) > 0  # Should have dependencies
        
        # Test parallel execution groups
        ci_task_trace = analyzer.trace_task_chain("ci")
        assert len(ci_task_trace["parallelizable_groups"]) > 1
        
    def test_circular_dependency_detection(self, temp_project_dir):
        """Test detection of circular dependencies"""
        # Create a configuration with circular dependencies
        circular_config = MiseConfig(
            tasks={
                "task_a": {
                    "run": "echo A",
                    "depends": ["task_b"]
                },
                "task_b": {
                    "run": "echo B", 
                    "depends": ["task_c"]
                },
                "task_c": {
                    "run": "echo C",
                    "depends": ["task_a"]  # Creates circle
                }
            }
        )
        
        with patch.object(MiseConfig, 'load_from_file', return_value=circular_config):
            analyzer = TaskAnalyzer(temp_project_dir)
            validation = analyzer.validate_task_architecture()
            
            assert validation["has_cycles"]
            assert any("Circular" in issue for issue in validation["issues"])
            
    def test_orphaned_task_detection(self, temp_project_dir):
        """Test detection of orphaned tasks"""
        # Create configuration with orphaned task
        orphaned_config = MiseConfig(
            tasks={
                "build": {
                    "run": "npm run build"
                },
                "test": {
                    "run": "npm test",
                    "depends": ["build"]
                },
                "orphan": {
                    "run": "echo orphan"
                    # No dependencies and nothing depends on it
                }
            }
        )
        
        with patch.object(MiseConfig, 'load_from_file', return_value=orphaned_config):
            analyzer = TaskAnalyzer(temp_project_dir)
            validation = analyzer.validate_task_architecture()
            
            assert "orphan" in validation["orphaned_tasks"]
            
    def test_missing_description_detection(self, temp_project_dir):
        """Test detection of tasks without descriptions"""
        # Create configuration with task missing description
        no_desc_config = MiseConfig(
            tasks={
                "build": {
                    "run": "npm run build"
                    # Missing description
                },
                "test": {
                    "description": "Run tests",
                    "run": "npm test"
                }
            }
        )
        
        with patch.object(MiseConfig, 'load_from_file', return_value=no_desc_config):
            analyzer = TaskAnalyzer(temp_project_dir)
            validation = analyzer.validate_task_architecture()
            
            assert any("missing descriptions" in issue.lower() for issue in validation["issues"])


class TestTaskAnalyzerEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_mise_config(self, temp_project_dir):
        """Test analyzer with empty mise configuration"""
        empty_config = MiseConfig()
        
        with patch.object(MiseConfig, 'load_from_file', return_value=empty_config):
            analyzer = TaskAnalyzer(temp_project_dir)
            tasks = analyzer.extract_existing_tasks()
            
            assert len(tasks) == 0
            
    def test_malformed_task_configuration(self, temp_project_dir):
        """Test handling of malformed task configurations"""
        malformed_config = MiseConfig(
            tasks={
                "valid_task": {
                    "description": "Valid task",
                    "run": "echo valid"
                },
                "string_task": "echo string",  # Just a string
                "list_task": ["echo", "list"],  # Just a list
                "empty_task": {}  # Empty dict
            }
        )
        
        with patch.object(MiseConfig, 'load_from_file', return_value=malformed_config):
            analyzer = TaskAnalyzer(temp_project_dir)
            tasks = analyzer.extract_existing_tasks()
            
            assert len(tasks) == 4
            
            # Check that all tasks were created successfully
            task_names = [task.name for task in tasks]
            assert "valid_task" in task_names
            assert "string_task" in task_names
            assert "list_task" in task_names
            assert "empty_task" in task_names
            
    def test_nonexistent_project_path(self):
        """Test analyzer with non-existent project path"""
        nonexistent_path = Path("/nonexistent/project/path")
        
        # Should not raise exception during initialization
        analyzer = TaskAnalyzer(nonexistent_path)
        assert analyzer.project_path == nonexistent_path
        
    def test_permission_denied_project_path(self):
        """Test analyzer with permission-denied project path"""
        # This test may not work in all environments
        # Just ensure it doesn't crash
        try:
            analyzer = TaskAnalyzer(Path("/root"))  # Usually permission denied
            structure = analyzer.analyze_project_structure()
            # Should return empty or limited structure
        except (PermissionError, FileNotFoundError):
            # Expected in some environments
            pass