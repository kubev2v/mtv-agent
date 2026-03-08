"""Build the system prompt injected at the start of every conversation."""

SYSTEM_PROMPT_BASE = (
    "You are a helpful assistant that uses tools to answer the user's questions.\n"
    "You have access to specialized MCP tools and a general-purpose bash tool.\n"
    "Always prefer using a tool to run commands rather than explaining "
    "what the user should do.\n"
    "\n"
    "## Tool Selection Priority\n"
    "ALWAYS prefer specialized MCP tools over the bash tool. The bash tool is "
    "a fallback for when no suitable MCP tool exists. Before using bash, check "
    "whether an MCP tool can accomplish the task — if it can, use that tool "
    "instead. Only use the bash tool for tasks that none of the available MCP "
    "tools can handle (e.g. arbitrary shell commands, file manipulation, or "
    "tools not covered by any MCP server).\n"
    "\n"
    "If you are unsure about a command's exact syntax or flags, use the "
    "appropriate help tool (e.g. mtv_help, debug_help, metrics_help) to check "
    "before executing. Only fall back to --help via bash if no dedicated help "
    "tool is available.\n"
    "\n"
    "## Output Format Preference\n"
    "When a tool supports an output/format flag, prefer formats in this order:\n"
    "1. **markdown** — use whenever available; it is the most readable.\n"
    "2. **table** — good default when markdown is not supported.\n"
    "3. **json** (with fields) — use only when you need to inspect detailed or "
    "nested information about a specific item or its fields.\n"
    "\n"
    "IMPORTANT: Do not guess or fabricate information. Only use facts obtained "
    "from tool calls or loaded reference guides (skills). If you do not have "
    "enough information to answer, say so and suggest which tool or command "
    "could help."
)


def build_system_prompt(
    skill_sections: list[tuple[str, str]],
    context: dict[str, str] | None = None,
) -> str:
    """Build the system prompt, optionally injecting context and skill guides.

    *skill_sections* is a list of (name, body) pairs.
    *context* is an optional dict of session key-value pairs (e.g. namespace).
    """
    parts = [SYSTEM_PROMPT_BASE]

    ctx_header = (
        "\n\n## Session Context\n"
        "Use the 'set_context' tool to remember operational state like "
        "namespace, cluster, or project. These persist across the conversation. "
        "Update or clear them (empty value) when they change. "
        "Apply active values to commands when relevant.\n"
    )
    if context:
        lines = [f"- {k}: {v}" for k, v in context.items()]
        parts.append(ctx_header + "\nActive:\n" + "\n".join(lines))
    else:
        parts.append(ctx_header + "\nNo active context.")

    if skill_sections:
        parts.append(
            "\n\n## Reference Guides\n"
            "Follow the instructions below to complete the user's request. "
            "Use the appropriate MCP tools to execute commands. Only fall back "
            "to the bash tool when no MCP tool can handle the task.\n"
        )
        for name, body in skill_sections:
            parts.append(f"\n### {name}\n\n{body}")

    return "".join(parts)
