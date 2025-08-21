"""
Domain experts for analyzing projects and recommending tasks
"""

from abc import ABC, abstractmethod
from typing import List
import json

from .models import TaskDefinition, TaskDomain, TaskComplexity, ProjectStructure, TaskRecommendation


class DomainExpert(ABC):
    """Base class for domain-specific task experts"""

    @property
    @abstractmethod
    def domain(self) -> TaskDomain:
        """The domain this expert handles"""
        pass

    @abstractmethod
    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        """Analyze project structure and recommend tasks for this domain"""
        pass

    @abstractmethod
    def can_handle_task(self, task_description: str) -> bool:
        """Check if this expert can handle a given task description"""
        pass


class BuildExpert(DomainExpert):
    """Expert for build-related tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.BUILD

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # JavaScript/Node.js builds
        if "npm" in structure.package_managers:
            # Check package.json for build scripts
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    scripts = data.get("scripts", {})

                    if "build" in scripts:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="build",
                                    domain=TaskDomain.BUILD,
                                    description="Build the project",
                                    run="npm run build",
                                    sources=["src/**/*", "package.json"],
                                    outputs=["dist/", "build/"],
                                    alias="b",
                                ),
                                reasoning="Found npm build script in package.json",
                                priority=9,
                                estimated_effort="low",
                            )
                        )

                    if "build:prod" in scripts or "build:production" in scripts:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="production",
                                    domain=TaskDomain.BUILD,
                                    description="Build for production",
                                    run=(
                                        "npm run build:prod"
                                        if "build:prod" in scripts
                                        else "npm run build:production"
                                    ),
                                    sources=["src/**/*", "package.json"],
                                    outputs=["dist/", "build/"],
                                    depends=["lint", "test:unit"],
                                ),
                                reasoning="Found production build script",
                                priority=8,
                                estimated_effort="low",
                            )
                        )

        # Rust builds
        if "cargo" in structure.package_managers:
            recommendations.extend(
                [
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="debug",
                            domain=TaskDomain.BUILD,
                            description="Build debug version",
                            run="cargo build",
                            sources=["src/**/*.rs", "Cargo.toml"],
                            outputs=["target/debug/"],
                            alias="bd",
                        ),
                        reasoning="Rust project detected - debug builds are essential",
                        priority=9,
                        estimated_effort="low",
                    ),
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="release",
                            domain=TaskDomain.BUILD,
                            description="Build optimized release version",
                            run="cargo build --release",
                            sources=["src/**/*.rs", "Cargo.toml"],
                            outputs=["target/release/"],
                            depends=["lint", "test"],
                        ),
                        reasoning="Rust project needs optimized release builds",
                        priority=8,
                        estimated_effort="medium",
                    ),
                ]
            )

        # Python builds
        if "python" in structure.languages:
            if (structure.root_path / "pyproject.toml").exists():
                recommendations.append(
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="wheel",
                            domain=TaskDomain.BUILD,
                            description="Build Python wheel",
                            run="python -m build",
                            sources=["src/**/*.py", "pyproject.toml"],
                            outputs=["dist/"],
                        ),
                        reasoning="Python package with pyproject.toml should have wheel builds",
                        priority=7,
                        estimated_effort="low",
                    )
                )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        build_keywords = ["build", "compile", "bundle", "package", "artifact", "dist"]
        return any(keyword in task_description.lower() for keyword in build_keywords)


class TestExpert(DomainExpert):
    """Expert for testing-related tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.TEST

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        if not structure.has_tests:
            return recommendations

        # JavaScript testing
        if "npm" in structure.package_managers:
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    scripts = data.get("scripts", {})
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    # Jest tests
                    if "jest" in deps or "test" in scripts:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="unit",
                                    domain=TaskDomain.TEST,
                                    description="Run unit tests",
                                    run="npm test",
                                    sources=["src/**/*", "tests/**/*", "__tests__/**/*"],
                                    alias="tu",
                                ),
                                reasoning="Jest testing framework detected",
                                priority=9,
                                estimated_effort="low",
                            )
                        )

                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="watch",
                                    domain=TaskDomain.TEST,
                                    description="Run tests in watch mode",
                                    run="npm test -- --watch",
                                    sources=["src/**/*", "tests/**/*"],
                                    alias="tw",
                                ),
                                reasoning="Watch mode useful for TDD workflow",
                                priority=7,
                                estimated_effort="low",
                            )
                        )

                    # E2E tests
                    if any(e2e in deps for e2e in ["playwright", "cypress", "@playwright/test"]):
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="e2e",
                                    domain=TaskDomain.TEST,
                                    description="Run end-to-end tests",
                                    run=(
                                        "npx playwright test"
                                        if "playwright" in deps
                                        else "npx cypress run"
                                    ),
                                    depends=["build"],
                                    complexity=TaskComplexity.MODERATE,
                                ),
                                reasoning="E2E testing framework detected",
                                priority=8,
                                estimated_effort="medium",
                            )
                        )

        # Rust testing
        if "cargo" in structure.package_managers:
            recommendations.extend(
                [
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="unit",
                            domain=TaskDomain.TEST,
                            description="Run unit tests",
                            run="cargo test",
                            sources=["src/**/*.rs", "tests/**/*.rs"],
                            alias="tu",
                        ),
                        reasoning="Rust projects have built-in test framework",
                        priority=9,
                        estimated_effort="low",
                    ),
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="coverage",
                            domain=TaskDomain.TEST,
                            description="Run tests with coverage",
                            run="cargo tarpaulin --out Html",
                            sources=["src/**/*.rs", "tests/**/*.rs"],
                            outputs=["tarpaulin-report.html"],
                        ),
                        reasoning="Test coverage important for Rust projects",
                        priority=6,
                        estimated_effort="medium",
                    ),
                ]
            )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        test_keywords = ["test", "spec", "coverage", "e2e", "integration", "unit"]
        return any(keyword in task_description.lower() for keyword in test_keywords)


