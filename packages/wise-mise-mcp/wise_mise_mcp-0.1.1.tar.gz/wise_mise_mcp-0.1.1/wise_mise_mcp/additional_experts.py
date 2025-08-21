"""
Additional domain experts for comprehensive task analysis
"""

from typing import List
import json

from .models import TaskDefinition, TaskDomain, TaskComplexity, ProjectStructure, TaskRecommendation
from .experts import DomainExpert


class DeployExpert(DomainExpert):
    """Expert for deployment and release tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.DEPLOY

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # Docker deployment
        if (structure.root_path / "Dockerfile").exists():
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="docker",
                        domain=TaskDomain.DEPLOY,
                        description="Build and deploy Docker container",
                        run="docker build -t $IMAGE_NAME . && docker push $IMAGE_NAME",
                        sources=["Dockerfile", "src/**/*"],
                        depends=["build", "test"],
                        complexity=TaskComplexity.MODERATE,
                    ),
                    reasoning="Dockerfile found - Docker deployment likely needed",
                    priority=7,
                    estimated_effort="medium",
                )
            )

        # Kubernetes deployment
        if (structure.root_path / "k8s").exists() or (structure.root_path / "kubernetes").exists():
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="k8s",
                        domain=TaskDomain.DEPLOY,
                        description="Deploy to Kubernetes",
                        run="kubectl apply -f k8s/",
                        sources=["k8s/**/*.yaml", "kubernetes/**/*.yaml"],
                        depends=["deploy:docker"],
                        complexity=TaskComplexity.COMPLEX,
                    ),
                    reasoning="Kubernetes manifests detected",
                    priority=6,
                    estimated_effort="high",
                )
            )

        # Cloud deployment (Vercel, Netlify, etc.)
        if "npm" in structure.package_managers:
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    scripts = data.get("scripts", {})

                    if "deploy" in scripts:
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="web",
                                    domain=TaskDomain.DEPLOY,
                                    description="Deploy web application",
                                    run="npm run deploy",
                                    depends=["build", "test"],
                                ),
                                reasoning="Deploy script found in package.json",
                                priority=8,
                                estimated_effort="low",
                            )
                        )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        deploy_keywords = ["deploy", "release", "ship", "publish", "docker", "k8s", "kubernetes"]
        return any(keyword in task_description.lower() for keyword in deploy_keywords)


class DbExpert(DomainExpert):
    """Expert for database-related tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.DB

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        if not structure.has_database:
            return recommendations

        # Database migrations
        migration_dirs = ["migrations", "migrate", "db/migrations"]
        if any((structure.root_path / mdir).exists() for mdir in migration_dirs):
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="migrate",
                        domain=TaskDomain.DB,
                        description="Run database migrations",
                        run="# Add migration command here",
                        complexity=TaskComplexity.MODERATE,
                    ),
                    reasoning="Migration directory found",
                    priority=8,
                    estimated_effort="medium",
                )
            )

        # Database seeding
        if (structure.root_path / "seeds").exists() or (structure.root_path / "db/seeds").exists():
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="seed",
                        domain=TaskDomain.DB,
                        description="Seed database with initial data",
                        run="# Add seed command here",
                        depends=["db:migrate"],
                    ),
                    reasoning="Seed directory found",
                    priority=6,
                    estimated_effort="low",
                )
            )

        # Database reset/setup
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="reset",
                    domain=TaskDomain.DB,
                    description="Reset database to clean state",
                    run="# Add reset commands here",
                    depends=["db:drop", "db:migrate", "db:seed"],
                    complexity=TaskComplexity.COMPLEX,
                ),
                reasoning="Database project should have reset capability",
                priority=7,
                estimated_effort="medium",
            )
        )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        db_keywords = ["database", "db", "migrate", "seed", "schema", "sql"]
        return any(keyword in task_description.lower() for keyword in db_keywords)


class CiExpert(DomainExpert):
    """Expert for CI/CD specific tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.CI

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        if not structure.has_ci:
            return recommendations

        # Main CI pipeline
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="check",
                    domain=TaskDomain.CI,
                    description="Run all CI checks",
                    run="# CI pipeline placeholder",
                    depends=["lint", "test", "build"],
                    alias="ci",
                ),
                reasoning="CI configuration detected",
                priority=9,
                estimated_effort="low",
            )
        )

        # Security scanning
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="security",
                    domain=TaskDomain.CI,
                    description="Run security scans",
                    run="# Add security scanning commands",
                    complexity=TaskComplexity.MODERATE,
                ),
                reasoning="Security scanning important for CI",
                priority=6,
                estimated_effort="medium",
            )
        )

        # Performance benchmarks
        if structure.has_tests:
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="benchmark",
                        domain=TaskDomain.CI,
                        description="Run performance benchmarks",
                        run="# Add benchmark commands",
                        depends=["build"],
                    ),
                    reasoning="Performance tracking valuable in CI",
                    priority=5,
                    estimated_effort="high",
                )
            )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        ci_keywords = ["ci", "pipeline", "continuous", "integration", "security", "benchmark"]
        return any(keyword in task_description.lower() for keyword in ci_keywords)


class DocsExpert(DomainExpert):
    """Expert for documentation tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.DOCS

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        if not structure.has_docs:
            return recommendations

        # Documentation generation
        if (structure.root_path / "docs").exists():
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="build",
                        domain=TaskDomain.DOCS,
                        description="Build documentation",
                        run="# Add docs build command",
                        sources=["docs/**/*", "README.md"],
                        outputs=["docs/build/", "site/"],
                    ),
                    reasoning="Documentation directory found",
                    priority=6,
                    estimated_effort="medium",
                )
            )

            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="serve",
                        domain=TaskDomain.DOCS,
                        description="Serve documentation locally",
                        run="# Add docs server command",
                        depends=["docs:build"],
                    ),
                    reasoning="Local docs serving useful for development",
                    priority=5,
                    estimated_effort="low",
                )
            )

        # API documentation
        if "npm" in structure.package_managers:
            package_json = structure.root_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if any(doc_tool in deps for doc_tool in ["jsdoc", "typedoc", "@storybook/cli"]):
                        recommendations.append(
                            TaskRecommendation(
                                task=TaskDefinition(
                                    name="api",
                                    domain=TaskDomain.DOCS,
                                    description="Generate API documentation",
                                    run="# Add API docs generation",
                                    sources=["src/**/*"],
                                ),
                                reasoning="Documentation tools detected",
                                priority=7,
                                estimated_effort="low",
                            )
                        )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        docs_keywords = ["docs", "documentation", "api", "readme", "guide", "manual"]
        return any(keyword in task_description.lower() for keyword in docs_keywords)


