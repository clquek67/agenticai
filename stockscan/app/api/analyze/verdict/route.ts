import { NextRequest, NextResponse } from 'next/server'
import { anthropic, parseJSON } from '@/lib/claude'

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name, stage1, stage2, stage3, stage4, stage5 } = await req.json()

    // Determine verdict from stage statuses
    const statuses = [stage2?.status, stage3?.status, stage4?.status, stage5?.status].filter(Boolean)
    let verdict: 'invest' | 'watchlist' | 'pass'

    if (statuses.includes('red')) {
      verdict = 'pass'
    } else if (statuses.every((s) => s === 'green')) {
      verdict = 'invest'
    } else {
      verdict = 'watchlist'
    }

    const isCyclical = stage5?.cyclical === true

    // Generate synthesis summary via Claude (no web search)
    const systemPrompt = `You are a financial analyst writing a concise investment summary. Return ONLY valid JSON, no other text, no markdown fences:
{
  "final_summary": "2-3 paragraph investment summary"
}`

    const stageNotes = `
Business: ${stage1?.notes || 'N/A'}
Financials (${stage2?.status}): ${stage2?.notes || 'N/A'}
Valuation (${stage3?.status}): ${stage3?.notes || 'N/A'}
Promoter (${stage4?.status}): ${stage4?.notes || 'N/A'}
Industry (${stage5?.status}): ${stage5?.notes || 'N/A'}
Cyclical industry: ${isCyclical ? 'Yes — moderate confidence in projections' : 'No'}
Verdict: ${verdict.toUpperCase()}
`

    const response = await anthropic.messages.create({
      model: 'claude-sonnet-4-6',
      max_tokens: 1024,
      system: systemPrompt,
      messages: [
        {
          role: 'user',
          content: `Write an investment summary for ${company_name || ticker} (${ticker}) with verdict ${verdict}. Stage notes:\n${stageNotes}`,
        },
      ],
    })

    let raw = ''
    for (const block of response.content) {
      if (block.type === 'text') raw += block.text
    }

    const { final_summary } = parseJSON<{ final_summary: string }>(raw)

    return NextResponse.json({ verdict, final_summary })
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
