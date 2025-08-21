"""
FastMCP server for intelligent mise task management
"""

from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from .models import TaskDomain, TaskComplexity
from .analyzer import TaskAnalyzer
from .manager import TaskManager


# Request/Response models
class AnalyzeProjectRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")


class TraceTaskChainRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")
    task_name: str = Field(description="Name of the task to trace")


class CreateTaskRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")
    task_description: str = Field(description="Description of what the task should do")
    suggested_name: Optional[str] = Field(None, description="Suggested task name")
    force_complexity: Optional[str] = Field(
        None, description="Force complexity level (simple/moderate/complex)"
    )
    domain_hint: Optional[str] = Field(
        None, description="Hint about which domain this task belongs to"
    )


class ValidateArchitectureRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")


class PruneTasksRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")
    dry_run: bool = Field(True, description="Whether to only report what would be pruned")


class RemoveTaskRequest(BaseModel):
    project_path: str = Field(description="Path to the project directory")
    task_name: str = Field(description="Name of the task to remove")


# Initialize FastMCP
app = FastMCP("Mise Task Tools")


@app.tool()
async def analyze_project_for_tasks(request: AnalyzeProjectRequest) -> Dict[str, Any]:
    """
    Analyze a project structure and extract strategic task recommendations.

    This tool examines the project's package managers, languages, frameworks, and
    structure to recommend useful tasks organized by domain. It identifies what
    build systems, testing frameworks, and development tools are in use to suggest
    practical, actionable tasks.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        analyzer = TaskAnalyzer(project_path)

        # Analyze project structure
        structure = analyzer.analyze_project_structure()

        # Get task recommendations
        recommendations = analyzer.get_task_recommendations()

        # Get existing tasks for context
        existing_tasks = analyzer.extract_existing_tasks()

        return {
            "project_path": str(project_path),
            "project_structure": {
                "package_managers": list(structure.package_managers),
                "languages": list(structure.languages),
                "frameworks": list(structure.frameworks),
                "has_tests": structure.has_tests,
                "has_docs": structure.has_docs,
                "has_ci": structure.has_ci,
                "has_database": structure.has_database,
                "source_dirs": structure.source_dirs,
            },
            "existing_tasks": [
                {
                    "name": task.full_name,
                    "domain": task.domain.value,
                    "description": task.description,
                    "complexity": task.complexity.value,
                }
                for task in existing_tasks
            ],
            "recommendations": [
                {
                    "task_name": rec.task.full_name,
                    "domain": rec.task.domain.value,
                    "description": rec.task.description,
                    "reasoning": rec.reasoning,
                    "priority": rec.priority,
                    "estimated_effort": rec.estimated_effort,
                    "run_command": rec.task.run,
                    "sources": rec.task.sources,
                    "outputs": rec.task.outputs,
                    "complexity": rec.task.complexity.value,
                }
                for rec in recommendations
            ],
        }

    except Exception as e:
        return {"error": f"Failed to analyze project: {str(e)}"}


@app.tool()
async def trace_task_chain(request: TraceTaskChainRequest) -> Dict[str, Any]:
    """
    Trace the complete execution chain for a mise task.

    This tool analyzes task dependencies to show the full execution flow, including
    what tasks run before/after, parallel execution groups, and detailed information
    about each task in the chain. Useful for understanding complex task workflows
    and providing context to other agents.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        analyzer = TaskAnalyzer(project_path)
        return analyzer.trace_task_chain(request.task_name)

    except Exception as e:
        return {"error": f"Failed to trace task chain: {str(e)}"}


