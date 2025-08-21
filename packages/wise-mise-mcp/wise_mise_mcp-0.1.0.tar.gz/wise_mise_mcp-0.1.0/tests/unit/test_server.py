"""
Unit tests for wise_mise_mcp.server module
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

from wise_mise_mcp.server import (
    AnalyzeProjectRequest,
    TraceTaskChainRequest, 
    CreateTaskRequest,
    ValidateArchitectureRequest,
    PruneTasksRequest,
    RemoveTaskRequest,
    analyze_project_for_tasks,
    trace_task_chain,
    create_task,
    validate_task_architecture,
    prune_tasks,
    remove_task,
    get_task_recommendations,
    get_mise_architecture_rules,
    mise_task_expert_guidance,
    task_chain_analyst
)
from wise_mise_mcp.models import TaskComplexity


class TestRequestModels:
    """Test request/response models"""
    
    def test_analyze_project_request(self):
        """Test AnalyzeProjectRequest validation"""
        request = AnalyzeProjectRequest(project_path="/test/project")
        assert request.project_path == "/test/project"
        
    def test_trace_task_chain_request(self):
        """Test TraceTaskChainRequest validation"""
        request = TraceTaskChainRequest(
            project_path="/test/project",
            task_name="build"
        )
        assert request.project_path == "/test/project"
        assert request.task_name == "build"
        
    def test_create_task_request(self):
        """Test CreateTaskRequest validation"""
        request = CreateTaskRequest(
            project_path="/test/project",
            task_description="Build the frontend",
            suggested_name="frontend",
            force_complexity="complex",
            domain_hint="build"
        )
        assert request.project_path == "/test/project"
        assert request.task_description == "Build the frontend"
        assert request.suggested_name == "frontend"
        assert request.force_complexity == "complex"
        assert request.domain_hint == "build"
        
    def test_create_task_request_minimal(self):
        """Test CreateTaskRequest with minimal fields"""
        request = CreateTaskRequest(
            project_path="/test/project",
            task_description="Simple task"
        )
        assert request.project_path == "/test/project"
        assert request.task_description == "Simple task"
        assert request.suggested_name is None
        assert request.force_complexity is None
        assert request.domain_hint is None
        
    def test_validate_architecture_request(self):
        """Test ValidateArchitectureRequest validation"""
        request = ValidateArchitectureRequest(project_path="/test/project")
        assert request.project_path == "/test/project"
        
    def test_prune_tasks_request(self):
        """Test PruneTasksRequest validation"""
        request = PruneTasksRequest(
            project_path="/test/project",
            dry_run=False
        )
        assert request.project_path == "/test/project"
        assert request.dry_run is False
        
    def test_prune_tasks_request_default(self):
        """Test PruneTasksRequest with default dry_run"""
        request = PruneTasksRequest(project_path="/test/project")
        assert request.dry_run is True  # Default value
        
    def test_remove_task_request(self):
        """Test RemoveTaskRequest validation"""
        request = RemoveTaskRequest(
            project_path="/test/project",
            task_name="test:old"
        )
        assert request.project_path == "/test/project"
        assert request.task_name == "test:old"


class TestAnalyzeProjectForTasks:
    """Test analyze_project_for_tasks tool function"""
    
    @pytest.mark.asyncio
    async def test_analyze_existing_project(self, temp_project_dir):
        """Test analyzing existing project"""
        request = AnalyzeProjectRequest(project_path=str(temp_project_dir))
        
        result = await analyze_project_for_tasks(request)
        
        assert "error" not in result
        assert "project_path" in result
        assert "project_structure" in result
        assert "existing_tasks" in result
        assert "recommendations" in result
        
        # Verify project structure
        structure = result["project_structure"]
        assert "npm" in structure["package_managers"]
        assert "javascript" in structure["languages"]
        assert structure["has_tests"] is True  # From fixture
        
        # Verify existing tasks
        assert len(result["existing_tasks"]) > 0
        task_names = [task["name"] for task in result["existing_tasks"]]
        assert "build" in task_names
        assert "test" in task_names
        
        # Verify recommendations
        assert len(result["recommendations"]) >= 0
        
    @pytest.mark.asyncio
    async def test_analyze_nonexistent_project(self):
        """Test analyzing non-existent project"""
        request = AnalyzeProjectRequest(project_path="/nonexistent/path")
        
        result = await analyze_project_for_tasks(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]
        
    @pytest.mark.asyncio 
    async def test_analyze_project_exception_handling(self):
        """Test exception handling in analyze_project_for_tasks"""
        request = AnalyzeProjectRequest(project_path="/test")
        
        with patch('wise_mise_mcp.server.TaskAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.analyze_project_structure.side_effect = Exception("Test error")
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await analyze_project_for_tasks(request)
            
            assert "error" in result
            assert "Test error" in result["error"]


class TestTraceTaskChain:
    """Test trace_task_chain tool function"""
    
    @pytest.mark.asyncio
    async def test_trace_existing_task(self, temp_project_dir):
        """Test tracing existing task chain"""
        request = TraceTaskChainRequest(
            project_path=str(temp_project_dir),
            task_name="test"
        )
        
        result = await trace_task_chain(request)
        
        assert "error" not in result or result.get("task_name") == "test"
        if "task_name" in result:
            assert result["task_name"] == "test"
            assert "execution_order" in result
            assert "dependencies" in result
            assert "dependents" in result
            assert "task_details" in result
            
    @pytest.mark.asyncio
    async def test_trace_nonexistent_task(self, temp_project_dir):
        """Test tracing non-existent task"""
        request = TraceTaskChainRequest(
            project_path=str(temp_project_dir),
            task_name="nonexistent"
        )
        
        result = await trace_task_chain(request)
        
        assert "error" in result
        assert "not found" in result["error"].lower()
        
    @pytest.mark.asyncio
    async def test_trace_task_nonexistent_project(self):
        """Test tracing task in non-existent project"""
        request = TraceTaskChainRequest(
            project_path="/nonexistent/path",
            task_name="build"
        )
        
        result = await trace_task_chain(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestCreateTask:
    """Test create_task tool function"""
    
    @pytest.mark.asyncio
    async def test_create_simple_task(self, temp_project_dir):
        """Test creating simple task"""
        request = CreateTaskRequest(
            project_path=str(temp_project_dir),
            task_description="Run unit tests with coverage",
            suggested_name="coverage"
        )
        
        with patch('wise_mise_mcp.server.TaskManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.create_task_intelligently.return_value = {
                "success": True,
                "task_name": "test:coverage",
                "type": "toml_task"
            }
            mock_manager_class.return_value = mock_manager
            
            result = await create_task(request)
            
            assert result["success"] is True
            assert result["task_name"] == "test:coverage"
            
    @pytest.mark.asyncio
    async def test_create_task_with_force_complexity(self, temp_project_dir):
        """Test creating task with forced complexity"""
        request = CreateTaskRequest(
            project_path=str(temp_project_dir),
            task_description="Deploy to production",
            force_complexity="complex"
        )
        
        with patch('wise_mise_mcp.server.TaskManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.create_task_intelligently.return_value = {
                "success": True,
                "task_name": "deploy:production",
                "type": "file_task"
            }
            mock_manager_class.return_value = mock_manager
            
            result = await create_task(request)
            
            # Verify force_complexity was converted to enum
            mock_manager.create_task_intelligently.assert_called_once()
            call_args = mock_manager.create_task_intelligently.call_args
            assert call_args[1]["force_complexity"] == TaskComplexity.COMPLEX
            
    @pytest.mark.asyncio
    async def test_create_task_invalid_complexity(self, temp_project_dir):
        """Test creating task with invalid complexity"""
        request = CreateTaskRequest(
            project_path=str(temp_project_dir),
            task_description="Test task",
            force_complexity="invalid"
        )
        
        result = await create_task(request)
        
        assert "error" in result
        assert "Invalid complexity" in result["error"]
        
    @pytest.mark.asyncio
    async def test_create_task_nonexistent_project(self):
        """Test creating task in non-existent project"""
        request = CreateTaskRequest(
            project_path="/nonexistent/path",
            task_description="Test task"
        )
        
        result = await create_task(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestValidateTaskArchitecture:
    """Test validate_task_architecture tool function"""
    
    @pytest.mark.asyncio
    async def test_validate_existing_project(self, temp_project_dir):
        """Test validating existing project architecture"""
        request = ValidateArchitectureRequest(project_path=str(temp_project_dir))
        
        result = await validate_task_architecture(request)
        
        assert "error" not in result
        # Should contain validation results from analyzer
        
    @pytest.mark.asyncio
    async def test_validate_nonexistent_project(self):
        """Test validating non-existent project"""
        request = ValidateArchitectureRequest(project_path="/nonexistent/path")
        
        result = await validate_task_architecture(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestPruneTasks:
    """Test prune_tasks tool function"""
    
    @pytest.mark.asyncio
    async def test_prune_tasks_dry_run(self, temp_project_dir):
        """Test pruning tasks in dry run mode"""
        request = PruneTasksRequest(
            project_path=str(temp_project_dir),
            dry_run=True
        )
        
        with patch('wise_mise_mcp.server.TaskAnalyzer') as mock_analyzer_class:
            mock_analyzer = Mock()
            mock_analyzer.find_redundant_tasks.return_value = [
                {"task": "redundant_task", "reason": "No dependencies"}
            ]
            mock_analyzer_class.return_value = mock_analyzer
            
            result = await prune_tasks(request)
            
            assert result["dry_run"] is True
            assert "redundant_tasks" in result
            assert len(result["redundant_tasks"]) == 1
            
    @pytest.mark.asyncio
    async def test_prune_tasks_actual_removal(self, temp_project_dir):
        """Test actually removing redundant tasks"""
        request = PruneTasksRequest(
            project_path=str(temp_project_dir),
            dry_run=False
        )
        
        with patch('wise_mise_mcp.server.TaskAnalyzer') as mock_analyzer_class:
            with patch('wise_mise_mcp.server.TaskManager') as mock_manager_class:
                mock_analyzer = Mock()
                mock_analyzer.find_redundant_tasks.return_value = [
                    {"task": "redundant_task", "reason": "No dependencies"}
                ]
                mock_analyzer_class.return_value = mock_analyzer
                
                mock_manager = Mock()
                mock_manager.remove_task.return_value = {"success": True}
                mock_manager_class.return_value = mock_manager
                
                result = await prune_tasks(request)
                
                assert result["dry_run"] is False
                assert "removed_tasks" in result
                assert "redundant_task" in result["removed_tasks"]
                
    @pytest.mark.asyncio
    async def test_prune_tasks_nonexistent_project(self):
        """Test pruning tasks in non-existent project"""
        request = PruneTasksRequest(project_path="/nonexistent/path")
        
        result = await prune_tasks(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestRemoveTask:
    """Test remove_task tool function"""
    
    @pytest.mark.asyncio
    async def test_remove_existing_task(self, temp_project_dir):
        """Test removing existing task"""
        request = RemoveTaskRequest(
            project_path=str(temp_project_dir),
            task_name="test:old"
        )
        
        with patch('wise_mise_mcp.server.TaskManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.remove_task.return_value = {
                "success": True,
                "message": "Removed TOML task 'test:old'"
            }
            mock_manager_class.return_value = mock_manager
            
            result = await remove_task(request)
            
            assert result["success"] is True
            assert "test:old" in result["message"]
            
    @pytest.mark.asyncio
    async def test_remove_nonexistent_task(self, temp_project_dir):
        """Test removing non-existent task"""
        request = RemoveTaskRequest(
            project_path=str(temp_project_dir),
            task_name="nonexistent"
        )
        
        with patch('wise_mise_mcp.server.TaskManager') as mock_manager_class:
            mock_manager = Mock()
            mock_manager.remove_task.return_value = {
                "error": "Task 'nonexistent' not found"
            }
            mock_manager_class.return_value = mock_manager
            
            result = await remove_task(request)
            
            assert "error" in result
            assert "not found" in result["error"]
            
    @pytest.mark.asyncio
    async def test_remove_task_nonexistent_project(self):
        """Test removing task from non-existent project"""
        request = RemoveTaskRequest(
            project_path="/nonexistent/path",
            task_name="test"
        )
        
        result = await remove_task(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestGetTaskRecommendations:
    """Test get_task_recommendations tool function"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, temp_project_dir):
        """Test getting task recommendations"""
        request = AnalyzeProjectRequest(project_path=str(temp_project_dir))
        
        result = await get_task_recommendations(request)
        
        assert "error" not in result
        assert "project_path" in result
        assert "new_task_recommendations" in result
        assert "architecture_improvements" in result
        assert "redundancy_analysis" in result
        assert "summary" in result
        
        # Verify summary statistics
        summary = result["summary"]
        assert "total_existing_tasks" in summary
        assert "domains_in_use" in summary
        assert "high_priority_recommendations" in summary
        
    @pytest.mark.asyncio
    async def test_get_recommendations_nonexistent_project(self):
        """Test getting recommendations for non-existent project"""
        request = AnalyzeProjectRequest(project_path="/nonexistent/path")
        
        result = await get_task_recommendations(request)
        
        assert "error" in result
        assert "does not exist" in result["error"]


