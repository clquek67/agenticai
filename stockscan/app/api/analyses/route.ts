import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const supabase = createServiceClient()

    const { data, error } = await supabase
      .from('analyses')
      .insert({
        user_id: body.user_id || null,
        ticker: body.ticker,
        company_name: body.company_name,
        stage1_business: body.stage1,
        stage2_financials: body.stage2,
        stage3_valuation: body.stage3,
        stage4_promoter: body.stage4,
        stage5_industry: body.stage5,
        final_verdict: body.verdict,
        final_summary: body.final_summary,
      })
      .select()
      .single()

    if (error) throw error
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function GET(req: NextRequest) {
  try {
    const supabase = createServiceClient()
    const { searchParams } = new URL(req.url)
    const verdict = searchParams.get('verdict')

    let query = supabase
      .from('analyses')
      .select('id, ticker, company_name, created_at, final_verdict, final_summary')
      .order('created_at', { ascending: false })
      .limit(50)

    if (verdict) {
      query = query.eq('final_verdict', verdict)
    }

    const { data, error } = await query
    if (error) throw error
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
