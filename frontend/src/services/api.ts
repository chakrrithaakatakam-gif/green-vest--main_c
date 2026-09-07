import type {
  LandProfile,
  PlantListResponse,
  SuitabilityEvaluationResponse,
  GreenVestPlan,
  InvestorMode,
  Scenario,
} from '../types';

const API_BASE = '/api/v1';

export async function fetchHealth(): Promise<Record<string, unknown>> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchLandProfile(latitude: number, longitude: number): Promise<LandProfile> {
  const res = await fetch(`${API_BASE}/land/profile`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latitude, longitude }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch land profile (${res.status})`);
  }
  const data = await res.json();
  return data.profile;
}

export async function fetchPlants(
  limit = 50,
  offset = 0,
  category?: string
): Promise<PlantListResponse> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  if (category) params.append('category', category);

  const res = await fetch(`${API_BASE}/plants?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to load plants: ${res.statusText}`);
  return res.json();
}

export async function evaluateSuitability(
  landProfile: LandProfile,
  topK = 20
): Promise<SuitabilityEvaluationResponse> {
  const res = await fetch(`${API_BASE}/suitability/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ land_profile: landProfile, top_k: topK }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Suitability evaluation failed (${res.status})`);
  }
  return res.json();
}

export async function generateOptimizedPlan(
  latitude: number,
  longitude: number,
  investorMode: InvestorMode,
  scenario: Scenario,
  areaHectares = 5.0,
  customDiscountRate?: number,
  customCarbonPrice?: number
): Promise<GreenVestPlan> {
  const res = await fetch(`${API_BASE}/plan/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      latitude,
      longitude,
      investor_mode: investorMode,
      scenario,
      area_hectares: areaHectares,
      custom_discount_rate: customDiscountRate,
      custom_carbon_price: customCarbonPrice,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Plan optimization failed (${res.status})`);
  }
  const data = await res.json();
  return data.plan;
}
