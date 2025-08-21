"""
Performance tests for handling large projects and complex configurations
"""

import pytest
import tempfile
import time
import json
from pathlib import Path
from typing import List

from wise_mise_mcp.server import (
    analyze_project_for_tasks,
    AnalyzeProjectRequest
)
from wise_mise_mcp.analyzer import TaskAnalyzer
from wise_mise_mcp.models import ProjectStructure


class TestLargeProjectPerformance:
    """Test performance with large project structures"""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_large_monorepo_analysis_performance(self):
        """Test analysis performance with large monorepo (50+ services)"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create large monorepo
            num_services = 50
            self._create_large_monorepo(project_path, num_services)
            
            # Measure analysis time
            start_time = time.time()
            
            analyzer = TaskAnalyzer(project_path)
            structure = analyzer.analyze_project_structure()
            existing_tasks = analyzer.extract_existing_tasks()
            recommendations = analyzer.get_task_recommendations()
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            # Performance assertions
            assert analysis_time < 15.0, f"Analysis took too long: {analysis_time}s"
            
            # Verify results are reasonable
            assert len(existing_tasks) > num_services * 2  # At least 2 tasks per service
            assert isinstance(structure, ProjectStructure)
            assert len(recommendations) >= 0
            
            print(f"Analyzed {num_services} services in {analysis_time:.2f}s")
            print(f"Found {len(existing_tasks)} existing tasks")
            print(f"Generated {len(recommendations)} recommendations")
            
    @pytest.mark.performance
    def test_deep_task_dependency_chain_performance(self):
        """Test performance with deep task dependency chains"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project with deep dependency chain
            chain_depth = 20
            self._create_deep_dependency_chain(project_path, chain_depth)
            
            start_time = time.time()
            
            analyzer = TaskAnalyzer(project_path)
            tasks = analyzer.extract_existing_tasks()
            graph = analyzer.build_dependency_graph(tasks)
            
            # Trace the deepest chain
            trace_result = analyzer.trace_task_chain(f"task_{chain_depth - 1}")
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            # Performance assertions
            assert analysis_time < 5.0, f"Deep chain analysis took too long: {analysis_time}s"
            
            # Verify dependency chain structure
            assert len(trace_result["execution_order"]) == chain_depth
            assert len(trace_result["dependencies"]) == chain_depth - 1
            
            print(f"Traced {chain_depth}-deep chain in {analysis_time:.2f}s")
            
    @pytest.mark.performance
    def test_wide_parallel_tasks_performance(self):
        """Test performance with many parallel tasks"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create project with many parallel tasks
            num_parallel_tasks = 100
            self._create_wide_parallel_tasks(project_path, num_parallel_tasks)
            
            start_time = time.time()
            
            analyzer = TaskAnalyzer(project_path)
            tasks = analyzer.extract_existing_tasks()
            graph = analyzer.build_dependency_graph(tasks)
            
            # Find parallel groups
            parallel_groups = analyzer._find_parallel_groups(graph)
            
            end_time = time.time()
            analysis_time = end_time - start_time
            
            # Performance assertions
            assert analysis_time < 10.0, f"Parallel analysis took too long: {analysis_time}s"
            
            # Verify parallel structure
            assert len(tasks) >= num_parallel_tasks
            # Most tasks should be in the first parallel group (independent)
            assert len(parallel_groups[0]) >= num_parallel_tasks * 0.8
            
            print(f"Analyzed {num_parallel_tasks} parallel tasks in {analysis_time:.2f}s")
            
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_analysis_performance(self):
        """Test performance of concurrent analysis operations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create moderately complex project
            self._create_complex_project(project_path)
            
            # Run multiple analyses concurrently
            num_concurrent = 10
            
            start_time = time.time()
            
            import asyncio
            
            async def run_analysis():
                request = AnalyzeProjectRequest(project_path=str(project_path))
                return await analyze_project_for_tasks(request)
                
            # Run concurrent analyses
            tasks = [run_analysis() for _ in range(num_concurrent)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Performance assertions
            assert total_time < 30.0, f"Concurrent analysis took too long: {total_time}s"
            
            # Verify all analyses succeeded
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) == num_concurrent
            
            # Results should be consistent
            first_result = successful_results[0]
            for result in successful_results[1:]:
                assert len(result["existing_tasks"]) == len(first_result["existing_tasks"])
                
            avg_time = total_time / num_concurrent
            print(f"Average concurrent analysis time: {avg_time:.2f}s")
            
    @pytest.mark.performance
    def test_memory_usage_large_project(self):
        """Test memory usage with large projects"""
        import psutil
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create very large project
            self._create_memory_intensive_project(project_path)
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform memory-intensive operations
            analyzer = TaskAnalyzer(project_path)
            structure = analyzer.analyze_project_structure()
            tasks = analyzer.extract_existing_tasks()
            graph = analyzer.build_dependency_graph(tasks)
            recommendations = analyzer.get_task_recommendations()
            validation = analyzer.validate_task_architecture()
            
            peak_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_usage = peak_memory - initial_memory
            
            # Memory usage should be reasonable (< 500MB for large projects)
            assert memory_usage < 500, f"Memory usage too high: {memory_usage}MB"
            
            print(f"Memory usage: {memory_usage:.1f}MB")
            print(f"Processed {len(tasks)} tasks, {len(recommendations)} recommendations")
            
    def _create_large_monorepo(self, project_path: Path, num_services: int):
        """Create a large monorepo with many services"""
        service_types = ["frontend", "backend", "api", "worker", "shared"]
        
        # Create services
        for i in range(num_services):
            service_type = service_types[i % len(service_types)]
            service_name = f"{service_type}-{i}"
            service_path = project_path / service_name
            service_path.mkdir()
            (service_path / "src").mkdir()
            
            # Create package.json for each service
            package_json = {
                "name": service_name,
                "version": "1.0.0",
                "scripts": {
                    "build": f"echo Building {service_name}",
                    "test": f"echo Testing {service_name}",
                    "start": f"echo Starting {service_name}"
                }
            }
            
            with open(service_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
        # Create root package.json
        root_package = {
            "name": "large-monorepo",
            "version": "1.0.0",
            "workspaces": [f"{service_types[i % len(service_types)]}-{i}" for i in range(num_services)]
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(root_package, f)
            
        # Create large .mise.toml with tasks for each service
        mise_config = """
[tools]
node = "20"

[tasks.install]
description = "Install all dependencies"
run = "npm install"

"""
        
        # Add tasks for each service
        for i in range(num_services):
            service_type = service_types[i % len(service_types)]
            service_name = f"{service_type}-{i}"
            
            mise_config += f"""
[tasks."build:{service_name}"]
description = "Build {service_name}"
run = "cd {service_name} && npm run build"
sources = ["{service_name}/src/**/*"]

[tasks."test:{service_name}"]
description = "Test {service_name}"
run = "cd {service_name} && npm test"
sources = ["{service_name}/src/**/*"]
depends = ["build:{service_name}"]

[tasks."start:{service_name}"]
description = "Start {service_name}"
run = "cd {service_name} && npm start"
depends = ["build:{service_name}"]
"""
        
        # Add aggregate tasks
        all_builds = ", ".join([f'"build:{service_types[i % len(service_types)]}-{i}"' for i in range(num_services)])
        all_tests = ", ".join([f'"test:{service_types[i % len(service_types)]}-{i}"' for i in range(num_services)])
        
        mise_config += f"""
[tasks."build:all"]
description = "Build all services"
depends = [{all_builds}]

[tasks."test:all"]
description = "Test all services"
depends = [{all_tests}]

[tasks.ci]
description = "Full CI pipeline"
depends = ["build:all", "test:all"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config)
            
    def _create_deep_dependency_chain(self, project_path: Path, chain_depth: int):
        """Create project with deep task dependency chain"""
        package_json = {
            "name": "deep-chain-project",
            "version": "1.0.0"
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f)
            
        # Create mise config with deep chain
        mise_config = """
[tools]
node = "20"

"""
        
        # Create chain: task_0 -> task_1 -> ... -> task_n
        for i in range(chain_depth):
            depends_clause = f'depends = ["task_{i-1}"]' if i > 0 else ""
            
            mise_config += f"""
[tasks."task_{i}"]
description = "Task {i} in chain"
run = "echo Task {i}"
{depends_clause}

"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config)
            
    def _create_wide_parallel_tasks(self, project_path: Path, num_tasks: int):
        """Create project with many independent parallel tasks"""
        package_json = {
            "name": "wide-parallel-project", 
            "version": "1.0.0"
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f)
            
        # Create mise config with many parallel tasks
        mise_config = """
[tools]
node = "20"

# Common base task
[tasks.setup]
description = "Setup project"
run = "echo Setup complete"

"""
        
        # Create many independent tasks
        for i in range(num_tasks):
            mise_config += f"""
[tasks."parallel_task_{i}"]
description = "Parallel task {i}"
run = "echo Parallel task {i}"
depends = ["setup"]

"""
        
        # Create aggregate task that depends on all parallel tasks
        all_parallel = ", ".join([f'"parallel_task_{i}"' for i in range(num_tasks)])
        
        mise_config += f"""
[tasks."aggregate"]
description = "Aggregate all parallel tasks"
depends = [{all_parallel}]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config)
            
    def _create_complex_project(self, project_path: Path):
        """Create moderately complex project for concurrent testing"""
        # Create structure
        (project_path / "frontend" / "src").mkdir(parents=True)
        (project_path / "backend" / "src").mkdir(parents=True)
        (project_path / "tests").mkdir()
        
        # Frontend package.json
        frontend_pkg = {
            "name": "frontend",
            "scripts": {"build": "webpack", "test": "jest"}
        }
        with open(project_path / "frontend" / "package.json", "w") as f:
            json.dump(frontend_pkg, f)
            
        # Backend pyproject.toml
        (project_path / "backend" / "pyproject.toml").write_text("""
[project]
name = "backend"
version = "1.0.0"
""")
        
        # Complex mise config
        mise_config = """
[tools]
node = "20"
python = "3.11"

[tasks."build:frontend"]
run = "cd frontend && npm run build"

[tasks."build:backend"]
run = "cd backend && python -m build"

[tasks."test:frontend"]
run = "cd frontend && npm test"

[tasks."test:backend"]
run = "cd backend && pytest"

[tasks.build]
depends = ["build:frontend", "build:backend"]

[tasks.test]
depends = ["test:frontend", "test:backend"]

[tasks.ci]
depends = ["build", "test"]
"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config)
            
    def _create_memory_intensive_project(self, project_path: Path):
        """Create project designed to test memory usage"""
        # Create many directories and files
        for i in range(20):
            module_dir = project_path / f"module_{i}"
            module_dir.mkdir()
            (module_dir / "src").mkdir()
            (module_dir / "tests").mkdir()
            
            # Create files in each module
            for j in range(10):
                (module_dir / "src" / f"file_{j}.py").write_text(f"# Module {i}, File {j}\nprint('Hello')\n")
                (module_dir / "tests" / f"test_file_{j}.py").write_text(f"def test_{j}(): pass\n")
                
        # Create very large mise config
        large_config = """
[tools]
node = "20"
python = "3.11"

"""
        
        # Add many tasks with complex configuration
        for i in range(200):  # 200 tasks
            large_config += f"""
[tasks."task_{i}"]
description = "Generated task {i} for performance testing"
run = [
    "echo Starting task {i}",
    "sleep 0.1",
    "echo Task {i} processing",
    "echo Task {i} completed"
]
sources = [
    "module_{i % 20}/src/**/*.py",
    "module_{i % 20}/tests/**/*.py"
]
outputs = [
    "build/task_{i}/",
    "logs/task_{i}.log"
]
env = {{
    "TASK_ID" = "{i}",
    "TASK_NAME" = "task_{i}",
    "MODULE_PATH" = "module_{i % 20}"
}}

"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(large_config)


class TestPerformanceBenchmarks:
    """Benchmark specific operations for performance regression testing"""
    
    @pytest.mark.performance
    def test_task_extraction_benchmark(self, benchmark):
        """Benchmark task extraction from configuration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            self._create_benchmark_project(project_path, num_tasks=50)
            
            analyzer = TaskAnalyzer(project_path)
            
            # Benchmark the extraction
            result = benchmark(analyzer.extract_existing_tasks)
            
            assert len(result) == 50
            
    @pytest.mark.performance
    def test_dependency_graph_build_benchmark(self, benchmark):
        """Benchmark dependency graph building"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) 
            self._create_benchmark_project(project_path, num_tasks=50)
            
            analyzer = TaskAnalyzer(project_path)
            tasks = analyzer.extract_existing_tasks()
            
            # Benchmark graph building
            result = benchmark(analyzer.build_dependency_graph, tasks)
            
            assert len(result.nodes()) == 50
            
    @pytest.mark.performance
    def test_recommendations_benchmark(self, benchmark):
        """Benchmark task recommendation generation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            self._create_benchmark_project(project_path, num_tasks=20)
            
            analyzer = TaskAnalyzer(project_path)
            
            # Benchmark recommendation generation
            result = benchmark(analyzer.get_task_recommendations)
            
            assert isinstance(result, list)
            
    def _create_benchmark_project(self, project_path: Path, num_tasks: int):
        """Create standardized project for benchmarking"""
        # Create realistic project structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        
        package_json = {
            "name": "benchmark-project",
            "version": "1.0.0",
            "scripts": {"build": "webpack", "test": "jest"},
            "devDependencies": {"webpack": "^5.0.0", "jest": "^29.0.0"}
        }
        
        with open(project_path / "package.json", "w") as f:
            json.dump(package_json, f)
            
        # Create mise config with specified number of tasks
        mise_config = """
[tools]
node = "20"

"""
        
        for i in range(num_tasks):
            depends = f'depends = ["task_{i-1}"]' if i > 0 and i % 10 != 0 else ""
            
            mise_config += f"""
[tasks."task_{i}"]
description = "Benchmark task {i}"
run = "echo Task {i}"
sources = ["src/**/*", "package.json"]
{depends}

"""
        
        with open(project_path / ".mise.toml", "w") as f:
            f.write(mise_config)