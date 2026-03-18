const BASE = "/api";

export interface StreamCallbacks {
  onSession?: (sessionId: string) => void;
  onThinking?: () => void;
  onUsage?: (data: {
    total_tokens: number;
    prompt_tokens: number;
    completion_tokens: number;
    context_window: number;
  }) => void;
  onToolCall?: (name: string, args: Record<string, unknown>) => void;
  onToolResult?: (name: string, result: string) => void;
  onToolDenied?: (name: string, reason?: string) => void;
  onSkillSelected?: (name: string) => void;
  onSkillCleared?: () => void;
  onContextSet?: (key: string, value: string) => void;
  onContextUnset?: (key: string) => void;
  onContent?: (content: string) => void;
  onCancelled?: (content: string) => void;
  onDone?: (content: string) => void;
  onError?: (error: Error) => void;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  skills?: string[];
  context?: Record<string, string>;
}

export async function streamChat(
  request: ChatRequest,
  callbacks: StreamCallbacks,
  options?: { approve?: boolean; signal?: AbortSignal },
): Promise<void> {
  const approve = options?.approve ? "?approve=true" : "";
  const url = `${BASE}/chat/stream${approve}`;

  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(request),
      signal: options?.signal,
    });
  } catch (err) {
    callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
    return;
  }

  if (!response.ok) {
    callbacks.onError?.(new Error(`Stream ${response.status}: ${response.statusText}`));
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    callbacks.onError?.(new Error("No response body"));
    return;
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let currentEvent = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (line.startsWith("event:")) {
          currentEvent = line.slice(6).trim();
        } else if (line.startsWith("data:")) {
          const raw = line.slice(5).trim();
          if (!raw) continue;

          let data: Record<string, unknown>;
          try {
            data = JSON.parse(raw);
          } catch {
            continue;
          }

          dispatchEvent(currentEvent, data, callbacks);
          currentEvent = "";
        }
      }
    }
  } catch (err) {
    if ((err as Error).name !== "AbortError") {
      callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }
}

function dispatchEvent(event: string, data: Record<string, unknown>, cb: StreamCallbacks): void {
  switch (event) {
    case "session":
      cb.onSession?.(data.session_id as string);
      break;
    case "thinking":
      cb.onThinking?.();
      break;
    case "usage":
      cb.onUsage?.(
        data as {
          total_tokens: number;
          prompt_tokens: number;
          completion_tokens: number;
          context_window: number;
        },
      );
      break;
    case "tool_call":
      cb.onToolCall?.(data.name as string, data.arguments as Record<string, unknown>);
      break;
    case "tool_result":
      cb.onToolResult?.(data.name as string, data.result as string);
      break;
    case "tool_denied":
      cb.onToolDenied?.(data.name as string, data.reason as string | undefined);
      break;
    case "skill_selected":
      cb.onSkillSelected?.(data.name as string);
      break;
    case "skill_cleared":
      cb.onSkillCleared?.();
      break;
    case "context_set":
      cb.onContextSet?.(data.key as string, data.value as string);
      break;
    case "context_unset":
      cb.onContextUnset?.(data.key as string);
      break;
    case "content":
      cb.onContent?.(data.content as string);
      break;
    case "cancelled":
      cb.onCancelled?.(data.content as string);
      break;
    case "done":
      cb.onDone?.(data.content as string);
      break;
  }
}
