"""
Custom pytest plugin for performance testing and benchmarking.

Provides performance markers, fixtures, and reporting functionality.
"""

import pytest
import time
import psutil
import functools
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import json


class PerformanceCollector:
    """Collects performance metrics during test runs"""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
        self.start_memory = None
        self.process = psutil.Process()
    
    def start_collection(self, test_name: str):
        """Start collecting metrics for a test"""
        self.start_time = time.time()
        self.start_memory = self.process.memory_info().rss
        
        self.metrics[test_name] = {
            "start_time": self.start_time,
            "start_memory_mb": self.start_memory / 1024 / 1024,
        }
    
    def end_collection(self, test_name: str):
        """End collecting metrics for a test"""
        if test_name not in self.metrics:
            return
            
        end_time = time.time()
        end_memory = self.process.memory_info().rss
        
        self.metrics[test_name].update({
            "end_time": end_time,
            "duration_ms": (end_time - self.start_time) * 1000,
            "end_memory_mb": end_memory / 1024 / 1024,
            "memory_delta_mb": (end_memory - self.start_memory) / 1024 / 1024,
        })
    
    def add_metric(self, test_name: str, metric_name: str, value: Any):
        """Add a custom metric for a test"""
        if test_name not in self.metrics:
            self.metrics[test_name] = {}
        self.metrics[test_name][metric_name] = value
    
    def get_metrics(self, test_name: str) -> Dict[str, Any]:
        """Get metrics for a specific test"""
        return self.metrics.get(test_name, {})
    
    def save_metrics(self, output_path: Path):
        """Save collected metrics to file"""
        with open(output_path, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)


# Global performance collector
performance_collector = PerformanceCollector()


@pytest.fixture(scope="session")
def perf_collector():
    """Fixture to provide access to performance collector"""
    return performance_collector


def performance_test(threshold_ms: Optional[float] = None, 
                    memory_threshold_mb: Optional[float] = None):
    """Decorator to mark tests as performance tests with thresholds"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            test_name = func.__name__
            
            performance_collector.start_collection(test_name)
            
            try:
                result = func(*args, **kwargs)
            finally:
                performance_collector.end_collection(test_name)
                
                # Check thresholds
                metrics = performance_collector.get_metrics(test_name)
                
                if threshold_ms and metrics.get("duration_ms", 0) > threshold_ms:
                    pytest.fail(
                        f"Performance test {test_name} exceeded time threshold: "
                        f"{metrics['duration_ms']:.1f}ms > {threshold_ms}ms"
                    )
                
                if memory_threshold_mb and metrics.get("memory_delta_mb", 0) > memory_threshold_mb:
                    pytest.fail(
                        f"Performance test {test_name} exceeded memory threshold: "
                        f"{metrics['memory_delta_mb']:.1f}MB > {memory_threshold_mb}MB"
                    )
            
            return result
            
        # Mark as performance test
        wrapper = pytest.mark.performance(wrapper)
        return wrapper
    
    return decorator


class PerformancePlugin:
    """pytest plugin for performance testing"""
    
    def __init__(self):
        self.session_start_time = None
        self.performance_report = {}
    
    @pytest.hookimpl(tryfirst=True)
    def pytest_sessionstart(self, session):
        """Called after the Session object has been created"""
        self.session_start_time = time.time()
        
        # Initialize performance tracking
        session.perf_collector = performance_collector
        
        # Add performance markers
        session.config.addinivalue_line(
            "markers", 
            "performance: marks tests as performance tests"
        )
        session.config.addinivalue_line(
            "markers",
            "benchmark: marks tests as benchmark tests" 
        )
        session.config.addinivalue_line(
            "markers",
            "slow: marks tests as slow running tests"
        )
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        """Hook to wrap test execution with performance monitoring"""
        
        # Check if this is a performance test
        is_performance_test = any(
            marker.name in ["performance", "benchmark", "slow"] 
            for marker in item.iter_markers()
        )
        
        if is_performance_test:
            test_name = item.nodeid
            performance_collector.start_collection(test_name)
        
        # Run the test
        outcome = yield
        
        if is_performance_test:
            performance_collector.end_collection(test_name)
            
            # Store performance results
            metrics = performance_collector.get_metrics(test_name)
            self.performance_report[test_name] = metrics
    
    def pytest_sessionfinish(self, session, exitstatus):
        """Called after whole test run finished"""
        
        session_duration = time.time() - self.session_start_time
        
        # Save performance report
        report_path = Path("tests/performance_report.json")
        report_path.parent.mkdir(exist_ok=True)
        
        full_report = {
            "session": {
                "duration_seconds": session_duration,
                "exit_status": exitstatus,
                "timestamp": time.time()
            },
            "tests": self.performance_report,
            "summary": self._generate_summary()
        }
        
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2, default=str)
        
        # Print performance summary
        if self.performance_report:
            self._print_performance_summary()
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate performance summary statistics"""
        if not self.performance_report:
            return {}
        
        durations = [
            metrics.get("duration_ms", 0) 
            for metrics in self.performance_report.values()
        ]
        
        memory_usage = [
            metrics.get("memory_delta_mb", 0)
            for metrics in self.performance_report.values()
        ]
        
        return {
            "total_performance_tests": len(self.performance_report),
            "average_duration_ms": sum(durations) / len(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "total_memory_usage_mb": sum(memory_usage),
            "max_memory_usage_mb": max(memory_usage) if memory_usage else 0,
        }
    
    def _print_performance_summary(self):
        """Print performance test summary to console"""
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        summary = self._generate_summary()
        
        print(f"Total Performance Tests: {summary['total_performance_tests']}")
        print(f"Average Duration: {summary['average_duration_ms']:.1f}ms")
        print(f"Slowest Test: {summary['max_duration_ms']:.1f}ms")
        print(f"Total Memory Usage: {summary['total_memory_usage_mb']:.1f}MB")
        print(f"Peak Memory Usage: {summary['max_memory_usage_mb']:.1f}MB")
        
        # Show slowest tests
        slowest_tests = sorted(
            self.performance_report.items(),
            key=lambda x: x[1].get("duration_ms", 0),
            reverse=True
        )[:5]
        
        if slowest_tests:
            print("\nSlowest Tests:")
            for test_name, metrics in slowest_tests:
                duration = metrics.get("duration_ms", 0)
                memory = metrics.get("memory_delta_mb", 0)
                print(f"  {test_name}: {duration:.1f}ms ({memory:.1f}MB)")
        
        print("=" * 60)


def pytest_configure(config):
    """Register the performance plugin"""
    if not hasattr(config, 'performance_plugin'):
        config.performance_plugin = PerformancePlugin()
        config.pluginmanager.register(config.performance_plugin)