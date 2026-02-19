const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000';

/**
 * Send a conversation to the chat endpoint and return the reply.
 * @param {Array} messages - [{role: 'user'|'assistant', content: string}]
 * @returns {Promise<{reply: string, messages: Array}>}
 */
export async function sendChat(messages) {
  const res = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  });
  if (!res.ok) {
    throw new Error(`Chat error: ${res.status}`);
  }
  return res.json();
}