@app.tool()
async def create_task(request: CreateTaskRequest) -> Dict[str, Any]:
    """
    Intelligently create a new mise task with proper organization and placement.

    This tool analyzes the task description to determine the appropriate domain,
    complexity level, file vs TOML placement, dependencies, and integration with
    existing tasks. It automatically handles script creation, configuration updates,
    and documentation.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        manager = TaskManager(project_path)

        # Convert complexity string to enum if provided
        force_complexity = None
        if request.force_complexity:
            try:
                force_complexity = TaskComplexity(request.force_complexity.lower())
            except ValueError:
                return {"error": f"Invalid complexity: {request.force_complexity}"}

        result = manager.create_task_intelligently(
            task_description=request.task_description,
            suggested_name=request.suggested_name,
            force_complexity=force_complexity,
        )

        return result

    except Exception as e:
        return {"error": f"Failed to create task: {str(e)}"}


@app.tool()
async def validate_task_architecture(request: ValidateArchitectureRequest) -> Dict[str, Any]:
    """
    Validate that the mise task configuration follows best practices.

    This tool checks for circular dependencies, missing descriptions, proper domain
    organization, source/output tracking, and other architectural issues. It provides
    specific suggestions for improvements and identifies potential problems.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        analyzer = TaskAnalyzer(project_path)
        return analyzer.validate_task_architecture()

    except Exception as e:
        return {"error": f"Failed to validate architecture: {str(e)}"}


@app.tool()
async def prune_tasks(request: PruneTasksRequest) -> Dict[str, Any]:
    """
    Identify and optionally remove outdated or redundant tasks.

    This tool analyzes the task configuration to find tasks that might be redundant,
    unused, or outdated. It can either report what would be removed (dry_run=True)
    or actually remove the tasks (dry_run=False).
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        analyzer = TaskAnalyzer(project_path)
        redundant_tasks = analyzer.find_redundant_tasks()

        if request.dry_run:
            return {
                "dry_run": True,
                "redundant_tasks": redundant_tasks,
                "message": f"Found {len(redundant_tasks)} potentially redundant tasks",
            }

        # Actually remove redundant tasks
        manager = TaskManager(project_path)
        removed_tasks = []

        for redundant in redundant_tasks:
            if "task" in redundant:  # Single isolated task
                task_name = redundant["task"]
                result = manager.remove_task(task_name)
                if result.get("success"):
                    removed_tasks.append(task_name)

        return {
            "dry_run": False,
            "redundant_tasks_found": redundant_tasks,
            "removed_tasks": removed_tasks,
            "message": f"Removed {len(removed_tasks)} redundant tasks",
        }

    except Exception as e:
        return {"error": f"Failed to prune tasks: {str(e)}"}


@app.tool()
async def remove_task(request: RemoveTaskRequest) -> Dict[str, Any]:
    """
    Remove a specific task from the mise configuration.

    This tool removes a task from either the TOML configuration or deletes the
    file-based task script. It automatically updates documentation and handles
    cleanup.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        manager = TaskManager(project_path)
        return manager.remove_task(request.task_name)

    except Exception as e:
        return {"error": f"Failed to remove task: {str(e)}"}


@app.tool()
async def get_task_recommendations(request: AnalyzeProjectRequest) -> Dict[str, Any]:
    """
    Get strategic recommendations for improving task organization.

    This tool provides suggestions for new tasks, architectural improvements,
    better dependency organization, and optimization opportunities based on
    project analysis and current task setup.
    """
    try:
        project_path = Path(request.project_path)
        if not project_path.exists():
            return {"error": f"Project path {request.project_path} does not exist"}

        analyzer = TaskAnalyzer(project_path)

        # Get task recommendations
        recommendations = analyzer.get_task_recommendations()

        # Get architecture validation
        validation = analyzer.validate_task_architecture()

        # Get redundancy analysis
        redundant = analyzer.find_redundant_tasks()

        return {
            "project_path": str(project_path),
            "new_task_recommendations": [
                {
                    "task_name": rec.task.full_name,
                    "domain": rec.task.domain.value,
                    "description": rec.task.description,
                    "reasoning": rec.reasoning,
                    "priority": rec.priority,
                    "estimated_effort": rec.estimated_effort,
                }
                for rec in recommendations[:10]  # Top 10 recommendations
            ],
            "architecture_improvements": {
                "issues": validation.get("issues", []),
                "suggestions": validation.get("suggestions", []),
            },
            "redundancy_analysis": {"redundant_tasks": len(redundant), "details": redundant},
            "summary": {
                "total_existing_tasks": validation.get("total_tasks", 0),
                "domains_in_use": len(validation.get("domains_used", [])),
                "high_priority_recommendations": len(
                    [r for r in recommendations if r.priority >= 8]
                ),
            },
        }

    except Exception as e:
        return {"error": f"Failed to get recommendations: {str(e)}"}


