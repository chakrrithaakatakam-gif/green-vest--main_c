import { create } from 'zustand';
import type {
  Coordinate,
  LandProfile,
  PlantationStrategy,
  PlantEvaluationResult,
  InvestorMode,
  Scenario,
} from '../types';

interface GreenVestState {
  // Map & Land State
  selectedCoordinate: Coordinate | null;
  landProfile: LandProfile | null;
  isLoadingProfile: boolean;
  profileError: string | null;

  // Evaluation & Optimization State
  investorMode: InvestorMode;
  scenario: Scenario;
  areaHectares: number;
  carbonPrice: number;
  discountRate: number;

  rankedStrategies: PlantationStrategy[];
  disqualifiedCandidates: PlantEvaluationResult[];
  selectedStrategy: PlantationStrategy | null;
  isEvaluating: boolean;
  evaluationError: string | null;

  // Actions
  setSelectedCoordinate: (coord: Coordinate) => void;
  setLandProfile: (profile: LandProfile | null) => void;
  setIsLoadingProfile: (loading: boolean) => void;
  setProfileError: (error: string | null) => void;

  setInvestorMode: (mode: InvestorMode) => void;
  setScenario: (scenario: Scenario) => void;
  setAreaHectares: (area: number) => void;
  setCarbonPrice: (price: number) => void;
  setDiscountRate: (rate: number) => void;

  setRankedStrategies: (strategies: PlantationStrategy[]) => void;
  setDisqualifiedCandidates: (disqualified: PlantEvaluationResult[]) => void;
  setSelectedStrategy: (strategy: PlantationStrategy | null) => void;
  setIsEvaluating: (evaluating: boolean) => void;
  setEvaluationError: (error: string | null) => void;
  resetPlan: () => void;
}

export const useGreenVestStore = create<GreenVestState>((set) => ({
  selectedCoordinate: null,
  landProfile: null,
  isLoadingProfile: false,
  profileError: null,

  investorMode: 'balanced',
  scenario: 'expected',
  areaHectares: 5.0,
  carbonPrice: 20.0,
  discountRate: 0.08,

  rankedStrategies: [],
  disqualifiedCandidates: [],
  selectedStrategy: null,
  isEvaluating: false,
  evaluationError: null,

  setSelectedCoordinate: (coord) => set({ selectedCoordinate: coord }),
  setLandProfile: (profile) => set({ landProfile: profile, profileError: null }),
  setIsLoadingProfile: (loading) => set({ isLoadingProfile: loading }),
  setProfileError: (error) => set({ profileError: error, isLoadingProfile: false }),

  setInvestorMode: (mode) => set({ investorMode: mode }),
  setScenario: (scenario) => set({ scenario }),
  setAreaHectares: (area) => set({ areaHectares: area }),
  setCarbonPrice: (price) => set({ carbonPrice: price }),
  setDiscountRate: (rate) => set({ discountRate: rate }),

  setRankedStrategies: (strategies) => set({ rankedStrategies: strategies }),
  setDisqualifiedCandidates: (disqualified) => set({ disqualifiedCandidates: disqualified }),
  setSelectedStrategy: (strategy) => set({ selectedStrategy: strategy }),
  setIsEvaluating: (evaluating) => set({ isEvaluating: evaluating }),
  setEvaluationError: (error) => set({ evaluationError: error, isEvaluating: false }),
  resetPlan: () =>
    set({
      rankedStrategies: [],
      disqualifiedCandidates: [],
      selectedStrategy: null,
      evaluationError: null,
    }),
}));