class TestGetMiseArchitectureRules:
    """Test get_mise_architecture_rules tool function"""
    
    @pytest.mark.asyncio
    async def test_get_architecture_rules(self):
        """Test getting mise architecture rules"""
        result = await get_mise_architecture_rules()
        
        assert "domains" in result
        assert "naming_conventions" in result
        assert "file_structure" in result
        assert "task_types" in result
        assert "dependencies" in result
        assert "performance" in result
        
        # Verify domain information
        domains = result["domains"]
        assert "core_domains" in domains
        assert "descriptions" in domains
        
        # Verify all expected domains are present
        expected_domains = {
            "build", "test", "lint", "dev", "deploy", 
            "db", "ci", "docs", "clean", "setup"
        }
        assert set(domains["core_domains"]) == expected_domains
        
        # Verify naming conventions
        naming = result["naming_conventions"]
        assert "hierarchical_structure" in naming
        assert ":" in naming["hierarchical_structure"]
        
        # Verify file structure
        file_struct = result["file_structure"]
        assert ".mise.toml" in file_struct["root_config"]
        assert ".mise/" in file_struct["task_directory"]


class TestPromptFunctions:
    """Test prompt functions"""
    
    @pytest.mark.asyncio
    async def test_mise_task_expert_guidance(self):
        """Test mise task expert guidance prompt"""
        result = await mise_task_expert_guidance()
        
        assert isinstance(result, str)
        assert len(result) > 100  # Should be substantial guidance
        assert "mise task" in result.lower()
        assert "domain" in result.lower()
        assert "architecture" in result.lower()
        
        # Should contain key concepts
        assert "10 domains" in result or "domains" in result
        assert "hierarchical" in result.lower()
        assert ".mise.toml" in result
        
    @pytest.mark.asyncio
    async def test_task_chain_analyst(self):
        """Test task chain analyst prompt"""
        result = await task_chain_analyst()
        
        assert isinstance(result, str)
        assert len(result) > 100  # Should be substantial guidance
        assert "task chain" in result.lower()
        assert "dependency" in result.lower()
        assert "execution" in result.lower()
        
        # Should contain analysis concepts
        assert "parallel" in result.lower()
        assert "topological" in result.lower() or "execution order" in result.lower()