@app.tool()
async def get_server_health() -> Dict[str, Any]:
    """
    Get comprehensive server health and diagnostics information.

    This tool provides detailed information about the server's health status,
    including dependency checks, system information, feature availability,
    and diagnostic data. Useful for troubleshooting and monitoring.
    """
    try:
        from datetime import datetime
        import sys
        import os
        from pathlib import Path
        
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "name": "Wise Mise MCP Server",
                "version": "0.1.0",
                "author": "Jarad DeLorenzo",
                "description": "Intelligent mise task management with domain expertise"
            },
            "system_info": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_directory": os.getcwd(),
                "python_path": sys.path[:3]  # First 3 entries
            },
            "dependencies": {},
            "features": {},
            "diagnostics": {}
        }
        
        # Check dependencies
        dependencies_to_check = [
            ("fastmcp", "FastMCP framework"),
            ("networkx", "Graph analysis"),
            ("pydantic", "Data validation"),
            ("tomli", "TOML parsing"),
            ("tomli_w", "TOML writing")
        ]
        
        for dep_name, description in dependencies_to_check:
            try:
                module = __import__(dep_name)
                version = getattr(module, '__version__', 'unknown')
                health["dependencies"][dep_name] = {
                    "status": "available",
                    "version": version,
                    "description": description
                }
            except ImportError as e:
                health["dependencies"][dep_name] = {
                    "status": "missing",
                    "error": str(e),
                    "description": description
                }
                health["status"] = "degraded"
        
        # Test core features
        try:
            from .models import TaskDomain, TaskComplexity, ProjectStructure
            domains = [domain.value for domain in TaskDomain]
            complexities = [complexity.value for complexity in TaskComplexity]
            
            health["features"]["task_system"] = {
                "status": "available",
                "domains": domains,
                "complexities": complexities,
                "domain_count": len(domains),
                "complexity_count": len(complexities)
            }
            
            # Test project analysis on current directory
            test_path = Path.cwd()
            structure = ProjectStructure.analyze(test_path)
            health["features"]["project_analysis"] = {
                "status": "available",
                "test_project": {
                    "path": str(test_path.absolute()),
                    "package_managers": list(structure.package_managers),
                    "languages": list(structure.languages),
                    "has_tests": structure.has_tests,
                    "has_docs": structure.has_docs,
                    "has_ci": structure.has_ci
                }
            }
            
        except Exception as e:
            health["features"]["core_functionality"] = {
                "status": "error", 
                "error": str(e)
            }
            health["status"] = "degraded"
        
        # Test expert system
        try:
            from .analyzer import TaskAnalyzer
            from .manager import TaskManager
            
            # Test analyzer
            analyzer = TaskAnalyzer(Path.cwd())
            existing_tasks = analyzer.extract_existing_tasks()
            
            health["features"]["expert_system"] = {
                "status": "available",
                "analyzer_available": True,
                "manager_available": True,
                "existing_tasks_count": len(existing_tasks),
                "expert_domains": len([domain.value for domain in TaskDomain])
            }
            
        except Exception as e:
            health["features"]["expert_system"] = {
                "status": "error",
                "error": str(e)
            }
            health["status"] = "degraded"
        
        # Diagnostic information
        try:
            # Check mise.toml in current directory
            mise_config = Path.cwd() / ".mise.toml"
            health["diagnostics"]["mise_config"] = {
                "exists": mise_config.exists(),
                "path": str(mise_config.absolute()),
                "readable": mise_config.exists() and mise_config.is_file()
            }
            
            # Check .mise directory
            mise_dir = Path.cwd() / ".mise"
            tasks_dir = mise_dir / "tasks"
            health["diagnostics"]["mise_directory"] = {
                "exists": mise_dir.exists(),
                "tasks_dir_exists": tasks_dir.exists(),
                "path": str(mise_dir.absolute())
            }
            
            # Available tools summary
            health["diagnostics"]["available_tools"] = [
                "analyze_project_for_tasks",
                "trace_task_chain", 
                "create_task",
                "validate_task_architecture",
                "prune_tasks",
                "remove_task",
                "get_task_recommendations",
                "get_mise_architecture_rules",
                "get_server_health"  # This tool
            ]
            
            # Available prompts summary
            health["diagnostics"]["available_prompts"] = [
                "mise_task_expert_guidance",
                "task_chain_analyst"
            ]
            
        except Exception as e:
            health["diagnostics"]["error"] = str(e)
        
        # Overall status assessment
        error_count = 0
        for category in [health["dependencies"], health["features"]]:
            for item in category.values():
                if isinstance(item, dict) and item.get("status") in ["missing", "error"]:
                    error_count += 1
        
        if error_count > 2:
            health["status"] = "unhealthy"
        elif error_count > 0:
            health["status"] = "degraded"
        
        health["summary"] = {
            "overall_status": health["status"],
            "dependencies_checked": len(health["dependencies"]),
            "features_tested": len(health["features"]),
            "diagnostics_collected": len(health["diagnostics"]),
            "error_count": error_count
        }
        
        return health
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


