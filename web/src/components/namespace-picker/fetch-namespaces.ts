import { callTool } from "../../services/api-client.js";

/**
 * Fetch all namespace names from the cluster via the debug_read MCP tool.
 * Returns a sorted array of namespace name strings.
 */
export async function fetchNamespaces(): Promise<string[]> {
  const resp = await callTool("debug_read", {
    command: "list",
    flags: { resource: "namespaces", all_namespaces: true, output: "json", query: "select name" },
  });

  let rows: unknown;
  try {
    rows = JSON.parse(resp.result);
  } catch (err) {
    throw new Error(
      `Failed to parse namespace list: ${err instanceof Error ? err.message : resp.result}`,
      { cause: err },
    );
  }

  if (!Array.isArray(rows)) {
    throw new Error(`Expected array of namespaces, got: ${typeof rows}`);
  }

  const names: string[] = rows
    .map((r: unknown) => {
      if (typeof r === "string") return r.trim() || "";
      if (r && typeof r === "object" && "name" in r) {
        const name = (r as { name: unknown }).name;
        return typeof name === "string" && name.trim() !== "" ? name.trim() : "";
      }
      return "";
    })
    .filter(Boolean);

  return names.sort((a, b) => a.localeCompare(b));
}
