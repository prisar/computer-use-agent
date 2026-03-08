"""
Benchmark evaluation for computer_use_agent.

Each test case sends a natural-language task to the agent and validates:
  - Which browser tools were called (structural check)
  - Whether the final answer contains expected keywords (semantic check)

Run:
    python eval/run_eval.py

Requires GOOGLE_API_KEY in the environment (or .env in the project root).
"""

import asyncio
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Load .env from project root so the script can be run from any directory.
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

sys.path.insert(0, str(project_root))

from google.adk.runners import InMemoryRunner
from google.genai import types

from computer_use_agent.agent import root_agent
from computer_use_agent.tools import _reset_ctx


@dataclass
class EvalCase:
    name: str
    task: str
    # Tool names that must appear in the tool calls during the run.
    required_tools: list[str] = field(default_factory=list)
    # Strings that must appear (case-insensitive) in the final text reply.
    expected_keywords: list[str] = field(default_factory=list)


EVAL_CASES: list[EvalCase] = [
    EvalCase(
        name="navigate_and_read_title",
        task="Navigate to https://example.com and tell me the page title.",
        required_tools=["browser_navigate"],
        expected_keywords=["example domain"],
    ),
    EvalCase(
        name="get_page_text",
        task=(
            "Go to https://example.com and use the text tool to read the page. "
            "What is the main heading on the page?"
        ),
        required_tools=["browser_navigate", "browser_get_text"],
        expected_keywords=["example domain"],
    ),
    EvalCase(
        name="scroll_and_screenshot",
        task=(
            "Navigate to https://example.com, scroll down, then take a screenshot "
            "and tell me what you see."
        ),
        required_tools=["browser_navigate", "browser_scroll", "browser_screenshot"],
        expected_keywords=[],
    ),
]


@dataclass
class EvalResult:
    name: str
    passed: bool
    details: str
    tools_called: list[str] = field(default_factory=list)
    final_response: str = ""


async def run_case(case: EvalCase) -> EvalResult:
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="eval", session_id=case.name
    )

    message = types.Content(
        role="user", parts=[types.Part.from_text(text=case.task)]
    )

    tools_called: list[str] = []
    final_response = ""

    try:
        async for event in runner.run_async(
            user_id="eval",
            session_id=case.name,
            new_message=message,
        ):
            # Collect tool calls.
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        tools_called.append(part.function_call.name)
                    if hasattr(part, "text") and part.text:
                        final_response = part.text  # keep last text part
    except Exception as exc:
        return EvalResult(
            name=case.name,
            passed=False,
            details=f"Exception during run: {exc}",
            tools_called=tools_called,
            final_response=final_response,
        )

    # Structural check: required tools were called.
    missing_tools = [t for t in case.required_tools if t not in tools_called]

    # Semantic check: expected keywords in final response.
    response_lower = final_response.lower()
    missing_keywords = [
        kw for kw in case.expected_keywords if kw.lower() not in response_lower
    ]

    passed = not missing_tools and not missing_keywords
    details_parts = []
    if missing_tools:
        details_parts.append(f"missing tools: {missing_tools}")
    if missing_keywords:
        details_parts.append(f"missing keywords in response: {missing_keywords}")
    details = "; ".join(details_parts) if details_parts else "all checks passed"

    return EvalResult(
        name=case.name,
        passed=passed,
        details=details,
        tools_called=tools_called,
        final_response=final_response,
    )


async def main() -> None:
    print(f"Running {len(EVAL_CASES)} eval case(s)...\n")
    results: list[EvalResult] = []

    for case in EVAL_CASES:
        print(f"  [{case.name}] ... ", end="", flush=True)
        result = await run_case(case)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        print(status)
        if not result.passed:
            print(f"    details : {result.details}")
        print(f"    tools   : {result.tools_called}")
        if result.final_response:
            snippet = result.final_response[:120].replace("\n", " ")
            print(f"    response: {snippet}")

    # Clean up browser before the event loop closes to avoid asyncio warnings.
    await _reset_ctx()

    passed = sum(r.passed for r in results)
    total = len(results)
    print(f"\n{passed}/{total} passed")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