@app.tool()
async def get_mise_architecture_rules() -> Dict[str, Any]:
    """
    Get the comprehensive mise task architecture rules and best practices.

    This tool returns the complete set of rules, patterns, and conventions that
    guide intelligent task creation and organization. Useful for providing context
    to other agents about how tasks should be structured.
    """
    return {
        "domains": {
            "core_domains": [domain.value for domain in TaskDomain],
            "descriptions": {
                "build": "Compilation, bundling, asset processing",
                "test": "All testing variants (unit, integration, e2e)",
                "lint": "Code quality, formatting, static analysis",
                "dev": "Development workflow tasks",
                "deploy": "Deployment, release, infrastructure",
                "db": "Database operations, migrations, seeding",
                "ci": "CI/CD specific tasks",
                "docs": "Documentation generation, serving",
                "clean": "Cleanup operations",
                "setup": "Environment setup, installation",
            },
        },
        "naming_conventions": {
            "hierarchical_structure": "Use ':' as domain separator (e.g., test:unit, build:frontend)",
            "sub_domain_nesting": "Support multiple levels (e.g., test:integration:api)",
            "environment_variants": "Include environment in name (e.g., deploy:staging)",
            "tool_specific": "Include tool name when relevant (e.g., lint:eslint)",
        },
        "file_structure": {
            "root_config": "./.mise.toml",
            "task_directory": "./.mise/",
            "file_tasks": "./.mise/tasks/",
            "domain_subdirs": "./.mise/tasks/{domain}/",
            "local_overrides": "./.mise.local.toml",
        },
        "task_types": {
            "toml_tasks": "Simple, single-command tasks defined in .mise.toml",
            "file_tasks": "Complex multi-step operations as executable scripts",
            "complexity_guidelines": {
                "simple": "Single command, inline in TOML",
                "moderate": "Multiple commands, still in TOML",
                "complex": "Requires file task with script",
            },
        },
        "dependencies": {
            "depends": "Hard dependencies that must complete successfully",
            "depends_post": "Tasks that run after completion",
            "wait_for": "Optional dependencies that wait if running",
            "best_practices": [
                "Use wildcards for domain dependencies: depends = ['lint:*']",
                "Chain related tasks: ci depends on ['build', 'lint', 'test']",
                "Avoid circular dependencies",
                "Keep dependency chains shallow (max 3 levels)",
            ],
        },
        "performance": {
            "source_tracking": "Always specify sources for build-related tasks",
            "output_tracking": "Use outputs to enable incremental builds",
            "parallel_execution": "Design tasks to be parallelizable when possible",
            "glob_patterns": "Limit glob patterns to avoid excessive file scanning",
        },
    }


