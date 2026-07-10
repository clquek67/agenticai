// Hand-written types for the Phase 1 schema (supabase/migrations/0001_init.sql).
// If you later run `supabase gen types typescript` against the dedicated
// instance, the generated file can replace this one.

export type Industry =
  | 'healthcare'
  | 'government'
  | 'aviation'
  | 'financial_services'
  | 'technology'
  | 'manufacturing'
  | 'energy_utilities'
  | 'telecommunications'
  | 'retail_ecommerce'
  | 'logistics_transport'
  | 'education'
  | 'insurance'
  | 'pharma_biotech'
  | 'media_entertainment'
  | 'real_estate_construction'
  | 'agriculture'
  | 'hospitality_travel'
  | 'legal_professional_services'
  | 'defense'
  | 'maritime'
  | 'other';

export type Region = 'asean' | 'korea' | 'eu' | 'us' | 'global';

export type Framework =
  | 'nist_ai_rmf'
  | 'iso_42001'
  | 'owasp_llm'
  | 'eu_ai_act'
  | 'gdpr_ai'
  | 'mas_trm'
  | 'imda_model_ai'
  | 'korea_ai_act'
  | 'pdpa'
  | 'pipa'
  | 'us_state_ai'
  | 'hipaa_ai'
  | 'critical_infra'
  | 'gxp_ai';

export type AssessmentStatus = 'draft' | 'in_progress' | 'completed';

export type Answer = 'yes' | 'partial' | 'no' | 'not_applicable';

export type Applicability = 'core' | 'regulatory' | 'sector' | 'certification';

export type Criticality = 'medium' | 'high' | 'critical';

export interface Organization {
  id: string;
  name: string;
  industry: Industry;
  region: Region;
  created_at: string;
  user_id: string;
}

export interface Assessment {
  id: string;
  organization_id: string;
  framework: Framework;
  status: AssessmentStatus;
  overall_score: number | null;
  started_at: string;
  completed_at: string | null;
}

export interface Control {
  id: string;
  framework: Framework;
  category: string;
  title: string;
  description: string;
  weight: number;
  /** Sparse map — industries not listed default to "medium". */
  industry_criticality: Partial<Record<Industry, Criticality>>;
}

export interface Response {
  id: string;
  assessment_id: string;
  control_id: string;
  answer: Answer;
  evidence_notes: string | null;
  updated_at: string;
}

export interface Report {
  id: string;
  assessment_id: string;
  generated_markdown: string | null;
  ai_summary: string | null;
  created_at: string;
}

export interface FrameworkApplicability {
  id: string;
  framework: Framework;
  industry: string | null;
  region: string | null;
  applicability: Applicability;
  rationale: string;
}

export interface Database {
  public: {
    Tables: {
      organizations: {
        Row: Organization;
        Insert: Omit<Organization, 'id' | 'created_at'> &
          Partial<Pick<Organization, 'id' | 'created_at'>>;
        Update: Partial<Organization>;
        Relationships: [];
      };
      assessments: {
        Row: Assessment;
        Insert: Omit<Assessment, 'id' | 'status' | 'overall_score' | 'started_at' | 'completed_at'> &
          Partial<Assessment>;
        Update: Partial<Assessment>;
        Relationships: [];
      };
      controls: {
        Row: Control;
        Insert: Control;
        Update: Partial<Control>;
        Relationships: [];
      };
      responses: {
        Row: Response;
        Insert: Omit<Response, 'id' | 'updated_at'> & Partial<Pick<Response, 'id' | 'updated_at'>>;
        Update: Partial<Response>;
        Relationships: [];
      };
      reports: {
        Row: Report;
        Insert: Omit<Report, 'id' | 'created_at'> & Partial<Pick<Report, 'id' | 'created_at'>>;
        Update: Partial<Report>;
        Relationships: [];
      };
      framework_applicability: {
        Row: FrameworkApplicability;
        Insert: Omit<FrameworkApplicability, 'id'> & Partial<Pick<FrameworkApplicability, 'id'>>;
        Update: Partial<FrameworkApplicability>;
        Relationships: [];
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: {
      industry_type: Industry;
      region_type: Region;
      framework_type: Framework;
      assessment_status: AssessmentStatus;
      answer_type: Answer;
      applicability_type: Applicability;
    };
    CompositeTypes: Record<string, never>;
  };
}
