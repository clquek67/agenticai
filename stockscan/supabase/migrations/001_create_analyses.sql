create table analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users,
  ticker text not null,
  company_name text,
  created_at timestamptz default now(),
  stage1_business jsonb,
  stage2_financials jsonb,
  stage3_valuation jsonb,
  stage4_promoter jsonb,
  stage5_industry jsonb,
  final_verdict text,
  final_summary text
);

alter table analyses enable row level security;

create policy "Users can view their own analyses"
  on analyses for select
  using (auth.uid() = user_id or user_id is null);

create policy "Users can insert their own analyses"
  on analyses for insert
  with check (auth.uid() = user_id or user_id is null);