# Prompts for providing guidance
@app.prompt()
async def mise_task_expert_guidance() -> str:
    """
    Provides expert guidance on mise task architecture and best practices.

    Use this prompt to get comprehensive guidance on creating, organizing, and
    maintaining mise tasks according to the established architecture rules.
    """
    return """You are a mise task architecture expert. You help developers create, organize, and maintain mise tasks following these comprehensive rules:

## Core Principles
- Tasks are organized into 10 non-overlapping domains: build, test, lint, dev, deploy, db, ci, docs, clean, setup
- Use hierarchical naming with ':' separators (e.g., test:unit, build:frontend:assets)
- Simple tasks go in .mise.toml, complex tasks become executable scripts in .mise/tasks/
- Always include descriptions for public tasks
- Use source/output tracking for build and test tasks
- Design for parallel execution when possible

## Task Creation Decision Tree
1. **Domain Classification**: Which of the 10 domains does this task belong to?
2. **Complexity Assessment**: Simple (1 command), Moderate (2-5 commands), Complex (needs script)?
3. **Dependency Analysis**: What tasks must run before/after this one?
4. **Source/Output Tracking**: What files does this task read/write?
5. **Integration**: How does this fit with existing tasks?

## File Organization
- Root config: `./.mise.toml`
- Task scripts: `./.mise/tasks/{domain}/{task_name}`
- Local overrides: `./.mise.local.toml` (git-ignored)
- Documentation: `./.mise/docs/tasks.md`

## Common Patterns
- **Default tasks**: Each domain should have a default task that runs common operations
- **Watch variants**: Development tasks often benefit from watch modes
- **Environment variants**: deploy:staging, deploy:production
- **Tool-specific**: lint:eslint, lint:prettier, test:jest

When helping with task creation:
1. Always determine the appropriate domain first
2. Assess complexity to choose TOML vs file task
3. Suggest appropriate dependencies
4. Recommend source/output tracking
5. Ensure naming follows conventions
6. Consider integration with existing tasks

Provide specific, actionable advice and always explain the reasoning behind recommendations."""


@app.prompt()
async def task_chain_analyst() -> str:
    """
    Provides analysis and insights about mise task execution chains.

    Use this prompt when you need to understand or explain complex task dependencies
    and execution flows to other agents or developers.
    """
    return """You are a mise task chain analyst. You specialize in understanding and explaining complex task dependency graphs and execution flows.

## Analysis Capabilities
- Trace complete task execution chains from start to finish
- Identify parallel execution opportunities
- Detect circular dependencies and bottlenecks
- Explain the purpose and context of each task in a chain
- Recommend optimizations for task organization

## When Analyzing Task Chains
1. **Map the Full Flow**: Show all tasks that will execute when running a specific task
2. **Identify Parallel Groups**: Group tasks that can run simultaneously
3. **Explain Dependencies**: Why each dependency exists and what it provides
4. **Performance Impact**: How the chain affects total execution time
5. **Context for Other Agents**: What insights this provides about the project

## Key Insights to Provide
- **Execution Order**: The sequence tasks will run in
- **Critical Path**: The longest chain that determines minimum execution time
- **Bottlenecks**: Tasks that block parallel execution
- **Domain Distribution**: How tasks are organized across domains
- **Complexity Assessment**: Whether the chain is well-organized or overly complex

## For Other Agents
When providing context to coding agents or other tools, explain:
- What the task chain reveals about project structure
- Development workflow insights from the task organization
- Build and deployment patterns evident in the dependencies
- Testing strategy reflected in test task relationships
- Development tools and frameworks inferred from task names

Always provide both the technical details of the dependency graph and the higher-level insights about what this reveals about the project's architecture and development practices."""


def main():
    """Main entry point for the MCP server"""
    app.run()


if __name__ == "__main__":
    main()
