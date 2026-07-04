import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

// web_search_20250305 is a server-side tool — Anthropic executes searches automatically.
// A single API call returns stop_reason="end_turn" with text incorporating search results.
export async function analyzeWithClaude(systemPrompt: string, userMessage: string): Promise<string> {
  const response = await (anthropic.beta.messages.create as Function)({
    model: 'claude-sonnet-4-6',
    max_tokens: 2048,
    system: systemPrompt,
    tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 5 }],
    messages: [{ role: 'user', content: userMessage }],
    betas: ['web-search-2025-03-05'],
  })

  let result = ''
  for (const block of response.content) {
    if (block.type === 'text') {
      result += block.text
    }
  }
  return result
}

export function parseJSON<T>(raw: string): T {
  // Strip markdown fences defensively
  const cleaned = raw
    .replace(/^```json\s*/i, '')
    .replace(/^```\s*/i, '')
    .replace(/```\s*$/i, '')
    .trim()
  return JSON.parse(cleaned)
}
