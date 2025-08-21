# 🎯 Wise Mise MCP

> **The intelligent MCP server that transforms mise task management with AI-powered analysis and domain expertise**

[![PyPI version](https://badge.fury.io/py/wise-mise-mcp.svg)](https://badge.fury.io/py/wise-mise-mcp)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://wise-mise-mcp.readthedocs.io)

**Stop wrestling with mise configuration.** Wise Mise MCP brings enterprise-grade intelligence to your [mise](https://mise.jdx.dev/) workflow, automatically analyzing your project structure and creating perfectly organized, maintainable task architectures that scale with your development needs.

## Why Wise Mise MCP?

**🧠 Intelligent Task Analysis**

- Automatically analyzes your project structure to extract meaningful tasks
- Understands 10+ technology domains (build, test, lint, deploy, CI/CD, etc.)
- Suggests optimal task organization and dependency patterns

**🏗️ Architecture-Aware**

- Follows mise best practices with hierarchical task organization
- Supports complex dependency graphs with source/output tracking
- Optimizes for incremental builds and performance

**🔧 Developer Experience**

- Integrates seamlessly with any MCP-compatible client
- Provides detailed explanations and recommendations
- Reduces cognitive load of task management

## Quick Start

### Using UVX (Recommended)

```bash
# Just run this to start Wise Mise MCP with UVX
uvx wise-mise-mcp

# Or install globally
uv tool install wise-mise-mcp
```

### Traditional pip

```bash
pip install wise-mise-mcp
```

### Add to Your MCP Client

Add to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "wise-mise-mcp": {
      "command": "uvx",
      "args": ["wise_mise_mcp"]
    }
  }
}
```

## What Makes It "Wise"?

Wise Mise MCP goes beyond simple task creation. It brings intelligence to your mise configuration:

### 🔍 Project Analysis

```python
# Analyzes your entire project structure
analyze_project_for_tasks("/path/to/project")
# Returns strategically organized tasks based on your tech stack
```

### 🕸️ Dependency Mapping

```python
# Traces complex task relationships
trace_task_chain("/path/to/project", "build:prod")
# Visualizes the complete execution flow
```

### ⚡ Smart Task Creation

```python
# Intelligently places tasks in the right domain
create_task(
    project_path="/path/to/project",
    task_description="Run TypeScript type checking",
    # Automatically suggests: lint:types with proper dependencies
)
```

## Core Features

### 🎯 **Domain Experts**

- **Build**: Frontend/Backend build systems, bundlers, compilers
- **Test**: Unit, integration, e2e testing strategies
- **Lint**: Code quality, formatting, static analysis
- **Deploy**: CI/CD, containerization, release management
- **Database**: Migrations, seeding, schema management
- **Development**: Local dev servers, hot reloading, debugging

### 📊 **Intelligent Analysis**

- **Complexity Assessment**: Automatically categorizes tasks as Simple, Moderate, or Complex
- **Dependency Detection**: Identifies natural task relationships
- **Source/Output Tracking**: Optimizes incremental builds
- **Redundancy Elimination**: Finds and removes duplicate tasks

### 🔧 **MCP Tools**

| Tool                         | Purpose                                        |
| ---------------------------- | ---------------------------------------------- |
| `analyze_project_for_tasks`  | Extract strategic tasks from project structure |
| `trace_task_chain`           | Map task dependencies and execution flow       |
| `create_task`                | Add new tasks with intelligent placement       |
| `prune_tasks`                | Remove outdated or redundant tasks             |
| `validate_task_architecture` | Ensure configuration follows best practices    |
| `get_task_recommendations`   | Get suggestions for optimization               |

## Example Workflows

### Analyzing a New Project

```bash
# Let Wise Mise MCP analyze your project
> analyze_project_for_tasks("./my-app")

✅ Detected: Next.js + TypeScript + Prisma
📋 Suggested Tasks:
  ├── build:dev (next dev)
  ├── build:prod (next build)
  ├── test:unit (jest)
  ├── test:e2e (playwright)
  ├── lint:code (eslint)
  ├── lint:types (tsc --noEmit)
  ├── db:migrate (prisma migrate)
  └── deploy:vercel (vercel deploy)
```

### Understanding Task Dependencies

```bash
# Trace the execution flow
> trace_task_chain("./my-app", "deploy:prod")

🕸️ Task Chain for deploy:prod:
  1. lint:types (TypeScript check)
  2. test:unit (Unit tests)
  3. build:prod (Production build)
  4. deploy:prod (Deploy to production)

💡 Recommendation: Add test:e2e before deploy:prod
```

### Smart Task Creation

```bash
# Describe what you want, get intelligent suggestions
> create_task(
    project_path="./my-app",
    task_description="Generate API documentation from OpenAPI spec"
  )

🧠 Analysis: Documentation generation task
📍 Suggested Placement: docs:api
🔗 Dependencies: build:prod (for spec generation)
📝 Suggested Implementation:
  [tasks.docs.api]
  run = "swagger-codegen generate -i ./openapi.json -l html2 -o ./docs/api"
  sources = ["src/api/**/*.ts", "openapi.json"]
  outputs = ["docs/api/**/*"]
```

## Architecture Philosophy

Wise Mise MCP follows a **Domain-Driven Design** approach to task organization:

### 🏛️ **Hierarchical Structure**

- **Level 1**: Domain (build, test, lint, etc.)
- **Level 2**: Environment/Type (dev, prod, unit, e2e)
- **Level 3**: Specific Implementation (server, client, api)

### 🔄 **Dependency Patterns**

- **Sequential**: `lint → test → build → deploy`
- **Parallel**: `test:unit` + `test:e2e` → `deploy`
- **Conditional**: `deploy:staging` → `test:smoke` → `deploy:prod`

### ⚡ **Performance Optimization**

- **Source Tracking**: Only rebuild when sources change
- **Output Caching**: Reuse previous build artifacts
- **Incremental Builds**: Support for modern build tools

## Technology Support

Wise Mise MCP includes expert knowledge for:

**Frontend**: React, Vue, Angular, Svelte, Next.js, Nuxt, Vite, Webpack
**Backend**: Node.js, Python, Go, Rust, Java, .NET, PHP
**Databases**: PostgreSQL, MySQL, MongoDB, Redis, Prisma, TypeORM
**Testing**: Jest, Vitest, Cypress, Playwright, PyTest, Go Test
**CI/CD**: GitHub Actions, GitLab CI, CircleCI, Jenkins
**Deployment**: Docker, Kubernetes, Vercel, Netlify, AWS, GCP

## Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Start for Contributors

```bash
# Clone and setup with UV
git clone https://github.com/delorenj/wise-mise-mcp
cd wise-mise-mcp
uv sync

# Run tests
uv run pytest

# Format code
uv run black .
uv run ruff check --fix .
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- **Documentation**: [Full API Documentation](https://wise-mise-mcp.readthedocs.io/)
- **Issues**: [GitHub Issues](https://github.com/delorenj/wise-mise-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/delorenj/wise-mise-mcp/discussions)

---

_Built with ❤️ by [Jarad DeLorenzo](https://github.com/delorenj) and the open source community_

