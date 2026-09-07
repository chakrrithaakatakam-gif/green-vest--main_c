export interface Coordinate {
  latitude: number;
  longitude: number;
}

export interface ClimateData {
  annual_rainfall_mm: number | null;
  mean_temperature_c: number | null;
  min_temperature_c: number | null;
  max_temperature_c: number | null;
  source: string;
  status: 'available' | 'unavailable';
  confidence_score: number;
  error_message?: string | null;
}

export interface SoilData {
  ph: number | null;
  source: string;
  status: 'available' | 'unavailable';
  confidence_score: number;
  error_message?: string | null;
}

export interface LandProfile {
  latitude: number;
  longitude: number;
  climate: ClimateData;
  soil: SoilData;
  composite_data_confidence: number;
  evaluated_at?: string | null;
}

export interface PlantRequirement {
  crop_id: number;
  scientific_name: string;
  common_name: string;
  use_category?: string | null;
  life_form?: string | null;
  growth_cycle_days_min?: number | null;
  growth_cycle_days_max?: number | null;
  rainfall_min: number;
  rainfall_max: number;
  temp_min: number;
  temp_max: number;
  ph_min: number;
  ph_max: number;
  rainfall_opt_min?: number | null;
  rainfall_opt_max?: number | null;
  temp_opt_min?: number | null;
  temp_opt_max?: number | null;
  ph_opt_min?: number | null;
  ph_opt_max?: number | null;
  has_complete_optimal_ranges: boolean;
  source: string;
}

export interface PlantSummary {
  crop_id: number;
  scientific_name: string;
  common_name: string;
  use_category?: string | null;
  life_form?: string | null;
  rainfall_range: string;
  temp_range: string;
  ph_range: string;
  has_complete_optimal_ranges: boolean;
}

export interface PlantListResponse {
  total_count: number;
  limit: number;
  offset: number;
  plants: PlantSummary[];
}

export interface PlantCarbonProfile {
  crop_id: number;
  scientific_name: string;
  common_name: string;
  max_above_ground_biomass_t_ha: number;
  growth_rate_k: number;
  inflection_year_t0: number;
  root_to_shoot_ratio: number;
  carbon_fraction: number;
  data_source: string;
  is_assumption: boolean;
  is_species_specific: boolean;
  confidence_rating: number;
}

export interface CarbonYearPoint {
  year: number;
  above_ground_biomass_t_ha: number;
  total_biomass_t_ha: number;
  carbon_stock_t_ha: number;
  cumulative_co2e_t_ha: number;
  annual_co2e_increment_t_ha: number;
}

export interface CarbonProjection {
  crop_id: number;
  scientific_name: string;
  time_horizon_years: number;
  cumulative_20yr_co2e_t_ha: number;
  mean_annual_co2e_t_ha: number;
  trajectory: CarbonYearPoint[];
  is_modeled_estimate: boolean;
  disclaimer: string;
  confidence_rating: number;
}

export interface ParameterSuitability {
  parameter_name: 'rainfall' | 'temperature' | 'ph';
  measured_value: number | null;
  min_bound: number;
  opt_min: number | null;
  opt_max: number | null;
  max_bound: number;
  sub_score: number | null;
  status: 'optimal' | 'marginal' | 'infeasible' | 'unevaluable';
  is_evaluable: boolean;
  explanation: string;
}

export interface FeasibilityResult {
  is_feasible: boolean;
  failure_reasons: string[];
}

export interface SuitabilityScore {
  environmental_score: number;
  data_completeness_pct: number;
  parameters: Record<string, ParameterSuitability>;
}

export interface PlantEvaluationResult {
  plant: PlantRequirement;
  feasibility: FeasibilityResult;
  suitability?: SuitabilityScore | null;
  data_confidence_rating: number;
  audit_notes: string[];
}

export interface SuitabilityEvaluationResponse {
  feasible_plants: PlantEvaluationResult[];
  disqualified_plants: PlantEvaluationResult[];
  total_evaluated: number;
  total_feasible: number;
  total_disqualified: number;
}

export interface AnnualCashFlow {
  year: number;
  capex_usd_ha: number;
  opex_usd_ha: number;
  yield_revenue_usd_ha: number;
  carbon_revenue_usd_ha: number;
  net_cash_flow_usd_ha: number;
  discounted_cash_flow_usd_ha: number;
  cumulative_cash_flow_usd_ha: number;
}

export interface FinancialMetrics {
  time_horizon_years: number;
  npv_usd_ha: number;
  irr_pct?: number | null;
  roi_pct: number;
  payback_period_years?: number | null;
  discounted_payback_years?: number | null;
  total_net_cash_flow_usd_ha: number;
  cash_flows: AnnualCashFlow[];
  is_modeled_assumption: boolean;
  disclaimer: string;
}

export interface RiskAssessment {
  composite_risk_penalty: number;
  climate_risk_score: number;
  data_uncertainty_score: number;
  market_risk_score: number;
  risk_factors: string[];
}

export interface AuditTrail {
  strengths: string[];
  constraints: string[];
  risk_flags: string[];
  completeness_notes: string[];
}

export interface PlantationStrategy {
  rank: number;
  crop_id: number;
  scientific_name: string;
  common_name: string;
  use_category?: string | null;
  life_form?: string | null;
  suitability: PlantEvaluationResult;
  carbon_projection?: CarbonProjection | null;
  financial_metrics?: FinancialMetrics | null;
  risk_assessment: RiskAssessment;
  greenvest_score: number;
  score_breakdown: Record<string, number>;
  audit_trail: AuditTrail;
}

export interface GreenVestPlan {
  land_profile: LandProfile;
  investor_mode: 'carbon_first' | 'return_first' | 'balanced';
  scenario: 'conservative' | 'expected' | 'optimistic';
  area_hectares: number;
  ranked_strategies: PlantationStrategy[];
  disqualified_candidates: PlantEvaluationResult[];
  total_evaluated_plants: number;
  total_feasible_plants: number;
  total_disqualified_plants: number;
  generated_at: string;
}

export type InvestorMode = 'carbon_first' | 'return_first' | 'balanced';
export type Scenario = 'conservative' | 'expected' | 'optimistic';
