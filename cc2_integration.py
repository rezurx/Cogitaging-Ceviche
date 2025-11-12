#!/usr/bin/env python3
"""
Cogitating-Ceviche CC2 Integration
Hybrid approach combining Continuum v2.0 and CC-Subagents v2.0 Task tool orchestration
"""

import sys
import json
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path.home() / "dev" / "continuum"))
sys.path.insert(0, str(Path(__file__).parent))

from continuum_cc2_client import ContinuumCC2Client, TodoItem
from claude_subagent_manager import ProjectAnalyzer, ProjectAnalysis
from task_tool_orchestrator import TaskToolOrchestrator, TaskConfig


class CogitatingCevicheOrchestrator:
    """
    Integrated orchestrator for cogitating-ceviche project.
    Combines Continuum session memory with CC-Subagents intelligent agent selection.
    """

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.continuum = ContinuumCC2Client(api_url="http://localhost:8000")
        self.orchestrator = TaskToolOrchestrator(str(self.project_path))

    def restore_session(self) -> dict:
        """
        Restore previous session context.

        Returns:
            Dictionary with restored todos and project context
        """
        print("🔄 Restoring previous session...")

        # Restore todos
        todos = self.continuum.restore_todos()
        print(f"✓ Restored {len(todos)} todos")

        # Get project context
        context = self.continuum.get_agent_context()
        summary = self.continuum.get_project_summary()

        print(f"📋 Project: {summary}")
        print()

        return {
            "todos": todos,
            "context": context,
            "summary": summary
        }

    def analyze_project(self) -> ProjectAnalysis:
        """
        Analyze project structure and recommend agents.

        Returns:
            Project analysis results
        """
        print("🔍 Analyzing project structure...")

        plan = self.orchestrator.analyze_and_recommend(create_plan=False)

        print(f"✓ Project Type: {plan.analysis.project_type}")
        print(f"✓ Complexity: {plan.analysis.complexity_score}/10")
        print(f"✓ Recommended Agents: {len(plan.agents)}")
        print()

        return plan.analysis

    def generate_task_configs_for_project(self) -> list:
        """
        Generate Task tool configs for project-specific agents.

        Returns:
            List of TaskConfig objects
        """
        print("🤖 Generating Task tool configurations...")

        plan = self.orchestrator.analyze_and_recommend(create_plan=True)

        print(f"✓ Generated {len(plan.task_configs)} agent configurations")
        print()

        # Display agents
        for agent in plan.agents:
            status = "⚡" if agent.auto_invoke else "  "
            print(f"  {status} {agent.name} ({agent.priority} priority)")

        print()

        return plan.task_configs

    def launch_content_optimization_agents(self) -> list:
        """
        Launch specialized agents for content optimization tasks.

        Returns:
            List of task configs for content management
        """
        print("📝 Launching content optimization agents...")

        objectives = [
            "Analyze blog content for SEO optimization opportunities",
            "Review Hugo configuration for performance improvements",
            "Check RSS feed generation and syndication setup"
        ]

        configs = self.orchestrator.launch_parallel_agents(objectives)

        print(f"✓ Generated {len(configs)} parallel agent tasks")
        print()

        return configs

    def sync_completed_task(self, task_content: str):
        """
        Sync completed task to Continuum.

        Args:
            task_content: Task description
        """
        todo = TodoItem(
            content=task_content,
            activeForm=f"Completed {task_content}",
            status="completed"
        )

        self.continuum.sync_todos([todo.dict() if hasattr(todo, 'dict') else vars(todo)])
        print(f"✓ Synced completion: {task_content}")

    def emit_deployment_event(self, success: bool, details: dict):
        """
        Emit deployment event to Continuum hooks.

        Args:
            success: Whether deployment succeeded
            details: Deployment details
        """
        event_type = "deployment_succeeded" if success else "deployment_failed"

        self.continuum.emit_event("tool_used", {
            "tool": "deployment",
            "success": success,
            "details": details
        })

        print(f"✓ Emitted deployment event: {event_type}")


# ============================================================================
# CLI Commands
# ============================================================================

def cmd_restore():
    """Restore previous session"""
    orchestrator = CogitatingCevicheOrchestrator()
    session = orchestrator.restore_session()

    print("=" * 60)
    print("RESTORED SESSION")
    print("=" * 60)
    print()

    if session["todos"]:
        print("Pending Todos:")
        for todo in session["todos"]:
            status_icon = {"pending": "⏳", "in_progress": "🔄", "completed": "✅"}
            icon = status_icon.get(todo.status, "❓")
            print(f"  {icon} {todo.content}")
    else:
        print("No pending todos from previous session.")

    print()
    print("Project Context:")
    print(session["summary"])