class TestServerIntegration:
    """Test integration aspects of the server"""
    
    def test_all_request_models_importable(self):
        """Test that all request models can be imported and used"""
        from wise_mise_mcp.server import (
            AnalyzeProjectRequest,
            TraceTaskChainRequest,
            CreateTaskRequest,
            ValidateArchitectureRequest,
            PruneTasksRequest,
            RemoveTaskRequest
        )
        
        # Should be able to create instances
        AnalyzeProjectRequest(project_path="/test")
        TraceTaskChainRequest(project_path="/test", task_name="build")
        CreateTaskRequest(project_path="/test", task_description="Test")
        ValidateArchitectureRequest(project_path="/test")
        PruneTasksRequest(project_path="/test")
        RemoveTaskRequest(project_path="/test", task_name="old")
        
    def test_fastmcp_app_structure(self):
        """Test that FastMCP app is properly structured"""
        from wise_mise_mcp.server import app
        
        # Should have app instance
        assert app is not None
        assert hasattr(app, 'tool')
        assert hasattr(app, 'prompt')
        
    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test that error handling is consistent across all tools"""
        nonexistent_path = "/nonexistent/path"
        
        # All tools should handle non-existent paths gracefully
        tools_to_test = [
            (analyze_project_for_tasks, AnalyzeProjectRequest(project_path=nonexistent_path)),
            (trace_task_chain, TraceTaskChainRequest(project_path=nonexistent_path, task_name="build")),
            (create_task, CreateTaskRequest(project_path=nonexistent_path, task_description="test")),
            (validate_task_architecture, ValidateArchitectureRequest(project_path=nonexistent_path)),
            (prune_tasks, PruneTasksRequest(project_path=nonexistent_path)),
            (remove_task, RemoveTaskRequest(project_path=nonexistent_path, task_name="test"))
        ]
        
        for tool_func, request in tools_to_test:
            result = await tool_func(request)
            
            # All should return error dict instead of raising exception
            assert isinstance(result, dict)
            assert "error" in result
            assert "does not exist" in result["error"]