import { useEffect, useState, useCallback } from 'react';
import { Leaf, Layers, ShieldCheck, Cloud, DollarSign, RefreshCw, AlertCircle } from 'lucide-react';
import { useGreenVestStore } from './store/useGreenVestStore';
import { fetchHealth, fetchLandProfile, generateOptimizedPlan } from './services/api';
import { LandMap, PRESET_LOCATIONS } from './components/Map/LandMap';
import { LandProfileCard } from './components/Land/LandProfileCard';
import { SuitabilityLeaderboard } from './components/Suitability/SuitabilityLeaderboard';
import { DisqualificationDrawer } from './components/Suitability/DisqualificationDrawer';
import { CarbonProjectionChart } from './components/Carbon/CarbonProjectionChart';
import { FinancialAnalysisView } from './components/Financial/FinancialAnalysisView';
import { InvestorControls } from './components/Investor/InvestorControls';
import { AuditModal } from './components/Audit/AuditModal';
import type { Coordinate, PlantationStrategy, InvestorMode, Scenario } from './types';

export function App() {
  const {
    selectedCoordinate,
    landProfile,
    isLoadingProfile,
    profileError,
    investorMode,
    scenario,
    areaHectares,
    carbonPrice,
    discountRate,
    rankedStrategies,
    disqualifiedCandidates,
    selectedStrategy,
    isEvaluating,
    evaluationError,
    setSelectedCoordinate,
    setLandProfile,
    setIsLoadingProfile,
    setProfileError,
    setInvestorMode,
    setScenario,
    setAreaHectares,
    setCarbonPrice,
    setDiscountRate,
    setRankedStrategies,
    setDisqualifiedCandidates,
    setSelectedStrategy,
    setIsEvaluating,
    setEvaluationError,
  } = useGreenVestStore();

  const [backendStatus, setBackendStatus] = useState<'checking' | 'healthy' | 'offline'>('checking');
  const [backendMeta, setBackendMeta] = useState<{ version?: string; environment?: string }>({});
  const [activeDetailTab, setActiveDetailTab] = useState<'carbon' | 'financial'>('carbon');
  const [auditModalStrategy, setAuditModalStrategy] = useState<PlantationStrategy | null>(null);

  // 1. Initial Health Check
  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setBackendStatus('healthy');
        setBackendMeta({
          version: data.version as string,
          environment: data.environment as string,
        });
      })
      .catch(() => {
        setBackendStatus('offline');
      });
  }, []);

  // 2. Optimization Pipeline Trigger
  const runOptimizationPipeline = useCallback(
    async (
      coord: Coordinate,
      mode: InvestorMode,
      sc: Scenario,
      area: number,
      discRate: number,
      cPrice: number
    ) => {
      setIsLoadingProfile(true);
      setIsEvaluating(true);
      setProfileError(null);
      setEvaluationError(null);

      try {
        // Step A: Acquire Canonical Land Profile
        const profile = await fetchLandProfile(coord.latitude, coord.longitude);
        setLandProfile(profile);
        setIsLoadingProfile(false);

        // Step B: Generate Multi-Objective Optimized Plan
        const plan = await generateOptimizedPlan(
          coord.latitude,
          coord.longitude,
          mode,
          sc,
          area,
          discRate,
          cPrice
        );

        setRankedStrategies(plan.ranked_strategies);
        setDisqualifiedCandidates(plan.disqualified_candidates);

        // Auto-select rank 1 strategy
        if (plan.ranked_strategies.length > 0) {
          setSelectedStrategy(plan.ranked_strategies[0]);
        } else {
          setSelectedStrategy(null);
        }
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Pipeline execution failed';
        setEvaluationError(msg);
        setProfileError(msg);
      } finally {
        setIsLoadingProfile(false);
        setIsEvaluating(false);
      }
    },
    [
      setIsLoadingProfile,
      setIsEvaluating,
      setProfileError,
      setEvaluationError,
      setLandProfile,
      setRankedStrategies,
      setDisqualifiedCandidates,
      setSelectedStrategy,
    ]
  );

  // 3. Coordinate Selection Handler
  const handleSelectCoordinate = (coord: Coordinate) => {
    setSelectedCoordinate(coord);
    runOptimizationPipeline(coord, investorMode, scenario, areaHectares, discountRate, carbonPrice);
  };

  // 4. Investor Mode Change Handler
  const handleSelectMode = (mode: InvestorMode) => {
    setInvestorMode(mode);
    if (selectedCoordinate) {
      runOptimizationPipeline(selectedCoordinate, mode, scenario, areaHectares, discountRate, carbonPrice);
    }
  };

  // 5. Scenario Change Handler
  const handleSelectScenario = (sc: Scenario) => {
    setScenario(sc);
    if (selectedCoordinate) {
      runOptimizationPipeline(selectedCoordinate, investorMode, sc, areaHectares, discountRate, carbonPrice);
    }
  };

  // 6. Sensitivity Sliders Handlers
  const handleUpdateCarbonPrice = (price: number) => {
    setCarbonPrice(price);
    if (selectedCoordinate) {
      runOptimizationPipeline(selectedCoordinate, investorMode, scenario, areaHectares, discountRate, price);
    }
  };

  const handleUpdateDiscountRate = (rate: number) => {
    setDiscountRate(rate);
    if (selectedCoordinate) {
      runOptimizationPipeline(selectedCoordinate, investorMode, scenario, areaHectares, rate, carbonPrice);
    }
  };

  const handleUpdateArea = (area: number) => {
    setAreaHectares(area);
    if (selectedCoordinate) {
      runOptimizationPipeline(selectedCoordinate, investorMode, scenario, area, discountRate, carbonPrice);
    }
  };

  // Auto-load default preset (Kerala Tropics) on initial load if none selected
  useEffect(() => {
    if (!selectedCoordinate) {
      const defaultPreset = PRESET_LOCATIONS[0].coord;
      setSelectedCoordinate(defaultPreset);
      runOptimizationPipeline(defaultPreset, investorMode, scenario, areaHectares, discountRate, carbonPrice);
    }
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col selection:bg-emerald-500/30 selection:text-emerald-300">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-emerald-400 via-green-300 to-emerald-200 bg-clip-text text-transparent">
                  GreenVest
                </span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                  MVP v0.1
                </span>
              </div>
              <p className="text-xs text-slate-400">Land-to-Carbon Intelligence & Investment Planner</p>
            </div>
          </div>

          {/* Backend Status Badge & Refresh */}
          <div className="flex items-center space-x-3">
            {selectedCoordinate && (
              <button
                type="button"
                onClick={() =>
                  runOptimizationPipeline(
                    selectedCoordinate,
                    investorMode,
                    scenario,
                    areaHectares,
                    discountRate,
                    carbonPrice
                  )
                }
                disabled={isEvaluating || isLoadingProfile}
                className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-slate-300 hover:text-white hover:border-slate-600 transition-all"
                title="Rerun Optimization Pipeline"
              >
                <RefreshCw className={`w-3.5 h-3.5 ${isEvaluating ? 'animate-spin text-emerald-400' : ''}`} />
                <span>Re-evaluate</span>
              </button>
            )}

            <div className="flex items-center space-x-2 text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 font-mono">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus === 'healthy'
                    ? 'bg-emerald-400 shadow-glow-green animate-pulse'
                    : backendStatus === 'checking'
                    ? 'bg-amber-400'
                    : 'bg-rose-500'
                }`}
              />
              <span className="text-slate-300">
                {backendStatus === 'healthy'
                  ? `API Active (v${backendMeta.version || '0.1.0'})`
                  : backendStatus === 'checking'
                  ? 'Connecting API...'
                  : 'API Offline'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Error Notification Banner if any */}
        {(profileError || evaluationError) && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 flex items-start space-x-3 text-xs text-rose-200">
            <AlertCircle className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div>
              <strong className="text-rose-300">Evaluation Warning: </strong>
              {profileError || evaluationError}
            </div>
          </div>
        )}

        {/* Top Grid: Left (Map + Telemetry) & Right (Investor Controls + Scope) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column (8 cols): Geospatial Land Selection & Telemetry */}
          <div className="lg:col-span-8 space-y-6">
            <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-emerald-400" />
                  <h2 className="text-xs uppercase font-semibold tracking-wider text-slate-300">
                    Geospatial Land Selection
                  </h2>
                </div>
                <span className="text-[11px] text-slate-400 font-mono">
                  Click map or pick preset to stream physical variables
                </span>
              </div>

              <LandMap
                selectedCoord={selectedCoordinate}
                onSelectCoord={handleSelectCoordinate}
                isLoading={isLoadingProfile}
              />
            </div>

            {/* Live Physical Land Profile Telemetry */}
            <LandProfileCard profile={landProfile} isLoading={isLoadingProfile} />

            {/* Disqualified Candidates Accordion */}
            <DisqualificationDrawer disqualified={disqualifiedCandidates} />
          </div>

          {/* Right Column (4 cols): Investor Controls & Scientific Summary */}
          <div className="lg:col-span-4 space-y-6">
            {/* Investor Mode & Risk Scenario Switcher */}
            <InvestorControls
              investorMode={investorMode}
              scenario={scenario}
              onSelectMode={handleSelectMode}
              onSelectScenario={handleSelectScenario}
              isEvaluating={isEvaluating}
            />

            {/* MVP Environmental Determinants Scope Card */}
            <div className="glass-card rounded-xl p-4 flex items-start space-x-3 border border-emerald-500/20 bg-emerald-950/20">
              <ShieldCheck className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-slate-300 leading-relaxed">
                <strong className="text-emerald-300">Strict Environmental Scope: </strong>
                Suitability is calculated strictly using <span className="text-emerald-200">Annual Rainfall</span>, <span className="text-emerald-200">Temperature</span>, and <span className="text-emerald-200">Soil pH</span> without synthetic fallback fabrications.
              </div>
            </div>

            {/* Scientific Transparency Overview */}
            <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3 text-xs">
              <h3 className="font-semibold text-slate-200 tracking-wider uppercase text-[11px]">
                Two-Stage Engine Architecture
              </h3>
              <ul className="space-y-2 text-slate-400 font-mono text-[11px]">
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">1.</span>
                  <span><strong>Hard Feasibility:</strong> Disqualifies outside RMIN/RMAX, TMIN/TMAX, PHMIN/PHMAX.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">2.</span>
                  <span><strong>Trapezoidal Tolerance:</strong> Continuous 0-100 score across available optimal ranges.</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">3.</span>
                  <span><strong>Biophysical Carbon:</strong> Sigmoidal AGB accumulation (IPCC Tier 1 AFOLU).</span>
                </li>
                <li className="flex items-start space-x-2">
                  <span className="text-emerald-400 font-bold">4.</span>
                  <span><strong>20-Yr DCF Modeling:</strong> Cash flows, NPV, IRR, and payback period.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Middle Section: Ranked Strategies Leaderboard */}
        <div className="space-y-6">
          <SuitabilityLeaderboard
            strategies={rankedStrategies}
            selectedStrategy={selectedStrategy}
            onSelectStrategy={setSelectedStrategy}
            onOpenAudit={(strat) => setAuditModalStrategy(strat)}
          />
        </div>

        {/* Bottom Section: Strategy Deep Dive (Carbon Trajectory + DCF Financial Waterfall) */}
        {selectedStrategy && (
          <div className="space-y-4">
            {/* View Switcher Tabs */}
            <div className="flex items-center space-x-3 border-b border-slate-800 pb-2">
              <span className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                Strategy Inspection:
              </span>
              <button
                type="button"
                onClick={() => setActiveDetailTab('carbon')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
                  activeDetailTab === 'carbon'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <Cloud className="w-3.5 h-3.5" />
                <span>20-Year Biophysical Carbon Trajectory</span>
              </button>
              <button
                type="button"
                onClick={() => setActiveDetailTab('financial')}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium flex items-center space-x-1.5 transition-all ${
                  activeDetailTab === 'financial'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 font-semibold'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                <DollarSign className="w-3.5 h-3.5" />
                <span>20-Year DCF Financial Waterfall</span>
              </button>
            </div>

            {/* Active Tab Panel */}
            {activeDetailTab === 'carbon' ? (
              <CarbonProjectionChart
                projection={selectedStrategy.carbon_projection}
                commonName={selectedStrategy.common_name}
              />
            ) : (
              <FinancialAnalysisView
                metrics={selectedStrategy.financial_metrics}
                commonName={selectedStrategy.common_name}
                carbonPrice={carbonPrice}
                discountRate={discountRate}
                areaHectares={areaHectares}
                onUpdateCarbonPrice={handleUpdateCarbonPrice}
                onUpdateDiscountRate={handleUpdateDiscountRate}
                onUpdateArea={handleUpdateArea}
              />
            )}
          </div>
        )}
      </main>

      {/* Explainability Audit Modal */}
      <AuditModal
        strategy={auditModalStrategy}
        onClose={() => setAuditModalStrategy(null)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 mt-12 py-6 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
          <div>
            <span className="font-semibold text-slate-300">GreenVest Intelligence Engine</span> — Land-to-Carbon Intelligence & Investment Planner.
          </div>
          <div className="text-[11px] font-mono text-slate-400">
            Open-Meteo Reanalysis • ISRIC SoilGrids v2.0 • FAO ECOCROP • IPCC 2006 AFOLU
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
