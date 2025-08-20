"""
Claude Code prompt submission hook for observability.

Called when user submits prompts to Claude Code to monitor interaction patterns.
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


def handle_prompt_submitted(
    prompt: str, session_id: str | None = None
) -> dict[str, Any]:
    """Handle user prompt submission hook event."""
    try:
        # Basic prompt analysis
        prompt_length = len(prompt)
        word_count = len(prompt.split())
        has_code_request = any(
            keyword in prompt.lower()
            for keyword in [
                "implement",
                "code",
                "function",
                "class",
                "script",
                "program",
            ]
        )
        has_file_reference = "@" in prompt or "file" in prompt.lower()
        has_question = "?" in prompt
        estimated_complexity = (
            "high"
            if prompt_length > 1000
            else "medium" if prompt_length > 200 else "low"
        )

        event = HookEvent(
            content=HookEventContent(
                event_type="prompt_submitted",
                tool_name="UserPromptSubmit",
                session_id=session_id,
                metadata={
                    "prompt": prompt,
                    "prompt_length": prompt_length,
                    "word_count": word_count,
                    "has_code_request": has_code_request,
                    "has_file_reference": has_file_reference,
                    "has_question": has_question,
                    "estimated_complexity": estimated_complexity,
                    "hook_type": "prompt_submitted",
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
            "prompt_length": prompt_length,
            "word_count": word_count,
            "estimated_complexity": estimated_complexity,
            "event_logged": True,
        }

    except Exception as e:
        return {"error": str(e), "event_logged": False}


def main():
    """Main entry point for prompt submission hook."""
    try:
        # Read JSON input from stdin
        hook_input = json.load(sys.stdin)

        # Extract session information
        session_id = hook_input.get("session_id", None)

        # Extract prompt from hook input
        prompt = hook_input.get("prompt", "")

        result = handle_prompt_submitted(prompt, session_id)

        # Always output JSON for Claude Code
        print(json.dumps(result))

        sys.exit(0)

    except Exception as e:
        print(f"Error in prompt submission hook: {e}", file=sys.stderr)
        print(json.dumps({"error": str(e)}))
        sys.exit(0)


if __name__ == "__main__":
    main()
