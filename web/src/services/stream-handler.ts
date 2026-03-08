import {
  appState,
  defaultPolicyForTool,
  type ChatSummary,
  type ToolPolicy,
} from "../state/app-state.js";
import { getChats, sendApproval } from "./api-client.js";
import { streamChat } from "./stream-client.js";

async function refreshChatList(): Promise<void> {
  try {
    const dtos = await getChats();
    const chats: ChatSummary[] = dtos.map((c) => ({
      id: c.id,
      title: c.title,
      updatedAt: c.updated_at,
    }));
    appState.setChatList(chats);
  } catch {
    // non-critical -- sidebar will just keep stale list
  }
}

/**
 * Execute a streaming chat request, wiring all SSE callbacks into appState.
 * Returns the AbortController so the caller can cancel.
 */
export function executeStreamChat(
  message: string,
  approve: boolean,
  startTime: number,
  signal: AbortSignal,
): Promise<void> {
  const s = appState.state;

  return streamChat(
    {
      message,
      session_id: s.sessionId ?? undefined,
      skills: s.activeSkills.length ? s.activeSkills : undefined,
      context: Object.keys(s.context).length ? s.context : undefined,
    },
    {
      onSession: (sessionId) => {
        appState.update({ sessionId, activeChatId: sessionId });
        const exists = appState.state.chatList.some((c) => c.id === sessionId);
        if (!exists) {
          const plain = message
            .replace(/^#{1,6}\s+/gm, "")
            .replace(/\*{1,3}(.+?)\*{1,3}/g, "$1")
            .replace(/`(.+?)`/g, "$1")
            .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
            .replace(/^[-*>]+\s+/gm, "")
            .replace(/\n/g, " ")
            .trim();
          const title = plain.length > 80 ? plain.slice(0, 80).trimEnd() + "..." : plain;
          appState.setChatList([
            { id: sessionId, title: title || "New Chat", updatedAt: Date.now() / 1000 },
            ...appState.state.chatList,
          ]);
        }
      },

      onThinking: () => {
        appState.updateLastAssistant((m) => ({ ...m, thinking: true }));
      },

      onUsage: (data) => {
        appState.update({
          usage: {
            totalTokens: data.total_tokens,
            promptTokens: data.prompt_tokens,
            completionTokens: data.completion_tokens,
            contextWindow: data.context_window,
          },
        });
      },

      onToolCall: (name, args) => {
        appState.updateLastAssistant((m) => ({ ...m, thinking: false }));
        let policy: ToolPolicy = appState.state.toolPolicies[name] ?? defaultPolicyForTool(name);

        if (name === "select_skill") {
          const requested = (args.name as string) ?? "";
          const alreadyActive = appState.state.activeSkills.some(
            (s) => s.toLowerCase() === requested.toLowerCase(),
          );
          if (alreadyActive) {
            policy = "auto-accept";
          }
        }

        const needsManual = approve && policy === "ask";
        appState.addToolCallToLast({ name, arguments: args, pending: needsManual });

        if (approve && policy !== "ask") {
          const sid = appState.state.sessionId;
          if (sid) {
            const accepted = policy === "auto-accept";
            sendApproval(sid, accepted, accepted ? undefined : "auto-rejected by policy").catch(
              () => {},
            );
            if (!accepted) {
              appState.updateLastToolCall((tc) => ({
                ...tc,
                pending: false,
                denied: true,
                denyReason: "auto-rejected by policy",
              }));
            }
          }
        }
      },

      onToolResult: (_name, result) => {
        appState.updateLastToolCall((tc) => ({
          ...tc,
          result,
          pending: false,
        }));
      },

      onToolDenied: (_name, reason) => {
        appState.updateLastToolCall((tc) => ({
          ...tc,
          denied: true,
          denyReason: reason,
          pending: false,
        }));
      },

      onSkillSelected: (name) => {
        if (!appState.state.activeSkills.includes(name)) {
          appState.setActiveSkills([...appState.state.activeSkills, name]);
        }
      },

      onSkillCleared: () => {
        appState.setActiveSkills([]);
      },

      onContextSet: (key, value) => {
        const policy =
          appState.state.toolPolicies["set_context"] ?? defaultPolicyForTool("set_context");
        if (policy !== "auto-reject") {
          appState.setContext(key, value);
        }
      },

      onContextUnset: (key) => {
        const policy =
          appState.state.toolPolicies["set_context"] ?? defaultPolicyForTool("set_context");
        if (policy !== "auto-reject") {
          appState.removeContext(key);
        }
      },

      onContent: (content) => {
        appState.updateLastAssistant((m) => ({
          ...m,
          content,
          thinking: false,
        }));
      },

      onDone: (content) => {
        const elapsed = (performance.now() - startTime) / 1000;
        appState.updateLastAssistant((m) => ({
          ...m,
          content,
          thinking: false,
        }));
        appState.update({
          isStreaming: false,
          streamElapsed: elapsed,
          activeChatId: appState.state.sessionId,
        });
        refreshChatList();
      },

      onError: (err) => {
        appState.updateLastAssistant((m) => ({
          ...m,
          content: `Error: ${err.message}`,
          thinking: false,
        }));
        appState.update({ isStreaming: false });
      },
    },
    { approve, signal },
  );
}
