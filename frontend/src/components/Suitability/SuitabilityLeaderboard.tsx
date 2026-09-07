import React from 'react';
import { Award, ChevronRight, Trees, Leaf, DollarSign, Cloud, Info } from 'lucide-react';
import type { PlantationStrategy } from '../../types';

interface SuitabilityLeaderboardProps {
  strategies: PlantationStrategy[];
  selectedStrategy: PlantationStrategy | null;
  onSelectStrategy: (strategy: PlantationStrategy) => void;
  onOpenAudit: (strategy: PlantationStrategy) => void;
}

export const SuitabilityLeaderboard: React.FC<SuitabilityLeaderboardProps> = ({
  strategies,
  selectedStrategy,
  onSelectStrategy,
  onOpenAudit,
}) => {
  if (!strategies || strategies.length === 0) {
    return (
      <div className="glass-panel rounded-2xl p-8 border border-slate-800 text-center flex flex-col items-center justify-center space-y-2">
        <Trees className="w-10 h-10 text-slate-600 mb-2" />
        <h4 className="text-base font-medium text-slate-300">No Plantation Strategies Generated Yet</h4>
        <p className="text-xs text-slate-400 max-w-md">
          Select a land coordinate to stream environmental telemetry and trigger multi-objective plantation optimization.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <Award className="w-4 h-4 text-emerald-400" />
            <span>Optimal Plantation Strategies</span>
          </h3>
          <p className="text-xs text-slate-400">Ranked by multi-objective GreenVest score across Investor Mode preferences</p>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-300">
          {strategies.length} Feasible Candidates
        </span>
      </div>

      {/* Strategies List */}
      <div className="space-y-2.5">
        {strategies.map((strat) => {
          const isSelected = selectedStrategy?.crop_id === strat.crop_id;
          const score = strat.greenvest_score;
          const envScore = strat.suitability.suitability?.environmental_score ?? 0;
          const carbonTotal = strat.carbon_projection?.cumulative_20yr_co2e_t_ha ?? 0;
          const npv = strat.financial_metrics?.npv_usd_ha ?? 0;

          return (
            <div
              key={strat.crop_id}
              onClick={() => onSelectStrategy(strat)}
              className={`p-4 rounded-xl border transition-all cursor-pointer relative overflow-hidden flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                isSelected
                  ? 'bg-slate-900/90 border-emerald-500/80 shadow-lg shadow-emerald-500/10'
                  : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60'
              }`}
            >
              {/* Left Column: Rank + Name + Badges */}
              <div className="flex items-start space-x-3.5">
                {/* Rank Badge */}
                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center font-mono font-bold text-sm flex-shrink-0 ${
                    strat.rank === 1
                      ? 'bg-gradient-to-br from-amber-400 to-amber-600 text-slate-950 shadow-md shadow-amber-500/20'
                      : strat.rank === 2
                      ? 'bg-gradient-to-br from-slate-300 to-slate-400 text-slate-950'
                      : strat.rank === 3
                      ? 'bg-gradient-to-br from-amber-700 to-amber-800 text-white'
                      : 'bg-slate-800 text-slate-300'
                  }`}
                >
                  #{strat.rank}
                </div>

                <div>
                  <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                    <h4 className="font-semibold text-white text-sm tracking-tight">{strat.common_name}</h4>
                    <span className="text-xs text-slate-400 italic font-serif">({strat.scientific_name})</span>
                    {strat.use_category && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-mono">
                        {strat.use_category}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3 text-xs text-slate-400 mt-1 font-mono">
                    <span className="flex items-center space-x-1">
                      <Leaf className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Suitability: <strong className="text-slate-200">{envScore}%</strong></span>
                    </span>
                    <span>•</span>
                    <span className="flex items-center space-x-1">
                      <Cloud className="w-3.5 h-3.5 text-sky-400" />
                      <span>Carbon: <strong className="text-slate-200">{carbonTotal.toFixed(0)} t/ha</strong></span>
                    </span>
                    <span>•</span>
                    <span className="flex items-center space-x-1">
                      <DollarSign className="w-3.5 h-3.5 text-amber-400" />
                      <span>NPV: <strong className="text-slate-200">${npv.toLocaleString()}</strong></span>
                    </span>
                  </div>
                </div>
              </div>

              {/* Right Column: GreenVest Score + Actions */}
              <div className="flex items-center space-x-4 self-end md:self-center">
                {/* Audit Button */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onOpenAudit(strat);
                  }}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-300 hover:bg-slate-800 transition-all text-xs flex items-center space-x-1"
                  title="View Explainability Audit Log"
                >
                  <Info className="w-4 h-4" />
                  <span className="hidden sm:inline">Audit</span>
                </button>

                {/* Score Pill */}
                <div className="text-right flex flex-col items-end">
                  <div className="flex items-baseline space-x-1 font-mono">
                    <span
                      className={`text-xl font-black ${
                        score >= 80
                          ? 'text-emerald-400'
                          : score >= 60
                          ? 'text-green-400'
                          : score >= 40
                          ? 'text-amber-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {score.toFixed(1)}
                    </span>
                    <span className="text-[10px] text-slate-500">/100</span>
                  </div>
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">GreenVest Score</span>
                </div>

                <ChevronRight
                  className={`w-5 h-5 transition-transform ${
                    isSelected ? 'text-emerald-400 translate-x-1' : 'text-slate-600'
                  }`}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default SuitabilityLeaderboard;