class CleanExpert(DomainExpert):
    """Expert for cleanup tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.CLEAN

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # Cache cleanup
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="cache",
                    domain=TaskDomain.CLEAN,
                    description="Clear build caches",
                    run="rm -rf .cache node_modules/.cache target/debug/.fingerprint",
                    hide=True,  # Internal task
                ),
                reasoning="Projects accumulate cache files",
                priority=7,
                estimated_effort="low",
            )
        )

        # Build artifacts cleanup
        build_outputs = ["dist/", "build/", "target/", "out/"]
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="build",
                    domain=TaskDomain.CLEAN,
                    description="Remove build artifacts",
                    run=f"rm -rf {' '.join(build_outputs)}",
                    alias="cb",
                ),
                reasoning="Build artifacts need periodic cleanup",
                priority=8,
                estimated_effort="low",
            )
        )

        # Dependencies cleanup
        if "npm" in structure.package_managers:
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="deps",
                        domain=TaskDomain.CLEAN,
                        description="Remove node_modules and reinstall",
                        run="rm -rf node_modules && npm install",
                        complexity=TaskComplexity.MODERATE,
                    ),
                    reasoning="Node.js projects benefit from clean dependency installs",
                    priority=6,
                    estimated_effort="medium",
                )
            )

        # All cleanup
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="all",
                    domain=TaskDomain.CLEAN,
                    description="Clean everything",
                    run="# Comprehensive cleanup",
                    depends=["clean:cache", "clean:build", "clean:deps"],
                    complexity=TaskComplexity.MODERATE,
                ),
                reasoning="Comprehensive cleanup task useful for troubleshooting",
                priority=5,
                estimated_effort="low",
            )
        )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        clean_keywords = ["clean", "clear", "remove", "delete", "reset", "purge"]
        return any(keyword in task_description.lower() for keyword in clean_keywords)


class SetupExpert(DomainExpert):
    """Expert for setup and installation tasks"""

    @property
    def domain(self) -> TaskDomain:
        return TaskDomain.SETUP

    def analyze_project(self, structure: ProjectStructure) -> List[TaskRecommendation]:
        recommendations = []

        # Development environment setup
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="dev",
                    domain=TaskDomain.SETUP,
                    description="Set up development environment",
                    run="mise install && mise run setup:deps",
                    complexity=TaskComplexity.COMPLEX,
                ),
                reasoning="Projects need development environment setup",
                priority=9,
                estimated_effort="medium",
            )
        )

        # Dependencies installation
        install_commands = []
        if "npm" in structure.package_managers:
            install_commands.append("npm install")
        if "cargo" in structure.package_managers:
            install_commands.append("cargo fetch")
        if "python" in structure.languages:
            install_commands.append("pip install -e .")

        if install_commands:
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="deps",
                        domain=TaskDomain.SETUP,
                        description="Install project dependencies",
                        run=install_commands[0] if len(install_commands) == 1 else install_commands,
                    ),
                    reasoning="Dependency installation is essential setup step",
                    priority=9,
                    estimated_effort="low",
                )
            )

        # Environment verification
        recommendations.append(
            TaskRecommendation(
                task=TaskDefinition(
                    name="verify",
                    domain=TaskDomain.SETUP,
                    description="Verify development environment",
                    run="# Add verification commands",
                    depends=["setup:deps"],
                    complexity=TaskComplexity.MODERATE,
                ),
                reasoning="Environment verification prevents setup issues",
                priority=7,
                estimated_effort="medium",
            )
        )

        # Git hooks setup
        if (structure.root_path / ".git").exists():
            recommendations.append(
                TaskRecommendation(
                    task=TaskDefinition(
                        name="hooks",
                        domain=TaskDomain.SETUP,
                        description="Install git hooks",
                        run="# Install pre-commit hooks",
                        complexity=TaskComplexity.MODERATE,
                    ),
                    reasoning="Git hooks improve code quality",
                    priority=6,
                    estimated_effort="low",
                )
            )

        return recommendations

    def can_handle_task(self, task_description: str) -> bool:
        setup_keywords = ["setup", "install", "configure", "init", "bootstrap", "prepare"]
        return any(keyword in task_description.lower() for keyword in setup_keywords)
