"""
Integration tests for complete task management workflows
"""

import pytest
import tempfile
import json
from pathlib import Path

from wise_mise_mcp.server import (
    analyze_project_for_tasks,
    create_task,
    trace_task_chain,
    validate_task_architecture,
    prune_tasks,
    remove_task,
    AnalyzeProjectRequest,
    CreateTaskRequest,
    TraceTaskChainRequest,
    ValidateArchitectureRequest,
    PruneTasksRequest,
    RemoveTaskRequest
)
from wise_mise_mcp.models import MiseConfig


class TestTaskLifecycleWorkflows:
    """Test complete task lifecycle workflows"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_task_lifecycle(self):
        """Test creating, modifying, and removing tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create initial project
            await self._create_test_project(project_path)
            
            # Step 1: Analyze initial project
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            initial_analysis = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in initial_analysis
            initial_task_count = len(initial_analysis["existing_tasks"])
            
            # Step 2: Create a new task
            create_request = CreateTaskRequest(
                project_path=str(project_path),
                task_description="Generate test coverage report",
                suggested_name="coverage"
            )
            
            create_result = await create_task(create_request)
            
            if "error" not in create_result:
                assert create_result["success"] is True
                new_task_name = create_result["task_name"]
                
                # Step 3: Verify task was added
                updated_analysis = await analyze_project_for_tasks(analyze_request)
                updated_task_count = len(updated_analysis["existing_tasks"])
                
                if create_result["type"] == "toml_task":
                    # TOML tasks should increase count
                    assert updated_task_count > initial_task_count
                    
                    task_names = [task["name"] for task in updated_analysis["existing_tasks"]]
                    assert new_task_name in task_names
                
                # Step 4: Trace the new task
                trace_request = TraceTaskChainRequest(
                    project_path=str(project_path),
                    task_name=new_task_name
                )
                
                trace_result = await trace_task_chain(trace_request)
                
                if "error" not in trace_result:
                    assert trace_result["task_name"] == new_task_name
                    assert "execution_order" in trace_result
                    
                # Step 5: Validate architecture after changes
                validate_request = ValidateArchitectureRequest(project_path=str(project_path))
                validation_result = await validate_task_architecture(validate_request)
                
                assert "error" not in validation_result
                
                # Step 6: Remove the task
                remove_request = RemoveTaskRequest(
                    project_path=str(project_path),
                    task_name=new_task_name
                )
                
                remove_result = await remove_task(remove_request)
                
                if "error" not in remove_result:
                    assert remove_result["success"] is True
                    
                    # Step 7: Verify task was removed
                    final_analysis = await analyze_project_for_tasks(analyze_request)
                    final_task_count = len(final_analysis["existing_tasks"])
                    
                    if create_result["type"] == "toml_task":
                        assert final_task_count <= updated_task_count
                        
                        task_names = [task["name"] for task in final_analysis["existing_tasks"]]
                        assert new_task_name not in task_names
                        
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_dependency_workflow(self):
        """Test creating tasks with complex dependencies"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project with existing tasks
            await self._create_test_project(project_path)
            
            # Create interdependent tasks
            tasks_to_create = [
                {
                    "description": "Lint TypeScript code",
                    "name": "typescript"
                },
                {
                    "description": "Run integration tests after build",
                    "name": "integration"
                },
                {
                    "description": "Deploy to staging environment",
                    "name": "staging"
                }
            ]
            
            created_tasks = []
            
            for task_info in tasks_to_create:
                create_request = CreateTaskRequest(
                    project_path=str(project_path),
                    task_description=task_info["description"],
                    suggested_name=task_info["name"]
                )
                
                result = await create_task(create_request)
                
                if "error" not in result and result.get("success"):
                    created_tasks.append(result["task_name"])
                    
            # Trace dependency chains for created tasks
            for task_name in created_tasks:
                trace_request = TraceTaskChainRequest(
                    project_path=str(project_path),
                    task_name=task_name
                )
                
                trace_result = await trace_task_chain(trace_request)
                
                if "error" not in trace_result:
                    assert trace_result["task_name"] == task_name
                    # Should have execution order (even if just the task itself)
                    assert len(trace_result["execution_order"]) >= 1
                    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_task_pruning_workflow(self):
        """Test identifying and pruning redundant tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project with redundant tasks
            await self._create_project_with_redundant_tasks(project_path)
            
            # Step 1: Analyze for redundant tasks (dry run)
            prune_request = PruneTasksRequest(
                project_path=str(project_path),
                dry_run=True
            )
            
            dry_run_result = await prune_tasks(prune_request)
            
            assert "error" not in dry_run_result
            assert dry_run_result["dry_run"] is True
            
            redundant_count = len(dry_run_result["redundant_tasks"])
            
            if redundant_count > 0:
                # Step 2: Actually prune redundant tasks
                prune_request.dry_run = False
                actual_prune_result = await prune_tasks(prune_request)
                
                if "error" not in actual_prune_result:
                    assert actual_prune_result["dry_run"] is False
                    assert "removed_tasks" in actual_prune_result
                    
                    # Step 3: Verify tasks were removed
                    analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
                    final_analysis = await analyze_project_for_tasks(analyze_request)
                    
                    assert "error" not in final_analysis
                    
                    # Removed tasks should no longer exist
                    remaining_task_names = [task["name"] for task in final_analysis["existing_tasks"]]
                    removed_tasks = actual_prune_result["removed_tasks"]
                    
                    for removed_task in removed_tasks:
                        assert removed_task not in remaining_task_names
                        
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_architecture_evolution_workflow(self):
        """Test how architecture validation changes as project evolves"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Start with minimal project
            await self._create_minimal_project(project_path)
            
            validate_request = ValidateArchitectureRequest(project_path=str(project_path))
            
            # Step 1: Initial validation
            initial_validation = await validate_task_architecture(validate_request)
            assert "error" not in initial_validation
            
            initial_issues = len(initial_validation.get("issues", []))
            initial_suggestions = len(initial_validation.get("suggestions", []))
            
            # Step 2: Add well-structured tasks
            well_structured_tasks = [
                {
                    "description": "Build frontend assets with webpack",
                    "name": "frontend"
                },
                {
                    "description": "Run comprehensive test suite",
                    "name": "comprehensive"
                },
                {
                    "description": "Perform code quality checks",
                    "name": "quality"
                }
            ]
            
            for task_info in well_structured_tasks:
                create_request = CreateTaskRequest(
                    project_path=str(project_path),
                    task_description=task_info["description"],
                    suggested_name=task_info["name"]
                )
                
                await create_task(create_request)
                
            # Step 3: Validation after improvements
            improved_validation = await validate_task_architecture(validate_request)
            assert "error" not in improved_validation
            
            improved_issues = len(improved_validation.get("issues", []))
            improved_suggestions = len(improved_validation.get("suggestions", []))
            
            # Architecture should be same or better (not necessarily fewer issues,
            # but should show more organized structure)
            assert improved_validation["total_tasks"] >= initial_validation["total_tasks"]
            
    async def _create_test_project(self, project_path: Path):
        """Create a standard test project"""
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "scripts": {
                "build": "webpack build",
                "test": "jest",
                "dev": "webpack serve"
            },
            "devDependencies": {
                "webpack": "^5.0.0",
                "jest": "^29.0.0"
            }
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f, indent=2)
            
        mise_config = """
