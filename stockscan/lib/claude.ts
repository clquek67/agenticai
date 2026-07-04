import Anthropic from '@anthropic-ai/sdk'

export const anthropic = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
})

export async function analyzeWithClaude(systemPrompt: string, userMessage: string): Promise<string> {
  const response = await anthropic.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 2048,
    system: systemPrompt,
    tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 5 } as any],
    messages: [{ role: 'user', content: userMessage }],
  })

  // Extract text from the final response
  let result = ''
  for (const block of response.content) {
    if (block.type === 'text') {
      result += block.text
    }
  }

  // Handle tool use — keep processing until we get a non-tool-use stop reason
  let currentResponse = response
  while (currentResponse.stop_reason === 'tool_use') {
    const toolUseBlocks = currentResponse.content.filter((b) => b.type === 'tool_use')
    const toolResults = toolUseBlocks.map((block: any) => ({
      type: 'tool_result' as const,
      tool_use_id: block.id,
      content: block.input?.query ? `Search results for: ${block.input.query}` : 'No results',
    }))

    const nextResponse = await anthropic.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 2048,
      system: systemPrompt,
      tools: [{ type: 'web_search_20250305', name: 'web_search', max_uses: 5 } as any],
      messages: [
        { role: 'user', content: userMessage },
        { role: 'assistant', content: currentResponse.content },
        { role: 'user', content: toolResults },
      ],
    })

    result = ''
    for (const block of nextResponse.content) {
      if (block.type === 'text') {
        result += block.text
      }
    }
    currentResponse = nextResponse
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
