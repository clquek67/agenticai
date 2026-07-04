import { NextRequest, NextResponse } from 'next/server'
import { analyzeWithClaude, parseJSON } from '@/lib/claude'

const SYSTEM_PROMPT = `You are a financial analyst. Given a stock ticker or company name, use web search to research the company. Return ONLY valid JSON, no other text, no markdown fences, matching this exact schema:
{
  "answers": {
    "what_it_does": "string describing the company's business",
    "revenue_model": "string describing how it makes money",
    "moat": "string describing competitive advantage or 'No clear moat'",
    "industry": "string with the industry/sector",
    "leadership": "string with CEO and key executives"
  },
  "notes": "1-2 sentence summary of business quality and moat strength"
}`

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name } = await req.json()
    const query = company_name ? `${ticker} (${company_name})` : ticker

    const raw = await analyzeWithClaude(
      SYSTEM_PROMPT,
      `Analyze the business fundamentals for stock: ${query}`
    )

    const data = parseJSON(raw)
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