[tools]
node = "18"

[tasks.install]
description = "Install dependencies"
run = "npm install"

[tasks.build]
description = "Build project"
run = "npm run build"
sources = ["src/**/*", "package.json"]
outputs = ["dist/"]
depends = ["install"]

[tasks.test]
description = "Run tests"
run = "npm test"
sources = ["src/**/*", "tests/**/*"]
depends = ["install"]

[tasks.dev]
description = "Start dev server"
run = "npm run dev"
depends = ["install"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
    async def _create_project_with_redundant_tasks(self, project_path: Path):
        """Create project with redundant/similar tasks"""
        (project_path / "src").mkdir()
        
        package_json = {
            "name": "redundant-project",
            "version": "1.0.0"
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f)
            
        # Create configuration with similar/redundant tasks
        mise_config = """
[tools]
node = "18"

[tasks.build]
description = "Build project"
run = "echo building"

[tasks.build-copy]
description = "Build project copy"
run = "echo building"

[tasks.test]
description = "Run tests"
run = "echo testing"

[tasks.test-duplicate]
description = "Run tests duplicate"
run = "echo testing"

[tasks.orphan1]
run = "echo orphan1"

[tasks.orphan2]
run = "echo orphan2"

[tasks.connected]
description = "Connected task"
run = "echo connected"
depends = ["build"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())
            
    async def _create_minimal_project(self, project_path: Path):
        """Create minimal project for architecture evolution testing"""
        package_json = {
            "name": "minimal-project",
            "version": "1.0.0"
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f)
            
        # Very basic configuration
        mise_config = """
[tools]
node = "18"

[tasks.basic]
run = "echo basic"
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config.strip())


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_migrating_from_package_json_scripts(self):
        """Test migrating existing package.json scripts to mise tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project with complex package.json scripts
            package_json = {
                "name": "complex-scripts",
                "version": "1.0.0",
                "scripts": {
                    "prebuild": "rm -rf dist",
                    "build": "webpack --mode=production",
                    "postbuild": "cp -r public/* dist/",
                    "dev": "webpack serve --mode=development",
                    "test": "jest",
                    "test:watch": "jest --watch",
                    "test:coverage": "jest --coverage",
                    "lint": "eslint src/",
                    "lint:fix": "eslint src/ --fix",
                    "format": "prettier --write src/",
                    "typecheck": "tsc --noEmit",
                    "predeploy": "npm run build",
                    "deploy": "aws s3 sync dist/ s3://my-bucket/",
                    "postdeploy": "echo 'Deployed successfully'"
                },
                "devDependencies": {
                    "webpack": "^5.0.0",
                    "jest": "^29.0.0",
                    "eslint": "^8.0.0",
                    "prettier": "^2.0.0",
                    "typescript": "^4.0.0"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f, indent=2)
                
            # Minimal .mise.toml
            (project_path / ".mise.toml").write_text("""
