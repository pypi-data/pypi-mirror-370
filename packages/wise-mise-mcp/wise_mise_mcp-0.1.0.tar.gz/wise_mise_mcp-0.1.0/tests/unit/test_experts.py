"""
Unit tests for wise_mise_mcp.experts module
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from wise_mise_mcp.experts import (
    BuildExpert, 
    TestExpert, 
    LintExpert, 
    DevExpert
)
from wise_mise_mcp.models import (
    TaskDomain, 
    ProjectStructure, 
    TaskRecommendation
)


class TestBuildExpert:
    """Test BuildExpert domain expert"""
    
    def test_domain_property(self):
        """Test domain property returns BUILD"""
        expert = BuildExpert()
        assert expert.domain == TaskDomain.BUILD
        
    def test_can_handle_task(self):
        """Test task handling capability detection"""
        expert = BuildExpert()
        
        # Should handle build-related tasks
        assert expert.can_handle_task("Build the project")
        assert expert.can_handle_task("Compile source code") 
        assert expert.can_handle_task("Bundle assets")
        assert expert.can_handle_task("Package application")
        assert expert.can_handle_task("Create distribution")
        
        # Should not handle non-build tasks
        assert not expert.can_handle_task("Run tests")
        assert not expert.can_handle_task("Start dev server")
        assert not expert.can_handle_task("Deploy to production")
        
    def test_analyze_npm_project(self):
        """Test analysis of npm-based project"""
        expert = BuildExpert()
        
        # Create mock project structure
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with build script
            package_json = {
                "name": "test-project",
                "scripts": {
                    "build": "webpack build",
                    "build:prod": "webpack build --mode=production"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                languages={"javascript"}
            )
            
            recommendations = expert.analyze_project(structure)
            
            assert len(recommendations) == 2  # build and build:prod
            
            # Check build task
            build_rec = next((r for r in recommendations if r.task.name == "build"), None)
            assert build_rec is not None
            assert build_rec.task.domain == TaskDomain.BUILD
            assert build_rec.task.run == "npm run build"
            assert "src/**/*" in build_rec.task.sources
            assert "package.json" in build_rec.task.sources
            assert any("dist/" in output or "build/" in output for output in build_rec.task.outputs)
            assert build_rec.priority == 9
            
            # Check production build task
            prod_rec = next((r for r in recommendations if r.task.name == "production"), None)
            assert prod_rec is not None
            assert prod_rec.task.run == "npm run build:prod"
            assert "lint" in prod_rec.task.depends
            assert "test:unit" in prod_rec.task.depends
            
    def test_analyze_rust_project(self):
        """Test analysis of Rust project"""
        expert = BuildExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers={"cargo"},
            languages={"rust"}
        )
        
        recommendations = expert.analyze_project(structure)
        
        assert len(recommendations) == 2  # debug and release builds
        
        # Check debug build
        debug_rec = next((r for r in recommendations if r.task.name == "debug"), None)
        assert debug_rec is not None
        assert debug_rec.task.run == "cargo build"
        assert "src/**/*.rs" in debug_rec.task.sources
        assert "Cargo.toml" in debug_rec.task.sources
        assert "target/debug/" in debug_rec.task.outputs
        assert debug_rec.task.alias == "bd"
        
        # Check release build
        release_rec = next((r for r in recommendations if r.task.name == "release"), None)
        assert release_rec is not None
        assert release_rec.task.run == "cargo build --release"
        assert "target/release/" in release_rec.task.outputs
        assert "lint" in release_rec.task.depends
        assert "test" in release_rec.task.depends
        
    def test_analyze_python_project(self):
        """Test analysis of Python project"""
        expert = BuildExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            (project_path / "pyproject.toml").touch()
            
            structure = ProjectStructure(
                root_path=project_path,
                languages={"python"}
            )
            
            recommendations = expert.analyze_project(structure)
            
            assert len(recommendations) == 1
            
            wheel_rec = recommendations[0]
            assert wheel_rec.task.name == "wheel"
            assert wheel_rec.task.run == "python -m build"
            assert "src/**/*.py" in wheel_rec.task.sources
            assert "pyproject.toml" in wheel_rec.task.sources
            assert "dist/" in wheel_rec.task.outputs
            
    def test_analyze_project_no_package_managers(self):
        """Test analysis of project with no recognized package managers"""
        expert = BuildExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers=set(),
            languages=set()
        )
        
        recommendations = expert.analyze_project(structure)
        assert len(recommendations) == 0


class TestTestExpert:
    """Test TestExpert domain expert"""
    
    def test_domain_property(self):
        """Test domain property returns TEST"""
        expert = TestExpert()
        assert expert.domain == TaskDomain.TEST
        
    def test_can_handle_task(self):
        """Test task handling capability detection"""
        expert = TestExpert()
        
        # Should handle test-related tasks
        assert expert.can_handle_task("Run unit tests")
        assert expert.can_handle_task("Execute test suite")
        assert expert.can_handle_task("Check code coverage")
        assert expert.can_handle_task("Run e2e tests")
        assert expert.can_handle_task("Integration testing")
        
        # Should not handle non-test tasks
        assert not expert.can_handle_task("Build project")
        assert not expert.can_handle_task("Lint code")
        assert not expert.can_handle_task("Deploy app")
        
    def test_analyze_project_no_tests(self):
        """Test analysis of project without tests"""
        expert = TestExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            has_tests=False
        )
        
        recommendations = expert.analyze_project(structure)
        assert len(recommendations) == 0
        
    def test_analyze_npm_jest_project(self):
        """Test analysis of npm project with Jest"""
        expert = TestExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with Jest
            package_json = {
                "name": "test-project",
                "scripts": {"test": "jest"},
                "devDependencies": {"jest": "^29.0.0"}
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                has_tests=True
            )
            
            recommendations = expert.analyze_project(structure)
            
            assert len(recommendations) == 2  # unit and watch tests
            
            # Check unit test
            unit_rec = next((r for r in recommendations if r.task.name == "unit"), None)
            assert unit_rec is not None
            assert unit_rec.task.run == "npm test"
            assert unit_rec.task.alias == "tu"
            assert "src/**/*" in unit_rec.task.sources
            
            # Check watch test
            watch_rec = next((r for r in recommendations if r.task.name == "watch"), None)
            assert watch_rec is not None
            assert watch_rec.task.run == "npm test -- --watch"
            assert watch_rec.task.alias == "tw"
            
    def test_analyze_npm_e2e_project(self):
        """Test analysis of npm project with E2E testing"""
        expert = TestExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with Playwright
            package_json = {
                "name": "test-project",
                "devDependencies": {
                    "jest": "^29.0.0",
                    "playwright": "^1.30.0"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                has_tests=True
            )
            
            recommendations = expert.analyze_project(structure)
            
            # Should have unit, watch, and e2e tests
            assert len(recommendations) == 3
            
            # Check e2e test
            e2e_rec = next((r for r in recommendations if r.task.name == "e2e"), None)
            assert e2e_rec is not None
            assert e2e_rec.task.run == "npx playwright test"
            assert "build" in e2e_rec.task.depends
            
    def test_analyze_rust_project(self):
        """Test analysis of Rust project"""
        expert = TestExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers={"cargo"},
            has_tests=True
        )
        
        recommendations = expert.analyze_project(structure)
        
        assert len(recommendations) == 2  # unit and coverage tests
        
        # Check unit test
        unit_rec = next((r for r in recommendations if r.task.name == "unit"), None)
        assert unit_rec is not None
        assert unit_rec.task.run == "cargo test"
        assert unit_rec.task.alias == "tu"
        
        # Check coverage test
        coverage_rec = next((r for r in recommendations if r.task.name == "coverage"), None)
        assert coverage_rec is not None
        assert coverage_rec.task.run == "cargo tarpaulin --out Html"
        assert "tarpaulin-report.html" in coverage_rec.task.outputs


class TestLintExpert:
    """Test LintExpert domain expert"""
    
    def test_domain_property(self):
        """Test domain property returns LINT"""
        expert = LintExpert()
        assert expert.domain == TaskDomain.LINT
        
    def test_can_handle_task(self):
        """Test task handling capability detection"""
        expert = LintExpert()
        
        # Should handle lint-related tasks
        assert expert.can_handle_task("Run linter")
        assert expert.can_handle_task("Format code")
        assert expert.can_handle_task("Check style")
        assert expert.can_handle_task("Quality check")
        assert expert.can_handle_task("Run clippy")
        assert expert.can_handle_task("ESLint check")
        
        # Should not handle non-lint tasks
        assert not expert.can_handle_task("Build project")
        assert not expert.can_handle_task("Run tests")
        assert not expert.can_handle_task("Start server")
        
    def test_analyze_npm_eslint_project(self):
        """Test analysis of npm project with ESLint"""
        expert = LintExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with ESLint and Prettier
            package_json = {
                "name": "test-project",
                "devDependencies": {
                    "eslint": "^8.0.0",
                    "prettier": "^2.0.0",
                    "typescript": "^4.0.0"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"}
            )
            
            recommendations = expert.analyze_project(structure)
            
            assert len(recommendations) == 3  # eslint, prettier, types
            
            # Check ESLint
            eslint_rec = next((r for r in recommendations if r.task.name == "eslint"), None)
            assert eslint_rec is not None
            assert eslint_rec.task.run == "npx eslint ."
            
            # Check Prettier
            prettier_rec = next((r for r in recommendations if r.task.name == "prettier"), None)
            assert prettier_rec is not None
            assert prettier_rec.task.run == "npx prettier --check ."
            
            # Check TypeScript
            types_rec = next((r for r in recommendations if r.task.name == "types"), None)
            assert types_rec is not None
            assert types_rec.task.run == "npx tsc --noEmit"
            
    def test_analyze_rust_project(self):
        """Test analysis of Rust project"""
        expert = LintExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers={"cargo"}
        )
        
        recommendations = expert.analyze_project(structure)
        
        assert len(recommendations) == 2  # clippy and fmt
        
        # Check Clippy
        clippy_rec = next((r for r in recommendations if r.task.name == "clippy"), None)
        assert clippy_rec is not None
        assert clippy_rec.task.run == "cargo clippy -- -D warnings"
        
        # Check fmt
        fmt_rec = next((r for r in recommendations if r.task.name == "fmt"), None)
        assert fmt_rec is not None
        assert fmt_rec.task.run == "cargo fmt --check"
        
    def test_analyze_python_project(self):
        """Test analysis of Python project"""
        expert = LintExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            languages={"python"}
        )
        
        recommendations = expert.analyze_project(structure)
        
        assert len(recommendations) == 2  # ruff and mypy
        
        # Check Ruff
        ruff_rec = next((r for r in recommendations if r.task.name == "ruff"), None)
        assert ruff_rec is not None
        assert ruff_rec.task.run == "ruff check ."
        
        # Check MyPy
        mypy_rec = next((r for r in recommendations if r.task.name == "mypy"), None)
        assert mypy_rec is not None
        assert mypy_rec.task.run == "mypy ."


class TestDevExpert:
    """Test DevExpert domain expert"""
    
    def test_domain_property(self):
        """Test domain property returns DEV"""
        expert = DevExpert()
        assert expert.domain == TaskDomain.DEV
        
    def test_can_handle_task(self):
        """Test task handling capability detection"""
        expert = DevExpert()
        
        # Should handle dev-related tasks
        assert expert.can_handle_task("Start dev server")
        assert expert.can_handle_task("Serve application")
        assert expert.can_handle_task("Watch for changes")
        assert expert.can_handle_task("Hot reload")
        
        # Should not handle non-dev tasks
        assert not expert.can_handle_task("Build project")
        assert not expert.can_handle_task("Run tests")
        assert not expert.can_handle_task("Deploy app")
        
    def test_analyze_npm_dev_project(self):
        """Test analysis of npm project with dev scripts"""
        expert = DevExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with dev script
            package_json = {
                "name": "test-project",
                "scripts": {
                    "dev": "webpack serve --mode=development",
                    "build": "webpack build"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                source_dirs=["src", "lib"]
            )
            
            recommendations = expert.analyze_project(structure)
            
            assert len(recommendations) == 2  # serve and watch
            
            # Check serve task
            serve_rec = next((r for r in recommendations if r.task.name == "serve"), None)
            assert serve_rec is not None
            assert serve_rec.task.run == "npm run dev"
            assert serve_rec.task.alias == "s"
            
            # Check watch task
            watch_rec = next((r for r in recommendations if r.task.name == "watch"), None)
            assert watch_rec is not None
            assert watch_rec.task.run == "mise watch build"
            
    def test_analyze_npm_start_project(self):
        """Test analysis of npm project with start script instead of dev"""
        expert = DevExpert()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create package.json with start script
            package_json = {
                "name": "test-project", 
                "scripts": {
                    "start": "node server.js",
                    "build": "webpack build"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                source_dirs=["src"]
            )
            
            recommendations = expert.analyze_project(structure)
            
            # Should still create serve task using start script
            serve_rec = next((r for r in recommendations if r.task.name == "serve"), None)
            assert serve_rec is not None
            assert serve_rec.task.run == "npm run start"
            
    def test_analyze_project_with_source_dirs(self):
        """Test analysis focusing on watch tasks for source directories"""
        expert = DevExpert()
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            source_dirs=["frontend/src", "backend/src", "shared"]
        )
        
        recommendations = expert.analyze_project(structure)
        
        # Should create watch task
        watch_rec = next((r for r in recommendations if r.task.name == "watch"), None)
        assert watch_rec is not None
        assert watch_rec.task.run == "mise watch build"
        assert watch_rec.task.sources == ["frontend/src", "backend/src", "shared"]


class TestDomainExpertIntegration:
    """Test integration between different domain experts"""
    
    def test_multiple_experts_same_project(self):
        """Test multiple experts analyzing the same complex project"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Create complex project structure
            package_json = {
                "name": "complex-project",
                "scripts": {
                    "build": "webpack build",
                    "test": "jest",
                    "dev": "webpack serve",
                    "lint": "eslint src"
                },
                "devDependencies": {
                    "webpack": "^5.0.0",
                    "jest": "^29.0.0", 
                    "eslint": "^8.0.0"
                }
            }
            
            with open(project_path / "package.json", "w") as f:
                json.dump(package_json, f)
                
            structure = ProjectStructure(
                root_path=project_path,
                package_managers={"npm"},
                languages={"javascript"},
                has_tests=True,
                source_dirs=["src"]
            )
            
            # Test all experts
            build_expert = BuildExpert()
            test_expert = TestExpert()
            lint_expert = LintExpert()
            dev_expert = DevExpert()
            
            build_recs = build_expert.analyze_project(structure)
            test_recs = test_expert.analyze_project(structure)
            lint_recs = lint_expert.analyze_project(structure)
            dev_recs = dev_expert.analyze_project(structure)
            
            # Each expert should provide recommendations
            assert len(build_recs) > 0
            assert len(test_recs) > 0
            assert len(lint_recs) > 0  
            assert len(dev_recs) > 0
            
            # Verify no overlap in task names within domain
            all_recs = build_recs + test_recs + lint_recs + dev_recs
            task_names = [rec.task.full_name for rec in all_recs]
            assert len(task_names) == len(set(task_names))  # All unique
            
    def test_expert_priority_consistency(self):
        """Test that experts assign consistent priority levels"""
        experts = [BuildExpert(), TestExpert(), LintExpert(), DevExpert()]
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers={"npm"},
            has_tests=True
        )
        
        for expert in experts:
            recommendations = expert.analyze_project(structure)
            
            for rec in recommendations:
                # Priority should be between 1 and 10
                assert 1 <= rec.priority <= 10
                # Should have valid effort estimation
                assert rec.estimated_effort in ["low", "medium", "high"]
                # Should have reasoning
                assert len(rec.reasoning) > 0
                
    def test_expert_task_complexity_assignment(self):
        """Test that experts assign appropriate task complexity"""
        from wise_mise_mcp.models import TaskComplexity
        
        experts = [BuildExpert(), TestExpert(), LintExpert(), DevExpert()]
        
        structure = ProjectStructure(
            root_path=Path("/test"),
            package_managers={"npm", "cargo"},
            languages={"javascript", "rust"},
            has_tests=True
        )
        
        for expert in experts:
            recommendations = expert.analyze_project(structure)
            
            for rec in recommendations:
                # All basic recommendations should be simple or moderate
                assert rec.task.complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE]