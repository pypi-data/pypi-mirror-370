"""
Task creation and management utilities
"""

from typing import Dict, Optional, Any
from pathlib import Path
import os

from .models import (
    TaskDefinition,
    TaskDomain,
    TaskComplexity,
    MiseConfig,
)
from .analyzer import TaskAnalyzer


class TaskManager:
    """Manages creation, modification, and organization of mise tasks"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.mise_config_path = project_path / ".mise.toml"
        self.mise_dir = project_path / ".mise"
        self.tasks_dir = self.mise_dir / "tasks"
        self.analyzer = TaskAnalyzer(project_path)

    def ensure_structure(self) -> None:
        """Ensure proper mise directory structure exists"""
        self.mise_dir.mkdir(exist_ok=True)
        self.tasks_dir.mkdir(exist_ok=True)

        # Create domain subdirectories
        for domain in TaskDomain:
            domain_dir = self.tasks_dir / domain.value
            domain_dir.mkdir(exist_ok=True)

    def create_task_intelligently(
        self,
        task_description: str,
        suggested_name: Optional[str] = None,
        force_complexity: Optional[TaskComplexity] = None,
    ) -> Dict[str, Any]:
        """Intelligently create a task based on description"""

        # Find appropriate expert
        expert = self.analyzer.find_expert_for_task(task_description)
        if not expert:
            return {
                "error": "Could not determine appropriate domain for task",
                "suggestion": "Please specify domain explicitly",
            }

        domain = expert.domain

        # Determine task complexity
        complexity = force_complexity or self._determine_complexity(task_description)

        # Generate task name if not provided
        if not suggested_name:
            suggested_name = self._generate_task_name(task_description, domain)

        # Ensure name follows convention
        if ":" not in suggested_name:
            full_name = f"{domain.value}:{suggested_name}"
        else:
            full_name = suggested_name

        # Check if task already exists
        existing_tasks = self.analyzer.extract_existing_tasks()
        if any(task.full_name == full_name for task in existing_tasks):
            return {
                "error": f"Task '{full_name}' already exists",
                "existing_task": next(
                    task for task in existing_tasks if task.full_name == full_name
                ),
            }

        # Create task definition
        task_def = self._create_task_definition(full_name, domain, task_description, complexity)

        # Add task to configuration
        result = self._add_task_to_config(task_def)

        # Update documentation if successful
        if "error" not in result:
            self._update_task_documentation()

        return result

    def _determine_complexity(self, description: str) -> TaskComplexity:
        """Determine task complexity from description"""
        complex_indicators = [
            "multiple steps",
            "conditional",
            "if",
            "loop",
            "check",
            "validate",
            "complex",
            "script",
            "sequence",
        ]

        moderate_indicators = ["build and", "test and", "multiple", "several", "both"]

        desc_lower = description.lower()

        if any(indicator in desc_lower for indicator in complex_indicators):
            return TaskComplexity.COMPLEX
        elif any(indicator in desc_lower for indicator in moderate_indicators):
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE

    def _generate_task_name(self, description: str, domain: TaskDomain) -> str:
        """Generate a task name from description"""
        # Extract key words
        words = description.lower().split()

        # Remove common words
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "run",
            "execute",
            "start",
            "create",
        }

        key_words = [word for word in words if word not in stop_words and len(word) > 2]

        # Take first 2-3 meaningful words
        name_parts = key_words[:2] if len(key_words) >= 2 else key_words[:1]

        # Join with underscores and limit length
        name = "_".join(name_parts)[:20]

        return name or "task"

    def _create_task_definition(
        self, full_name: str, domain: TaskDomain, description: str, complexity: TaskComplexity
    ) -> TaskDefinition:
        """Create a task definition with intelligent defaults"""

        # Extract name without domain prefix
        if ":" in full_name:
            name = full_name.split(":", 1)[1]
        else:
            name = full_name

        # Generate basic run command based on domain and description
        run_command = self._generate_run_command(domain, description, name)

        # Determine sources and outputs based on domain
        sources, outputs = self._generate_sources_outputs(domain)

        task_def = TaskDefinition(
            name=full_name,
            domain=domain,
            description=description,
            run=run_command,
            sources=sources,
            outputs=outputs,
            complexity=complexity,
        )

        # For complex tasks, create as file task
        if complexity == TaskComplexity.COMPLEX:
            task_def.file_path = self._create_file_task(task_def)

        return task_def

    def _generate_run_command(self, domain: TaskDomain, description: str, name: str) -> str:
        """Generate appropriate run command based on domain and description"""
        desc_lower = description.lower()

        if domain == TaskDomain.BUILD:
            if "npm" in desc_lower or "node" in desc_lower:
                return "npm run build"
            elif "cargo" in desc_lower or "rust" in desc_lower:
                return "cargo build"
            elif "python" in desc_lower:
                return "python -m build"
            else:
                return "echo 'TODO: Add build command'"

        elif domain == TaskDomain.TEST:
            if "npm" in desc_lower or "jest" in desc_lower:
                return "npm test"
            elif "cargo" in desc_lower or "rust" in desc_lower:
                return "cargo test"
            elif "pytest" in desc_lower or "python" in desc_lower:
                return "pytest"
            else:
                return "echo 'TODO: Add test command'"

        elif domain == TaskDomain.LINT:
            if "eslint" in desc_lower:
                return "npx eslint ."
            elif "clippy" in desc_lower:
                return "cargo clippy"
            elif "ruff" in desc_lower:
                return "ruff check ."
            else:
                return "echo 'TODO: Add lint command'"

        elif domain == TaskDomain.DEV:
            if "serve" in desc_lower or "start" in desc_lower:
                return "npm run dev"
            elif "watch" in desc_lower:
                return "mise watch build"
            else:
                return "echo 'TODO: Add dev command'"

        else:
            return f"echo 'TODO: Implement {name} task'"

    def _generate_sources_outputs(self, domain: TaskDomain) -> tuple:
        """Generate appropriate sources and outputs based on domain"""

        # Analyze project to determine source patterns
        structure = self.analyzer.analyze_project_structure()
        sources = []
        outputs = []

        if domain in [TaskDomain.BUILD, TaskDomain.TEST, TaskDomain.LINT]:
            # Add common source patterns
            if structure.source_dirs:
                sources.extend([f"{src}/**/*" for src in structure.source_dirs])

            # Add config files
            if "npm" in structure.package_managers:
                sources.append("package.json")
            if "cargo" in structure.package_managers:
                sources.append("Cargo.toml")
            if "python" in structure.languages:
                sources.append("pyproject.toml")

        if domain == TaskDomain.BUILD:
            # Common build outputs
            outputs = ["dist/", "build/", "target/"]

        return sources, outputs

    def _create_file_task(self, task_def: TaskDefinition) -> Path:
        """Create a file-based task script"""
        self.ensure_structure()

        # Determine script location
        domain_dir = self.tasks_dir / task_def.domain.value
        script_name = task_def.name.split(":", 1)[1] if ":" in task_def.name else task_def.name
        script_path = domain_dir / script_name

        # Generate script content
        script_content = self._generate_script_content(task_def)

        # Write script
        with open(script_path, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(script_path, 0o755)

        return script_path

    def _generate_script_content(self, task_def: TaskDefinition) -> str:
        """Generate script content for file tasks"""
        content = f"""#!/usr/bin/env bash
