const BASE = "/api";

export interface StatusInfo {
  model: string;
  llm_status: string;
  mcp_servers: string[];
  tools: number;
  context_window: number;
  max_active_skills: number;
}

export interface ToolInfo {
  name: string;
  description: string;
}

export interface SkillInfo {
  name: string;
  description: string;
}

export interface ModelSwitchResult {
  model: string;
  context_window: number;
}

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export async function getStatus(): Promise<StatusInfo> {
  return request<StatusInfo>("/status");
}

export async function getModels(): Promise<string[]> {
  const data = await request<{ models: string[] }>("/models");
  return data.models;
}

export async function switchModel(model: string): Promise<ModelSwitchResult> {
  return request<ModelSwitchResult>("/model", {
    method: "PUT",
    body: JSON.stringify({ model }),
  });
}

export async function getTools(): Promise<ToolInfo[]> {
  const data = await request<{ tools: ToolInfo[] }>("/tools");
  return data.tools;
}

export async function getSkills(): Promise<SkillInfo[]> {
  const data = await request<{ skills: SkillInfo[] }>("/skills");
  return data.skills;
}

export interface PlaybookInfo {
  name: string;
  category: string;
  description: string;
  body: string;
}

export async function getPlaybooks(): Promise<PlaybookInfo[]> {
  const data = await request<{ playbooks: PlaybookInfo[] }>("/playbooks");
  return data.playbooks;
}

export interface MCPServerInfo {
  name: string;
  url: string;
  connected: boolean;
}

interface MCPMutateResult {
  servers: MCPServerInfo[];
  tools: number;
}

export async function getMcpServers(): Promise<MCPServerInfo[]> {
  const data = await request<{ servers: MCPServerInfo[] }>("/mcp");
  return data.servers;
}

export async function connectMcpServer(name: string): Promise<MCPMutateResult> {
  return request<MCPMutateResult>(`/mcp/${encodeURIComponent(name)}`, {
    method: "POST",
  });
}

export async function disconnectMcpServer(name: string): Promise<MCPMutateResult> {
  return request<MCPMutateResult>(`/mcp/${encodeURIComponent(name)}`, {
    method: "DELETE",
  });
}

// ---------------------------------------------------------------------------
// Chat history (persistent)
// ---------------------------------------------------------------------------

export interface ChatSummaryDTO {
  id: string;
  title: string;
  updated_at: number;
}

export interface ChatDetailDTO {
  id: string;
  title: string;
  created_at: number;
  updated_at: number;
  messages: { role: string; content: string }[];
}

export async function getChats(): Promise<ChatSummaryDTO[]> {
  const data = await request<{ chats: ChatSummaryDTO[] }>("/chats");
  return data.chats;
}

export async function getChat(id: string): Promise<ChatDetailDTO> {
  return request<ChatDetailDTO>(`/chats/${encodeURIComponent(id)}`);
}

export async function deleteChat(id: string): Promise<void> {
  await request(`/chats/${encodeURIComponent(id)}`, { method: "DELETE" });
}

export async function renameChat(id: string, title: string): Promise<void> {
  await request(`/chats/${encodeURIComponent(id)}/title`, {
    method: "PUT",
    body: JSON.stringify({ title }),
  });
}

// ---------------------------------------------------------------------------
// Direct tool execution
// ---------------------------------------------------------------------------

export interface ToolCallResult {
  tool: string;
  result: string;
}

export async function callTool(
  toolName: string,
  args: Record<string, unknown> = {},
): Promise<ToolCallResult> {
  return request<ToolCallResult>(`/tools/${encodeURIComponent(toolName)}`, {
    method: "POST",
    body: JSON.stringify({ arguments: args }),
  });
}

// ---------------------------------------------------------------------------
// Tool approval
// ---------------------------------------------------------------------------

export async function sendApproval(
  sessionId: string,
  approved: boolean,
  reason?: string,
): Promise<void> {
  const body: Record<string, unknown> = { approved };
  if (reason) body.reason = reason;
  await request(`/chat/${sessionId}/approve`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

// ---------------------------------------------------------------------------
// Session cancellation
// ---------------------------------------------------------------------------

export async function cancelChat(sessionId: string): Promise<void> {
  await request(`/chat/${sessionId}/cancel`, { method: "POST" });
}

/**
 * Fire-and-forget cancel via sendBeacon (works during page unload).
 */
export function cancelChatBeacon(sessionId: string): void {
  const url = `${BASE}/chat/${sessionId}/cancel`;
  navigator.sendBeacon(url);
}
