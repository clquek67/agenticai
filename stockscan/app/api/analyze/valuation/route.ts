import { NextRequest, NextResponse } from 'next/server'
import { analyzeWithClaude, parseJSON } from '@/lib/claude'

const SYSTEM_PROMPT = `You are a financial analyst. Given a stock ticker or company name, use web search to find the most recent valuation metrics. Return ONLY valid JSON, no other text, no markdown fences, matching this exact schema:
{
  "pe_ratio": number or null,
  "industry_pe_avg": number or null,
  "peg_ratio": number or null,
  "ev_ebitda": number or null,
  "industry_ev_ebitda_avg": number or null,
  "price_to_book": number or null,
  "dividend_yield_percent": number or null,
  "status": "green" or "yellow" or "red",
  "notes": "1-2 sentence rationale"
}

Thresholds for status:
- green: P/E <= industry avg AND PEG < 2 AND EV/EBITDA <= industry avg
- red: P/E > 30 or significantly above industry AND PEG > 3
- yellow: P/E between 20-30 or mildly above industry, PEG 2-3

Flag if P/E > 20 as a caution even if green. If data cannot be found, use null and explain in notes.`

export async function POST(req: NextRequest) {
  try {
    const { ticker, company_name } = await req.json()
    const query = company_name ? `${ticker} (${company_name})` : ticker

    const raw = await analyzeWithClaude(
      SYSTEM_PROMPT,
      `Find and analyze the valuation metrics for stock: ${query}. Look for P/E ratio, industry P/E average, PEG ratio, EV/EBITDA, price-to-book, and dividend yield.`
    )

    const data = parseJSON(raw)
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