#MISE description="{task_def.description}"
"""

        if task_def.sources:
            sources_str = '", "'.join(task_def.sources)
            content += f'#MISE sources=["{sources_str}"]\n'

        if task_def.outputs:
            outputs_str = '", "'.join(task_def.outputs)
            content += f'#MISE outputs=["{outputs_str}"]\n'

        if task_def.depends:
            depends_str = '", "'.join(task_def.depends)
            content += f'#MISE depends=["{depends_str}"]\n'

        content += f"""
set -euo pipefail

# TODO: Implement {task_def.name} task
echo "Running {task_def.name}: {task_def.description}"

# Add your implementation here
{task_def.run if isinstance(task_def.run, str) else chr(10).join(task_def.run)}

echo "✅ {task_def.name} completed successfully"
"""

        return content

    def _add_task_to_config(self, task_def: TaskDefinition) -> Dict[str, Any]:
        """Add task to mise configuration"""
        try:
            # Load current config
            config = MiseConfig.load_from_file(self.mise_config_path)

            # For file tasks, just ensure the file exists (mise auto-discovers)
            if task_def.is_file_task:
                return {
                    "success": True,
                    "task_name": task_def.full_name,
                    "type": "file_task",
                    "file_path": str(task_def.file_path),
                    "message": f"Created file task at {task_def.file_path}",
                }

            # For TOML tasks, add to configuration
            task_config = {}

            if task_def.description:
                task_config["description"] = task_def.description

            if isinstance(task_def.run, list) and len(task_def.run) == 1:
                task_config["run"] = task_def.run[0]
            else:
                task_config["run"] = task_def.run

            if task_def.depends:
                task_config["depends"] = task_def.depends

            if task_def.sources:
                task_config["sources"] = task_def.sources

            if task_def.outputs:
                task_config["outputs"] = task_def.outputs

            if task_def.env:
                task_config["env"] = task_def.env

            if task_def.alias:
                task_config["alias"] = task_def.alias

            if task_def.hide:
                task_config["hide"] = task_def.hide

            # Add to config
            config.tasks[task_def.full_name] = task_config

            # Save config
            config.save_to_file(self.mise_config_path)

            return {
                "success": True,
                "task_name": task_def.full_name,
                "type": "toml_task",
                "message": f"Added task '{task_def.full_name}' to .mise.toml",
            }

        except Exception as e:
            return {"error": f"Failed to add task: {str(e)}"}

    def remove_task(self, task_name: str) -> Dict[str, Any]:
        """Remove a task from configuration"""
        try:
            # Load current config
            config = MiseConfig.load_from_file(self.mise_config_path)

            # Check if task exists in TOML
            if task_name in config.tasks:
                del config.tasks[task_name]
                config.save_to_file(self.mise_config_path)
                return {"success": True, "message": f"Removed TOML task '{task_name}'"}

            # Check for file task
            task_file = self._find_task_file(task_name)
            if task_file and task_file.exists():
                task_file.unlink()
                return {
                    "success": True,
                    "message": f"Removed file task '{task_name}' at {task_file}",
                }

            return {"error": f"Task '{task_name}' not found"}

        except Exception as e:
            return {"error": f"Failed to remove task: {str(e)}"}

    def _find_task_file(self, task_name: str) -> Optional[Path]:
        """Find the file for a given task name"""
        # Extract domain and name
        if ":" in task_name:
            domain, name = task_name.split(":", 1)
        else:
            domain = "misc"
            name = task_name

        # Check in domain directory
        domain_dir = self.tasks_dir / domain
        if domain_dir.exists():
            potential_file = domain_dir / name
            if potential_file.exists():
                return potential_file

        # Check in root tasks directory
        potential_file = self.tasks_dir / name
        if potential_file.exists():
            return potential_file

        return None

    def _update_task_documentation(self) -> None:
        """Update task documentation after changes"""
        # This could generate markdown docs, update README, etc.
        # For now, just ensure the structure is documented

        docs_dir = self.mise_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        readme_path = docs_dir / "tasks.md"

        try:
            # Generate task documentation
            tasks = self.analyzer.extract_existing_tasks()

            content = "# Project Tasks\n\n"
            content += "This document lists all available mise tasks for this project.\n\n"

            # Group by domain
            by_domain = {}
            for task in tasks:
                domain = task.domain.value
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(task)

            for domain, domain_tasks in sorted(by_domain.items()):
                content += f"## {domain.title()} Tasks\n\n"

                for task in sorted(domain_tasks, key=lambda t: t.full_name):
                    content += f"### `{task.full_name}`\n\n"
                    if task.description:
                        content += f"{task.description}\n\n"

                    if task.alias:
                        content += f"**Alias:** `{task.alias}`\n\n"

                    if task.depends:
                        content += f"**Dependencies:** {', '.join(task.depends)}\n\n"

                    content += f"**Usage:** `mise run {task.full_name}`\n\n"

            with open(readme_path, "w") as f:
                f.write(content)
        except Exception:
            # Don't fail if documentation update fails
            pass
