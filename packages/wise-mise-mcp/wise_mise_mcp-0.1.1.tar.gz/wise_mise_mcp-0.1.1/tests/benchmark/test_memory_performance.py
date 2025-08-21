"""
Memory Usage and Performance Profiling Tests

Comprehensive memory usage analysis for the wise-mise-mcp server including:
- Memory leak detection
- Peak memory usage monitoring
- Garbage collection efficiency
- Long-running server stability
"""

import pytest
import asyncio
import gc
import sys
import tracemalloc
from pathlib import Path
from typing import Dict, List, Tuple
import psutil
import time

from wise_mise_mcp.server import (
    analyze_project_for_tasks,
    create_task,
    AnalyzeProjectRequest,
    CreateTaskRequest
)


class MemoryProfiler:
    """Context manager for memory profiling"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.process = psutil.Process()
        self.start_memory = 0
        self.peak_memory = 0
        self.end_memory = 0
        self.tracemalloc_snapshot = None
        
    def __enter__(self):
        gc.collect()  # Clean up before measurement
        self.start_memory = self.process.memory_info().rss
        tracemalloc.start()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        current_memory = self.process.memory_info().rss
        self.peak_memory = max(self.peak_memory, current_memory)
        
        # Take snapshot for detailed analysis
        self.tracemalloc_snapshot = tracemalloc.take_snapshot()
        tracemalloc.stop()
        
        gc.collect()
        self.end_memory = self.process.memory_info().rss
        
    @property
    def memory_increase_mb(self) -> float:
        """Memory increase in MB"""
        return (self.peak_memory - self.start_memory) / 1024 / 1024
        
    @property
    def memory_leaked_mb(self) -> float:
        """Memory potentially leaked in MB"""
        return (self.end_memory - self.start_memory) / 1024 / 1024
        
    def get_top_allocations(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top memory allocations from tracemalloc"""
        if not self.tracemalloc_snapshot:
            return []
            
        top_stats = self.tracemalloc_snapshot.statistics('lineno')
        return [(str(stat.traceback), stat.size) for stat in top_stats[:limit]]