class LintExpert(DomainExpert):
    """Expert for linting and code quality tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.LINT

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # JavaScript linting
        if "npm" in structure.package_managers:
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if "eslint" in deps:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="eslint",
                                    domain=TaskDomain.LINT,
                                    description="Run ESLint",
                                    run="npx eslint .",
                                    sources=["src/**/*", ".eslintrc*"],
                                ),
                                reasoning="ESLint configuration detected",
                                priority=8,
                                estimated_effort="low",
                            )
                        )

                    if "prettier" in deps:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="prettier",
                                    domain=TaskDomain.LINT,
                                    description="Check code formatting",
                                    run="npx prettier --check .",
                                    sources=["src/**/*", ".prettierrc*"],
                                ),
                                reasoning="Prettier configuration detected",
                                priority=7,
                                estimated_effort="low",
                            )
                        )

                    if "typescript" in deps:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="types",
                                    domain=TaskDomain.LINT,
                                    description="Check TypeScript types",
                                    run="npx tsc --noEmit",
                                    sources=["src/**/*.ts", "tsconfig.json"],
                                ),
                                reasoning="TypeScript project needs type checking",
                                priority=9,
                                estimated_effort="low",
                            )
                        )

        # Rust linting
        if "cargo" in structure.package_managers:
            recommendations.extend(
                [
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="clippy",
                            domain=TaskDomain.LINT,
                            description="Run Clippy linter",
                            run="cargo clippy -- -D warnings",
                            sources=["src/**/*.rs", "Cargo.toml"],
                        ),
                        reasoning="Clippy is the standard Rust linter",
                        priority=9,
                        estimated_effort="low",
                    ),
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="fmt",
                            domain=TaskDomain.LINT,
                            description="Check code formatting",
                            run="cargo fmt --check",
                            sources=["src/**/*.rs"],
                        ),
                        reasoning="Rust formatting should be enforced",
                        priority=8,
                        estimated_effort="low",
                    ),
                ]
            )

        # Python linting
        if "python" in structure.languages:
            recommendations.extend(
                [
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="ruff",
                            domain=TaskDomain.LINT,
                            description="Run Ruff linter",
                            run="ruff check .",
                            sources=["src/**/*.py", "pyproject.toml"],
                        ),
                        reasoning="Ruff is fast modern Python linter",
                        priority=8,
                        estimated_effort="low",
                    ),
                    TaskRecommendation(
                        task=TaskDefinition(
                            name="mypy",
                            domain=TaskDomain.LINT,
                            description="Run type checking",
                            run="mypy .",
                            sources=["src/**/*.py", "pyproject.toml"],
                        ),
                        reasoning="Type checking improves Python code quality",
                        priority=7,
                        estimated_effort="medium",
                    ),
                ]
            )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        lint_keywords = ["lint", "format", "style", "check", "quality", "clippy", "eslint"]
        return any(keyword in task_description.lower() for keyword in lint_keywords)


class DevExpert(DomainExpert):
    """Expert for development workflow tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.DEV

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # Development server tasks
        if "npm" in structure.package_managers:
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    scripts = data.get("scripts", {})

                    if "dev" in scripts or "start" in scripts:
                        script_name = "dev" if "dev" in scripts else "start"
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="serve",
                                    domain=TaskDomain.DEV,
                                    description="Start development server",
                                    run=f"npm run {script_name}",
                                    alias="s",
                                ),
                                reasoning=f"Found {script_name} script for development server",
                                priority=9,
                                estimated_effort="low",
                            )
                        )

        # Watch tasks for various languages
        if structure.source_dirs:
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="watch",
                        domain=TaskDomain.DEV,
                        description="Watch for changes and rebuild",
                        run="mise watch build",
                        sources=structure.source_dirs,
                        complexity=TaskComplexity.MODERATE,
                    ),
                    reasoning="Watch mode useful for development workflow",
                    priority=7,
                    estimated_effort="low",
                )
            )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        dev_keywords = ["dev", "serve", "start", "watch", "hot", "reload"]
        return any(keyword in task_description.lower() for keyword in dev_keywords)