def cmd_analyze():
    """Analyze project and show recommendations"""
    orchestrator = CogitatingCevicheOrchestrator()
    analysis = orchestrator.analyze_project()

    print("=" * 60)
    print("PROJECT ANALYSIS")
    print("=" * 60)
    print()
    print(f"Project Type: {analysis.project_type}")
    print(f"Complexity: {analysis.complexity_score}/10")
    print()
    print(f"Languages: {', '.join(analysis.languages)}")
    print(f"Frameworks: {', '.join(analysis.frameworks)}")
    print(f"Tools: {', '.join(analysis.tools)}")
    print()
    print(f"Architecture Patterns: {', '.join(analysis.architecture_patterns)}")
    print()
    print(f"Suggested Agents: {len(analysis.suggested_subagents)}")
    for agent in analysis.suggested_subagents:
        print(f"  • {agent}")


def cmd_generate_configs():
    """Generate Task tool configs"""
    orchestrator = CogitatingCevicheOrchestrator()
    configs = orchestrator.generate_task_configs_for_project()

    output_file = Path("cc2_task_configs.json")
    with open(output_file, "w") as f:
        json.dump([{
            "subagent_type": c.subagent_type,
            "model": c.model,
            "description": c.description,
            "prompt": c.prompt
        } for c in configs], f, indent=2)

    print(f"✓ Saved configurations to {output_file}")
    print()
    print("Usage in Claude Code 2:")
    print("  Read cc2_task_configs.json and launch Task tool agents")


def cmd_optimize_content():
    """Launch content optimization agents"""
    orchestrator = CogitatingCevicheOrchestrator()
    configs = orchestrator.launch_content_optimization_agents()

    output_file = Path("content_optimization_tasks.json")
    with open(output_file, "w") as f:
        json.dump([{
            "subagent_type": c.subagent_type,
            "model": c.model,
            "description": c.description,
            "prompt": c.prompt
        } for c in configs], f, indent=2)

    print(f"✓ Saved content optimization tasks to {output_file}")


def cmd_stats():
    """Show integration statistics"""
    orchestrator = CogitatingCevicheOrchestrator()
    stats = orchestrator.continuum.get_stats()

    print("=" * 60)
    print("CC2 INTEGRATION STATISTICS")
    print("=" * 60)
    print()
    print(f"Continuum Version: {stats['version']}")
    print(f"Last Sync: {stats['last_sync']}")
    print()
    print("Todos:")
    print(f"  Total: {stats['todos']['total']}")
    print(f"  Completed: {stats['todos']['completed']}")
    print(f"  In Progress: {stats['todos']['in_progress']}")
    print(f"  Pending: {stats['todos']['pending']}")
    print()
    print(f"Session History Entries: {stats['session_history_entries']}")
    print(f"Next Tasks: {stats['next_tasks']}")
    print(f"Events Logged: {stats['events_logged']}")


def cmd_test_sync():
    """Test todo sync"""
    orchestrator = CogitatingCevicheOrchestrator()

    print("Testing todo sync...")

    test_todos = [
        TodoItem(content="Test task 1", activeForm="Testing task 1", status="completed"),
        TodoItem(content="Test task 2", activeForm="Testing task 2", status="in_progress"),
        TodoItem(content="Test task 3", activeForm="Testing task 3", status="pending")
    ]

    result = orchestrator.continuum.sync_todos([
        vars(t) for t in test_todos
    ])

    print(f"✓ Synced {result['count']} todos")
    print(f"✓ Timestamp: {result['timestamp']}")


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cogitating-Ceviche CC2 Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cc2_integration.py restore          # Restore previous session
  python cc2_integration.py analyze          # Analyze project
  python cc2_integration.py generate         # Generate Task tool configs
  python cc2_integration.py optimize         # Launch content optimization
  python cc2_integration.py stats            # Show statistics
  python cc2_integration.py test            # Test todo sync
        """
    )

    parser.add_argument("command", choices=[
        "restore", "analyze", "generate", "optimize", "stats", "test"
    ], help="Command to execute")

    args = parser.parse_args()

    try:
        if args.command == "restore":
            cmd_restore()
        elif args.command == "analyze":
            cmd_analyze()
        elif args.command == "generate":
            cmd_generate_configs()
        elif args.command == "optimize":
            cmd_optimize_content()
        elif args.command == "stats":
            cmd_stats()
        elif args.command == "test":
            cmd_test_sync()

    except ConnectionError as e:
        print(f"❌ Error: {e}")
        print()
        print("Make sure Continuum server is running:")
        print("  cd ~/dev/continuum")
        print("  python3 server-v2.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