class TestMemoryPerformance:
    """Memory performance and leak detection tests"""

    @pytest.mark.benchmark(group="memory")
    def test_memory_usage_small_project(self, benchmark, temp_project_dir):
        """Test memory usage for small project analysis"""
        
        # Create small test project
        for i in range(20):
            (temp_project_dir / f"file_{i}.py").write_text(f"# File {i}\nprint('Hello {i}')")
        (temp_project_dir / "package.json").write_text('{"name": "small-test"}')
        
        def memory_test():
            with MemoryProfiler("small_project") as profiler:
                async def analyze():
                    request = AnalyzeProjectRequest(project_path=str(temp_project_dir))
                    return await analyze_project_for_tasks(request)
                
                result = asyncio.run(analyze())
                
                # Track peak memory during operation
                profiler.peak_memory = max(
                    profiler.peak_memory, 
                    psutil.Process().memory_info().rss
                )
                
                return {
                    "result": result,
                    "memory_increase_mb": profiler.memory_increase_mb,
                    "memory_leaked_mb": profiler.memory_leaked_mb,
                    "top_allocations": profiler.get_top_allocations(5)
                }
        
        result = benchmark(memory_test)
        
        # Verify analysis succeeded
        assert "error" not in result["result"]
        
        # Memory usage should be reasonable for small project
        assert result["memory_increase_mb"] < 20  # Less than 20MB
        assert result["memory_leaked_mb"] < 2     # Less than 2MB leaked

    @pytest.mark.benchmark(group="memory")
    @pytest.mark.slow
    def test_memory_usage_large_project(self, benchmark, complex_project_structure):
        """Test memory usage for large project analysis"""
        
        # Add more files to make it truly large
        for i in range(500):
            (complex_project_structure / "generated" / f"file_{i}.py").mkdir(parents=True, exist_ok=True)
            (complex_project_structure / "generated" / f"file_{i}.py").write_text(
                f"# Generated file {i}\n" + "# " * 100 + f"\nclass Class{i}:\n    pass"
            )
        
        def memory_test_large():
            with MemoryProfiler("large_project") as profiler:
                async def analyze_large():
                    request = AnalyzeProjectRequest(project_path=str(complex_project_structure))
                    return await analyze_project_for_tasks(request)
                
                result = asyncio.run(analyze_large())
                
                return {
                    "result": result,
                    "memory_increase_mb": profiler.memory_increase_mb,
                    "memory_leaked_mb": profiler.memory_leaked_mb,
                    "file_count": result["project_structure"]["file_count"]
                }
        
        result = benchmark(memory_test_large)
        
        assert "error" not in result["result"]
        assert result["file_count"] > 500
        
        # Memory usage should scale reasonably with project size
        memory_per_file = result["memory_increase_mb"] / result["file_count"]
        assert memory_per_file < 0.5  # Less than 0.5MB per file
        assert result["memory_leaked_mb"] < 10  # Less than 10MB leaked total

    @pytest.mark.benchmark(group="memory")
    def test_memory_leak_detection(self, benchmark, temp_project_dir):
        """Test for memory leaks in repeated operations"""
        
        def setup_test_project():
            # Create test files
            for i in range(50):
                (temp_project_dir / f"test_{i}.py").write_text(f"# Test file {i}")
            (temp_project_dir / ".mise.toml").write_text("""
[tasks.test]
run = "pytest"
sources = ["**/*.py"]

[tasks.build] 
run = "python setup.py build"
depends = ["test"]
""")
        
        def memory_leak_test():
            setup_test_project()
            
            memory_readings = []
            
            # Perform the same operation multiple times
            for iteration in range(10):
                with MemoryProfiler(f"iteration_{iteration}") as profiler:
                    async def perform_operations():
                        # Mix of different operations
                        request1 = AnalyzeProjectRequest(project_path=str(temp_project_dir))
                        result1 = await analyze_project_for_tasks(request1)
                        
                        request2 = CreateTaskRequest(
                            project_path=str(temp_project_dir),
                            task_name=f"leak_test_{iteration}",
                            description=f"Leak test iteration {iteration}",
                            commands=[f"echo 'Iteration {iteration}'"]
                        )
                        result2 = await create_task(request2)
                        
                        return result1, result2
                    
                    results = asyncio.run(perform_operations())
                    
                    memory_readings.append({
                        "iteration": iteration,
                        "memory_increase_mb": profiler.memory_increase_mb,
                        "memory_leaked_mb": profiler.memory_leaked_mb
                    })
                    
                    # Force garbage collection between iterations
                    gc.collect()
            
            return {
                "memory_readings": memory_readings,
                "total_iterations": len(memory_readings),
                "average_increase": sum(r["memory_increase_mb"] for r in memory_readings) / len(memory_readings),
                "total_leaked": sum(r["memory_leaked_mb"] for r in memory_readings)
            }
        
        result = benchmark(memory_leak_test)
        
        # Check for memory leak patterns
        readings = result["memory_readings"]
        
        # Memory usage should be consistent across iterations
        memory_increases = [r["memory_increase_mb"] for r in readings]
        memory_variance = max(memory_increases) - min(memory_increases)
        assert memory_variance < 10  # Less than 10MB variance between iterations
        
        # Total leaked memory should be minimal
        assert result["total_leaked"] < 5  # Less than 5MB total leaked

    @pytest.mark.benchmark(group="memory")
    @pytest.mark.slow
    def test_long_running_memory_stability(self, benchmark, temp_project_dir):
        """Test memory stability over extended operation period"""
        
        def long_running_test():
            # Setup test environment
            for i in range(100):
                (temp_project_dir / f"file_{i}.py").write_text(f"# File {i}")
            
            memory_snapshots = []
            start_time = time.time()
            target_duration = 30  # Run for 30 seconds
            
            iteration = 0
            while time.time() - start_time < target_duration:
                with MemoryProfiler(f"long_run_{iteration}") as profiler:
                    async def operation():
                        request = AnalyzeProjectRequest(project_path=str(temp_project_dir))
                        return await analyze_project_for_tasks(request)
                    
                    result = asyncio.run(operation())
                    
                    memory_snapshots.append({
                        "iteration": iteration,
                        "timestamp": time.time() - start_time,
                        "memory_mb": psutil.Process().memory_info().rss / 1024 / 1024,
                        "memory_increase_mb": profiler.memory_increase_mb
                    })
                    
                    iteration += 1
                    
                    # Brief pause to avoid overwhelming the system
                    time.sleep(0.1)
            
            return {
                "snapshots": memory_snapshots,
                "total_iterations": iteration,
                "duration_seconds": time.time() - start_time,
                "final_memory_mb": memory_snapshots[-1]["memory_mb"],
                "initial_memory_mb": memory_snapshots[0]["memory_mb"]
            }
        
        result = benchmark(long_running_test)
        
        # Analyze memory stability
        snapshots = result["snapshots"]
        
        # Memory should not grow unboundedly
        memory_growth = result["final_memory_mb"] - result["initial_memory_mb"]
        assert memory_growth < 50  # Less than 50MB growth over 30 seconds
        
        # Check for memory growth trend
        mid_point = len(snapshots) // 2
        first_half_avg = sum(s["memory_mb"] for s in snapshots[:mid_point]) / mid_point
        second_half_avg = sum(s["memory_mb"] for s in snapshots[mid_point:]) / (len(snapshots) - mid_point)
        
        growth_rate = (second_half_avg - first_half_avg) / first_half_avg
        assert growth_rate < 0.2  # Less than 20% memory growth rate

    @pytest.mark.benchmark(group="memory") 
    def test_concurrent_memory_usage(self, benchmark, temp_project_dir):
        """Test memory usage under concurrent operations"""
        
        def concurrent_memory_test():
            # Setup test project
            for i in range(50):
                (temp_project_dir / f"concurrent_{i}.py").write_text(f"# Concurrent test {i}")
            
            with MemoryProfiler("concurrent_ops") as profiler:
                async def concurrent_operations():
                    # Create multiple concurrent operations
                    tasks = []
                    
                    for i in range(20):
                        request = AnalyzeProjectRequest(project_path=str(temp_project_dir))
                        task = analyze_project_for_tasks(request)
                        tasks.append(task)
                    
                    # Wait for all operations to complete
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    successful = sum(1 for r in results if not isinstance(r, Exception))
                    return {
                        "total_operations": len(tasks),
                        "successful_operations": successful,
                        "errors": [str(r) for r in results if isinstance(r, Exception)]
                    }
                
                operation_results = asyncio.run(concurrent_operations())
                
                return {
                    "operation_results": operation_results,
                    "memory_increase_mb": profiler.memory_increase_mb,
                    "memory_leaked_mb": profiler.memory_leaked_mb
                }
        
        result = benchmark(concurrent_memory_test)
        
        # All operations should succeed
        op_results = result["operation_results"]
        assert op_results["successful_operations"] == op_results["total_operations"]
        
        # Memory usage should be reasonable even with concurrency
        assert result["memory_increase_mb"] < 100  # Less than 100MB for 20 concurrent ops
        assert result["memory_leaked_mb"] < 5      # Less than 5MB leaked

    def test_memory_profiling_tools(self):
        """Test that memory profiling tools are working correctly"""
        
        with MemoryProfiler("test_profiler") as profiler:
            # Allocate some memory intentionally
            large_list = [i for i in range(100000)]
            
            # Memory increase should be detected
            current_memory = psutil.Process().memory_info().rss
            profiler.peak_memory = max(profiler.peak_memory, current_memory)
            
            # Clean up
            del large_list
        
        # Profiler should have recorded the memory usage
        assert profiler.memory_increase_mb > 0
        
        # Should have some allocation data
        allocations = profiler.get_top_allocations(3)
        assert len(allocations) > 0