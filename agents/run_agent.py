"""Atlas Engine — agent runner.

Runs a named autonomous agent task using the Claude Agent SDK (the same
harness that powers Claude Code). Tasks are markdown prompts in
agents/tasks/; skills in .claude/skills/ are loaded automatically so every
agent inherits the atlas playbook.

Usage:
  export ANTHROPIC_API_KEY=sk-...
  python agents/run_agent.py scraper_repair
  python agents/run_agent.py fdd_qa
  python agents/run_agent.py report_writer

In CI these run via .github/workflows/ (see SETUP.md). Locally you can also
just open the repo in Claude Code and ask for the same things interactively.
"""
import asyncio, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


async def run(task: str):
    from claude_agent_sdk import query, ClaudeAgentOptions

    prompt_path = os.path.join(ROOT, "agents", "tasks", f"{task}.md")
    if not os.path.exists(prompt_path):
        tasks = [f[:-3] for f in os.listdir(os.path.join(ROOT, "agents", "tasks"))]
        sys.exit(f"unknown task '{task}'. available: {', '.join(sorted(tasks))}")
    prompt = open(prompt_path).read()

    options = ClaudeAgentOptions(
        cwd=ROOT,
        allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep",
                       "WebSearch", "WebFetch", "Skill"],
        permission_mode="acceptEdits",
        setting_sources=["project"],   # loads .claude/skills/ + CLAUDE.md
        max_turns=60,                  # cost guardrail for unattended runs
    )

    print(f"[agent:{task}] starting (cwd={ROOT})")
    async for message in query(prompt=prompt, options=options):
        # Stream lightweight progress to CI logs.
        mtype = getattr(message, "type", type(message).__name__)
        if hasattr(message, "result"):
            print(f"\n[agent:{task}] RESULT\n{message.result}")
        elif mtype in ("assistant", "AssistantMessage"):
            for block in getattr(message, "content", []) or []:
                if getattr(block, "type", "") == "tool_use":
                    print(f"[agent:{task}] tool: {getattr(block, 'name', '?')}")
    print(f"[agent:{task}] done")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: python agents/run_agent.py <task>")
    asyncio.run(run(sys.argv[1]))
