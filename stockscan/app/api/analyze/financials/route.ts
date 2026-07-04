import { NextRequest, NextResponse } from 'next/server'
import { analyzeWithClaude, parseJSON } from '@/lib/claude'

const SYSTEM_PROMPT = `You are a financial analyst. Given a stock ticker or company name, use web search to find the most recent available financial data. Return ONLY valid JSON, no other text, no markdown fences, matching this exact schema:
{
  "roe_percent": number or null,
  "debt_to_equity": number or null,
  "net_profit_margin_percent": number or null,
  "quick_ratio": number or null,
  "interest_coverage_ratio": number or null,
  "revenue_trend": "growing" or "flat" or "declining" or "unknown",
  "status": "green" or "yellow" or "red",
  "notes": "1-2 sentence rationale"
}

Thresholds for status:
- green: ROE > 15% AND D/E < 1 AND net margin > 15% and stable
- red: ROE < 10% OR D/E > 2 OR net margin < 5% OR declining revenue
- yellow: anything in between

If data cannot be found, use null and explain in notes.`

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name } = await req.json()
    const query = company_name ? `${ticker} (${company_name})` : ticker

    const raw = await analyzeWithClaude(
      SYSTEM_PROMPT,
      `Find and analyze the financial metrics for stock: ${query}. Look for ROE, debt-to-equity ratio, net profit margin, quick ratio, interest coverage ratio, and revenue trend from recent annual reports or financial data.`
    )

    const data = parseJSON(raw)
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
