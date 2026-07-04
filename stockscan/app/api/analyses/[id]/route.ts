import { NextRequest, NextResponse } from 'next/server'
import { createServiceClient } from '@/lib/supabase'

export const dynamic = 'force-dynamic'

export async function PATCH(req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const body = await req.json()
    const supabase = createServiceClient()

    const update: Record<string, unknown> = {}
    if (body.stage1 !== undefined) update.stage1_business = body.stage1
    if (body.stage2 !== undefined) update.stage2_financials = body.stage2
    if (body.stage3 !== undefined) update.stage3_valuation = body.stage3
    if (body.stage4 !== undefined) update.stage4_promoter = body.stage4
    if (body.stage5 !== undefined) update.stage5_industry = body.stage5
    if (body.verdict !== undefined) update.final_verdict = body.verdict
    if (body.final_summary !== undefined) update.final_summary = body.final_summary
    if (body.company_name !== undefined) update.company_name = body.company_name

    const { data, error } = await supabase
      .from('analyses')
      .update(update)
      .eq('id', params.id)
      .select()
      .single()

    if (error) throw error
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}

export async function GET(_req: NextRequest, { params }: { params: { id: string } }) {
  try {
    const supabase = createServiceClient()
    const { data, error } = await supabase
      .from('analyses')
      .select('*')
      .eq('id', params.id)
      .single()

    if (error) throw error
    return NextResponse.json(data)
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 })
  }
}
