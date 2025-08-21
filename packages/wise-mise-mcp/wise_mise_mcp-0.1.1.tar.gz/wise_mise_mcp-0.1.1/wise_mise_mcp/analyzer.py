"""
Task analysis and management utilities
"""

from typing import Dict, List, Optional
from pathlib import Path
import networkx as nx
from collections import defaultdict

from .models import TaskDefinition, TaskDomain, MiseConfig, ProjectStructure, TaskRecommendation
from .experts import DomainExpert, BuildExpert, TestExpert, LintExpert, DevExpert
from .additional_experts import (
    DeployExpert,
    DbExpert,
    CiExpert,
    DocsExpert,
    CleanExpert,
    SetupExpert,
)


class TaskAnalyzer:
    """Analyzes mise task configurations and dependencies"""

    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.mise_config = MiseConfig.load_from_file(project_path / ".mise.toml")
        self.experts: List[DomainExpert] = [
            BuildExpert(),
            TestExpert(),
            LintExpert(),
            DevExpert(),
            DeployExpert(),
            DbExpert(),
            CiExpert(),
            DocsExpert(),
            CleanExpert(),
            SetupExpert(),
        ]

    def analyze_project_structure(self) -> ProjectStructure:
        """Analyze the project structure for task recommendations"""
        return ProjectStructure.analyze(self.project_path)

    def extract_existing_tasks(self) -> List[TaskDefinition]:
        """Extract all existing tasks from mise configuration"""
        tasks = []

        for task_name, task_config in self.mise_config.tasks.items():
            # Handle different task configuration formats
            if isinstance(task_config, str):
                run = task_config
                config = {}
            elif isinstance(task_config, list):
                run = task_config
                config = {}
            else:
                run = task_config.get("run", "")
                config = task_config

            # Determine domain from task name
            domain = self._extract_domain_from_name(task_name)

            task = TaskDefinition(
                name=task_name,
                domain=domain,
                description=config.get("description", ""),
                run=run,
                depends=config.get("depends", []),
                depends_post=config.get("depends_post", []),
                wait_for=config.get("wait_for", []),
                sources=config.get("sources", []),
                outputs=config.get("outputs", []),
                env=config.get("env", {}),
                dir=config.get("dir"),
                alias=config.get("alias"),
                hide=config.get("hide", False),
                confirm=config.get("confirm"),
            )
            tasks.append(task)

        return tasks

    def _extract_domain_from_name(self, task_name: str) -> TaskDomain:
        """Extract domain from task name using heuristics"""
        if ":" in task_name:
            domain_name = task_name.split(":")[0]
            try:
                return TaskDomain(domain_name)
            except ValueError:
                pass

        # Fallback to keyword matching
        for domain in TaskDomain:
            if domain.value in task_name.lower():
                return domain

        # Default to BUILD if unclear
        return TaskDomain.BUILD

    def build_dependency_graph(self, tasks: List[TaskDefinition]) -> nx.DiGraph:
        """Build a directed graph of task dependencies"""
        graph = nx.DiGraph()

        # Add all tasks as nodes
        for task in tasks:
            graph.add_node(task.full_name, task=task)

        # Add dependency edges
        for task in tasks:
            for dep in task.depends:
                if graph.has_node(dep):
                    graph.add_edge(dep, task.full_name, type="depends")

            for dep in task.depends_post:
                if graph.has_node(dep):
                    graph.add_edge(task.full_name, dep, type="depends_post")

            for dep in task.wait_for:
                if graph.has_node(dep):
                    graph.add_edge(dep, task.full_name, type="wait_for")

        return graph

    def trace_task_chain(self, task_name: str) -> Dict[str, any]:
        """Trace the full execution chain for a task"""
        tasks = self.extract_existing_tasks()
        graph = self.build_dependency_graph(tasks)

        if task_name not in graph:
            return {"error": f"Task '{task_name}' not found"}

        # Find all predecessors (dependencies)
        predecessors = list(nx.ancestors(graph, task_name))

        # Find all successors (what depends on this)
        successors = list(nx.descendants(graph, task_name))

        # Build execution order using topological sort
        subgraph = graph.subgraph([task_name] + predecessors)
        execution_order = list(nx.topological_sort(subgraph))

        # Get task details
        task_details = {}
        for node in execution_order + successors:
            task = graph.nodes[node]["task"]
            task_details[node] = {
                "description": task.description,
                "run": task.run,
                "domain": task.domain.value,
                "sources": task.sources,
                "outputs": task.outputs,
                "complexity": task.complexity.value,
            }

        return {
            "task_name": task_name,
            "execution_order": execution_order,
            "dependencies": predecessors,
            "dependents": successors,
            "task_details": task_details,
            "parallelizable_groups": self._find_parallel_groups(subgraph),
        }

    def _find_parallel_groups(self, graph: nx.DiGraph) -> List[List[str]]:
        """Find groups of tasks that can run in parallel"""
        levels = []
        remaining = set(graph.nodes())

        while remaining:
            # Find nodes with no dependencies among remaining nodes
            current_level = []
            for node in remaining:
                deps = set(graph.predecessors(node))
                if not (deps & remaining):  # No remaining dependencies
                    current_level.append(node)

            if not current_level:
                break  # Circular dependency

            levels.append(current_level)
            remaining -= set(current_level)

        return levels

    def get_task_recommendations(self) -> List[TaskRecommendation]:
        """Get recommendations for new tasks based on project analysis"""
        structure = self.analyze_project_structure()
        existing_tasks = {task.full_name for task in self.extract_existing_tasks()}

        all_recommendations = []

        for expert in self.experts:
            recommendations = expert.analyze_project(structure)
            # Filter out tasks that already exist
            new_recommendations = [
                rec for rec in recommendations if rec.task.full_name not in existing_tasks
            ]
            all_recommendations.extend(new_recommendations)

        # Sort by priority
        all_recommendations.sort(key=lambda x: x.priority, reverse=True)

        return all_recommendations

    def find_expert_for_task(self, task_description: str) -> Optional[DomainExpert]:
        """Find the best expert to handle a task description"""
        for expert in self.experts:
            if expert.can_handle_task(task_description):
                return expert
        return None

    def validate_task_architecture(self) -> Dict[str, any]:
        """Validate that the current task setup follows best practices"""
        tasks = self.extract_existing_tasks()
        graph = self.build_dependency_graph(tasks)

        issues = []
        suggestions = []

        # Check for circular dependencies
        try:
            nx.find_cycle(graph)
            issues.append("Circular dependencies detected in task graph")
        except nx.NetworkXNoCycle:
            pass

        # Check for orphaned tasks (no dependencies, no dependents)
        orphaned = [
            node
            for node in graph.nodes()
            if graph.in_degree(node) == 0
            and graph.out_degree(node) == 0
            and not graph.nodes[node]["task"].alias  # Skip tasks with aliases
        ]
        if orphaned:
            suggestions.append(f"Consider connecting orphaned tasks: {orphaned}")

        # Check for missing descriptions
        no_description = [
            task.full_name for task in tasks if not task.description and not task.hide
        ]
        if no_description:
            issues.append(f"Tasks missing descriptions: {no_description}")

        # Check domain distribution
        domain_counts = defaultdict(int)
        for task in tasks:
            domain_counts[task.domain] += 1

        if len(domain_counts) < 3:
            suggestions.append("Consider organizing tasks into more domains for better structure")

        # Check for tasks that could benefit from source/output tracking
        no_sources = [
            task.full_name
            for task in tasks
            if task.domain in [TaskDomain.BUILD, TaskDomain.TEST] and not task.sources
        ]
        if no_sources:
            suggestions.append(f"Consider adding source tracking to: {no_sources}")

        return {
            "total_tasks": len(tasks),
            "domains_used": list(domain_counts.keys()),
            "domain_distribution": dict(domain_counts),
            "has_cycles": bool(issues and "Circular" in issues[0]),
            "issues": issues,
            "suggestions": suggestions,
            "orphaned_tasks": orphaned,
        }

    def find_redundant_tasks(self) -> List[Dict[str, any]]:
        """Find tasks that might be redundant or outdated"""
        tasks = self.extract_existing_tasks()
        redundant = []

        # Group tasks by domain
        domain_tasks = defaultdict(list)
        for task in tasks:
            domain_tasks[task.domain].append(task)

        # Look for similar tasks within domains
        for domain, domain_task_list in domain_tasks.items():
            for i, task1 in enumerate(domain_task_list):
                for task2 in domain_task_list[i + 1 :]:
                    similarity = self._calculate_task_similarity(task1, task2)
                    if similarity > 0.8:  # Very similar tasks
                        redundant.append(
                            {
                                "task1": task1.full_name,
                                "task2": task2.full_name,
                                "similarity": similarity,
                                "reason": "Very similar task definitions",
                                "suggestion": "Consider merging or removing one",
                            }
                        )

        # Look for tasks with no dependencies and no dependents
        graph = self.build_dependency_graph(tasks)
        for task in tasks:
            if (
                graph.in_degree(task.full_name) == 0
                and graph.out_degree(task.full_name) == 0
                and not task.alias
                and task.full_name != "default"
            ):
                redundant.append(
                    {
                        "task": task.full_name,
                        "reason": "Isolated task with no connections",
                        "suggestion": "Consider adding dependencies or removing if unused",
                    }
                )

        return redundant

    def _calculate_task_similarity(self, task1: TaskDefinition, task2: TaskDefinition) -> float:
        """Calculate similarity score between two tasks"""
        score = 0.0

        # Compare run commands
        if isinstance(task1.run, str) and isinstance(task2.run, str):
            if task1.run == task2.run:
                score += 0.5
        elif task1.run == task2.run:  # Lists
            score += 0.5

        # Compare sources
        if set(task1.sources) == set(task2.sources) and task1.sources:
            score += 0.2

        # Compare outputs
        if set(task1.outputs) == set(task2.outputs) and task1.outputs:
            score += 0.2

        # Compare dependencies
        if set(task1.depends) == set(task2.depends) and task1.depends:
            score += 0.1

        return score
