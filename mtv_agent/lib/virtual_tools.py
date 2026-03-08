"""Virtual tool definitions handled inside the agent loop (not executed externally)."""

from mtv_agent.lib.skills import SkillsManager

SELECT_SKILL_TOOL_NAME = "select_skill"
SET_CONTEXT_TOOL_NAME = "set_context"


def make_select_skill_tool(skills: SkillsManager) -> dict | None:
    """Build the select_skill tool definition, or None if no skills exist."""
    catalog = skills.get_catalog()
    if not catalog:
        return None
    return {
        "type": "function",
        "function": {
            "name": SELECT_SKILL_TOOL_NAME,
            "description": (
                "Load a reference guide for a specific task. "
                "Multiple guides can be active at once; calling this adds "
                "the requested guide to the active set. If the limit is "
                "reached, the oldest guide is dropped automatically.\n"
                "Call this BEFORE running commands so you have the right "
                "instructions.\nAvailable skills:\n" + catalog + "\n"
                "Pass 'none' to clear ALL active guides."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "Skill name to add to active guides, "
                            "or 'none' to clear all."
                        ),
                    },
                },
                "required": ["name"],
            },
        },
    }


def make_set_context_tool() -> dict:
    """Build the set_context tool definition for the LLM."""
    return {
        "type": "function",
        "function": {
            "name": SET_CONTEXT_TOOL_NAME,
            "description": (
                "Set or unset a session context value. Context values are "
                "persistent key-value pairs that influence how commands are "
                "run (e.g. namespace, cluster, project).\n"
                "When you discover the active namespace, cluster, or similar "
                "operational state, call this tool to record it so future "
                "commands use the correct flags automatically.\n"
                "To remove a key, pass an empty string as the value."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": (
                            "Context key, e.g. 'namespace', 'cluster', 'project'."
                        ),
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "Value to set, or empty string to unset the key."
                        ),
                    },
                },
                "required": ["key", "value"],
            },
        },
    }
