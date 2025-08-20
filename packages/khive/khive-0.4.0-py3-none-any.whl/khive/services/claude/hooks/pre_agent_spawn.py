"""
Claude Code pre-agent-spawn hook for observability.

Called before Claude Code spawns Task agents to monitor task coordination patterns.
"""

import json
import sys
from typing import Any

import anyio

from khive.services.claude.hooks.hook_event import (
    HookEvent,
    HookEventContent,
    hook_event_logger,
    shield,
)


def handle_pre_agent_spawn(
    task_description: str, session_id: str | None = None
) -> dict[str, Any]:
    """Handle pre-agent-spawn hook event."""
    try:
        # Basic task analysis
        task_length = len(task_description)
        has_complex_keywords = any(
            keyword in task_description.lower()
            for keyword in [
                "analyze",
                "architect",
                "implement",
                "refactor",
                "optimize",
                "research",
            ]
        )
        estimated_complexity = (
            "high" if task_length > 500 else "medium" if task_length > 100 else "low"
        )
        word_count = len(task_description.split())

        event = HookEvent(
            content=HookEventContent(
                event_type="pre_agent_spawn",
                tool_name="Task",
                session_id=session_id,
                metadata={
                    "task_description": task_description,
                    "task_length": task_length,
                    "word_count": word_count,
                    "has_complex_keywords": has_complex_keywords,
                    "estimated_complexity": estimated_complexity,
                    "hook_type": "pre_agent_spawn",
                },
            )
        )

        try:
            anyio.run(shield, event.save)
        except Exception as e:
            hook_event_logger.error(
                f"Failed to save event: {e}",
                exc_info=True,
            )

        return {
            "proceed": True,
            "task_length": task_length,
            "estimated_complexity": estimated_complexity,
            "event_logged": True,
        }

    except Exception as e:
        return {
            "proceed": True,  # Don't block on error
            "error": str(e),
            "event_logged": False,
        }


def main():
    """Main entry point for pre-agent-spawn hook."""
    try:
        # Read JSON input from stdin
        hook_input = json.load(sys.stdin)

        # Extract session information
        session_id = hook_input.get("session_id", None)

        # Extract task description from tool input
        tool_input = hook_input.get("tool_input", {})
        task_description = tool_input.get("prompt", "") or tool_input.get(
            "description", ""
        )

        result = handle_pre_agent_spawn(task_description, session_id)

        # Always output JSON for Claude Code
        print(json.dumps(result))

        # Exit with 0 for proceed, 1 for block
        sys.exit(0 if result.get("proceed", True) else 1)

    except Exception as e:
        print(f"Error in pre-agent-spawn hook: {e}", file=sys.stderr)
        # Default to proceed on error
        print(json.dumps({"proceed": True, "error": str(e)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
