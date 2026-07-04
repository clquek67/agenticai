import { NextRequest, NextResponse } from 'next/server'
import { analyzeWithClaude, parseJSON } from '@/lib/claude'

const SYSTEM_PROMPT = `You are a financial analyst. Given a stock ticker or company name, use web search to assess its industry and risk profile. Return ONLY valid JSON, no other text, no markdown fences, matching this exact schema:
{
  "cyclical": true or false or null,
  "cyclical_type": "string describing cycle type or null",
  "demand_trend": "growing" or "flat" or "shrinking" or "unknown",
  "market_structure": "monopoly" or "oligopoly" or "fragmented" or "unknown",
  "macro_exposure": "string describing key macro risks",
  "status": "green" or "yellow" or "red",
  "notes": "1-2 sentence rationale"
}

Thresholds for status:
- green: non-cyclical (or defensive) + growing demand + oligopoly/monopoly + low macro exposure
- red: highly cyclical + shrinking demand + fragmented + high macro exposure
- yellow: mixed signals

Note: cyclical industry lowers confidence but doesn't auto-disqualify.
If data cannot be found, use null and explain in notes.`

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name } = await req.json()
    const query = company_name ? `${ticker} (${company_name})` : ticker

    const raw = await analyzeWithClaude(
      SYSTEM_PROMPT,
      `Analyze the industry dynamics and macro risks for stock: ${query}. Consider cyclicality, demand trends, market structure, and global macro exposure.`
    )

    const data = parseJSON(raw)
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
