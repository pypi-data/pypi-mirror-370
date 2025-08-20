"""
Claude Code post-command hook for observability.

Called after Claude Code executes bash commands to analyze results and patterns.
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


def handle_post_command(
    output: str, command: str = "", session_id: str | None = None
) -> dict[str, Any]:
    """Handle post-command hook event."""
    try:
        # Basic output analysis
        output_length = len(output)
        has_error = any(
            error in output.lower()
            for error in ["error", "failed", "exception", "traceback"]
        )
        exit_code_success = "exit code: 0" in output or not has_error
        line_count = output.count("\n")

        # Pattern detection
        contains_json = "{" in output and "}" in output
        contains_xml = "<" in output and ">" in output
        contains_warnings = "warning" in output.lower() or "warn" in output.lower()

        event = HookEvent(
            content=HookEventContent(
                event_type="post_command",
                tool_name="Bash",
                command=command,
                output=output,
                session_id=session_id,
                metadata={
                    "output_length": output_length,
                    "has_error": has_error,
                    "exit_code_success": exit_code_success,
                    "line_count": line_count,
                    "contains_json": contains_json,
                    "contains_xml": contains_xml,
                    "contains_warnings": contains_warnings,
                    "hook_type": "post_command",
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
            "output_length": output_length,
            "has_error": has_error,
            "exit_code_success": exit_code_success,
            "line_count": line_count,
            "event_logged": True,
        }

    except Exception as e:
        return {"error": str(e), "event_logged": False}


def main():
    """Main entry point for post-command hook."""
    try:
        # Read JSON input from stdin
        hook_input = json.load(sys.stdin)

        # Extract session information
        session_id = hook_input.get("session_id", None)

        # Extract command output from hook input
        tool_input = hook_input.get("tool_input", {})
        tool_output = hook_input.get("tool_output", "")
        command = tool_input.get("command", "")

        result = handle_post_command(tool_output, command, session_id)

        # Always output JSON for Claude Code
        print(json.dumps(result))

        sys.exit(0)

    except Exception as e:
        print(f"Error in post-command hook: {e}", file=sys.stderr)
        print(json.dumps({"error": str(e)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
