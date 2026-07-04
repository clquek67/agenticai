import { NextRequest, NextResponse } from 'next/server'
import { analyzeWithClaude, parseJSON } from '@/lib/claude'

const SYSTEM_PROMPT = `You are a financial analyst. Given a stock ticker or company name, use web search to find promoter and institutional holding data. Return ONLY valid JSON, no other text, no markdown fences, matching this exact schema:
{
  "promoter_holding_pct": number or null,
  "pledging_pct": number or null,
  "institutional_holding_pct": number or null,
  "insider_trend": "buying" or "selling" or "neutral" or "unknown",
  "status": "green" or "yellow" or "red",
  "notes": "1-2 sentence rationale"
}

Thresholds for status:
- green: promoter holding > 50%, pledging < 5%, institutions present, insiders buying/neutral
- red: pledging > 25% (forced-selling risk, red flag regardless of other metrics) OR promoter holding < 20%
- yellow: pledging 5-25%, promoter holding 20-50%, or insiders selling

If this is a US stock without traditional promoter structure, note that and assess major shareholder/insider ownership instead.
If data cannot be found, use null and explain in notes.`

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name } = await req.json()
    const query = company_name ? `${ticker} (${company_name})` : ticker

    const raw = await analyzeWithClaude(
      SYSTEM_PROMPT,
      `Find promoter holding, pledging percentage, institutional holding, and insider trading trends for stock: ${query}.`
    )

    const data = parseJSON(raw)
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