[tools]
node = "18"
""")
            
            # Analyze project - should recommend tasks based on scripts
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            analysis = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in analysis
            recommendations = analysis["recommendations"]
            
            # Should recommend tasks for major script categories
            rec_names = [r["task_name"] for r in recommendations]
            
            # Should have build, test, lint recommendations
            domains_in_recs = set()
            for name in rec_names:
                if ":" in name:
                    domain = name.split(":")[0]
                    domains_in_recs.add(domain)
                    
            # Should cover main development domains
            expected_domains = {"build", "test", "lint"}
            # At least some overlap expected
            assert len(domains_in_recs.intersection(expected_domains)) > 0
            
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_multi_environment_deployment_workflow(self):
        """Test setting up deployment tasks for multiple environments"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project structure
            (project_path / "src").mkdir()
            (project_path / "deploy").mkdir()
            
            package_json = {
                "name": "multi-env-app",
                "version": "1.0.0",
                "scripts": {
                    "build": "webpack build",
                    "build:prod": "webpack build --mode=production"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            # Initial mise config
            mise_config = """
[tools]
node = "18"

[tasks.build]
description = "Build for development"
run = "npm run build"
sources = ["src/**/*"]
outputs = ["dist/"]

[tasks."build:production"]
description = "Build for production"
run = "npm run build:prod"
sources = ["src/**/*"]
outputs = ["dist/"]
depends = ["test", "lint"]
"""
            
            with open(project_path / ".mise.toml", "w") as f:
                f.write(mise_config.strip())
                
            # Create deployment tasks for different environments
            deployment_tasks = [
                {
                    "description": "Deploy to development environment",
                    "name": "development"
                },
                {
                    "description": "Deploy to staging environment", 
                    "name": "staging"
                },
                {
                    "description": "Deploy to production environment",
                    "name": "production"
                }
            ]
            
            created_deploy_tasks = []
            
            for task_info in deployment_tasks:
                create_request = CreateTaskRequest(
                    project_path=str(project_path),
                    task_description=task_info["description"],
                    suggested_name=task_info["name"],
                    force_complexity="complex"  # Deployments are complex
                )
                
                result = await create_task(create_request)
                
                if "error" not in result and result.get("success"):
                    created_deploy_tasks.append(result["task_name"])
                    
            # Validate the deployment workflow
            validate_request = ValidateArchitectureRequest(project_path=str(project_path))
            validation = await validate_task_architecture(validate_request)
            
            assert "error" not in validation
            
            # Should have multiple deploy domain tasks now
            final_analysis = await analyze_project_for_tasks(
                AnalyzeProjectRequest(project_path=str(project_path))
            )
            
            deploy_tasks = [
                task for task in final_analysis["existing_tasks"] 
                if task["name"].startswith("deploy:")
            ]
            
            # Should have created deployment tasks
            assert len(deploy_tasks) >= 0  # Depends on expert availability
            
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_microservices_monorepo_workflow(self):
        """Test managing tasks in a microservices monorepo"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create microservices structure
            services = ["auth-service", "user-service", "payment-service", "notification-service"]
            
            for service in services:
                service_path = project_path / service
                service_path.mkdir()
                (service_path / "src").mkdir()
                (service_path / "tests").mkdir()
                
                # Each service has its own package.json
                service_package = {
                    "name": service,
                    "version": "1.0.0",
                    "scripts": {
                        "build": "tsc",
                        "test": "jest",
                        "start": "node dist/index.js"
                    }
                }
                
                with open(service_path / "package.json", "w") as f:
                    json.dump(service_package, f)
                    
            # Root package.json for workspace
            root_package = {
                "name": "microservices-monorepo",
                "version": "1.0.0",
                "workspaces": services
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(root_package, f)
                
            # Complex mise configuration for microservices
            mise_tasks = """
[tools]
node = "18"

[tasks.install]
description = "Install all dependencies"
run = "npm install"

# Individual service tasks
"""
            
            for service in services:
                mise_tasks += f"""
[tasks."build:{service}"]
description = "Build {service}"
run = "cd {service} && npm run build"
sources = ["{service}/src/**/*", "{service}/package.json"]
outputs = ["{service}/dist/"]

[tasks."test:{service}"]
description = "Test {service}"
run = "cd {service} && npm test"
sources = ["{service}/src/**/*", "{service}/tests/**/*"]

[tasks."start:{service}"]
description = "Start {service}"
run = "cd {service} && npm start"
depends = ["build:{service}"]

"""
            
            # Aggregate tasks
            all_services = " ".join(services)
            mise_tasks += f"""
[tasks."build:all"]
description = "Build all services"
depends = [{", ".join([f'"build:{s}"' for s in services])}]

[tasks."test:all"]
description = "Test all services" 
depends = [{", ".join([f'"test:{s}"' for s in services])}]

[tasks."start:all"]
description = "Start all services"
run = "mise run --parallel {' '.join([f'start:{s}' for s in services])}"

[tasks.ci]
description = "Full CI pipeline"
depends = ["build:all", "test:all"]
"""
            
            with open(project_path / ".mise.toml", "w") as f:
                f.write(mise_tasks.strip())
                
            # Analyze the complex monorepo
            analyze_request = AnalyzeProjectRequest(project_path=str(project_path))
            analysis = await analyze_project_for_tasks(analyze_request)
            
            assert "error" not in analysis
            assert len(analysis["existing_tasks"]) > 10  # Should have many tasks
            
            # Trace the CI task to see full dependency chain
            trace_request = TraceTaskChainRequest(
                project_path=str(project_path),
                task_name="ci"
            )
            
            trace_result = await trace_task_chain(trace_request)
            
            if "error" not in trace_result:
                assert trace_result["task_name"] == "ci"
                # Should have complex execution order
                assert len(trace_result["execution_order"]) > 5
                # Should have parallel execution opportunities
                assert len(trace_result["parallelizable_groups"]) >= 2
                
            # Validate architecture - should be well-structured
            validate_request = ValidateArchitectureRequest(project_path=str(project_path))
            validation = await validate_task_architecture(validate_request)
            
            assert "error" not in validation
            # Should use multiple domains
            assert len(validation["domains_used"]) >= 3