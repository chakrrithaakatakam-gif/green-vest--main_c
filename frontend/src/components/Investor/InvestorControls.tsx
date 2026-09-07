import React from 'react';
import { Sliders } from 'lucide-react';
import type { InvestorMode, Scenario } from '../../types';

interface InvestorControlsProps {
  investorMode: InvestorMode;
  scenario: Scenario;
  onSelectMode: (mode: InvestorMode) => void;
  onSelectScenario: (scenario: Scenario) => void;
  isEvaluating: boolean;
}

export const InvestorControls: React.FC<InvestorControlsProps> = ({
  investorMode,
  scenario,
  onSelectMode,
  onSelectScenario,
  isEvaluating,
}) => {
  const modeConfigs = {
    carbon_first: {
      label: 'Carbon-First',
      desc: 'Maximizes 20-yr biophysical carbon sequestration.',
      weights: { suit: 35, carbon: 45, fin: 10, risk: 10 },
      color: 'from-emerald-500 to-green-600',
    },
    return_first: {
      label: 'Return-First',
      desc: 'Maximizes discounted commercial yield & cash flow returns.',
      weights: { suit: 25, carbon: 15, fin: 50, risk: 10 },
      color: 'from-amber-500 to-yellow-600',
    },
    balanced: {
      label: 'Balanced',
      desc: 'Optimizes dual-objective carbon accumulation & financial returns.',
      weights: { suit: 35, carbon: 25, fin: 25, risk: 15 },
      color: 'from-sky-500 to-indigo-600',
    },
  };

  const currentConfig = modeConfigs[investorMode];

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
          <Sliders className="w-4 h-4 text-emerald-400" />
          <span>Investor Objective & Risk Scenario</span>
        </h3>
        {isEvaluating && (
          <span className="text-[11px] text-emerald-400 font-mono animate-pulse">
            Optimizing...
          </span>
        )}
      </div>

      {/* Mode Buttons */}
      <div className="space-y-2">
        <label className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider block">
          Investor Strategy Mode
        </label>
        <div className="grid grid-cols-3 gap-2">
          {(['carbon_first', 'return_first', 'balanced'] as const).map((m) => {
            const isSelected = investorMode === m;
            const cfg = modeConfigs[m];
            return (
              <button
                key={m}
                type="button"
                onClick={() => onSelectMode(m)}
                disabled={isEvaluating}
                className={`py-2.5 px-3 rounded-xl border transition-all text-left flex flex-col justify-between ${
                  isSelected
                    ? 'bg-slate-900 border-emerald-500/80 shadow-md shadow-emerald-500/10'
                    : 'bg-slate-900/40 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60'
                }`}
              >
                <div className="flex items-center justify-between w-full">
                  <span
                    className={`text-xs font-semibold ${
                      isSelected ? 'text-emerald-300' : 'text-slate-300'
                    }`}
                  >
                    {cfg.label}
                  </span>
                  {isSelected && (
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-glow-green" />
                  )}
                </div>
              </button>
            );
          })}
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed italic">
          {currentConfig.desc}
        </p>
      </div>

      {/* Multi-Objective Weight Distribution Bar */}
      <div className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
          <span>Objective Weighting:</span>
          <span className="text-slate-300">
            Suitability: {currentConfig.weights.suit}% | Carbon: {currentConfig.weights.carbon}% | Fin: {currentConfig.weights.fin}% | Risk: -{currentConfig.weights.risk}%
          </span>
        </div>
        <div className="w-full h-2 rounded-full overflow-hidden flex bg-slate-800">
          <div
            style={{ width: `${currentConfig.weights.suit}%` }}
            className="bg-emerald-500 transition-all duration-300"
            title={`Suitability ${currentConfig.weights.suit}%`}
          />
          <div
            style={{ width: `${currentConfig.weights.carbon}%` }}
            className="bg-sky-500 transition-all duration-300"
            title={`Carbon ${currentConfig.weights.carbon}%`}
          />
          <div
            style={{ width: `${currentConfig.weights.fin}%` }}
            className="bg-amber-500 transition-all duration-300"
            title={`Financial ${currentConfig.weights.fin}%`}
          />
          <div
            style={{ width: `${currentConfig.weights.risk}%` }}
            className="bg-rose-500 transition-all duration-300"
            title={`Risk Penalty -${currentConfig.weights.risk}%`}
          />
        </div>
      </div>

      {/* Risk Scenario Switcher */}
      <div className="space-y-2 pt-2 border-t border-slate-800/80">
        <div className="flex items-center justify-between">
          <label className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">
            Risk & Macro Scenario
          </label>
          <span className="text-[10px] text-slate-500 font-mono">Stress Test</span>
        </div>
        <div className="grid grid-cols-3 gap-2">
          {(['conservative', 'expected', 'optimistic'] as const).map((sc) => {
            const isSelected = scenario === sc;
            return (
              <button
                key={sc}
                type="button"
                onClick={() => onSelectScenario(sc)}
                disabled={isEvaluating}
                className={`py-1.5 text-xs font-medium rounded-lg border capitalize transition-all ${
                  isSelected
                    ? 'bg-slate-900 border-emerald-500 text-emerald-300 font-semibold shadow-sm'
                    : 'bg-slate-900/40 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                {sc}
              </button>
            );
          })}
        </div>
        <div className="text-[10px] font-mono text-slate-400">
          {scenario === 'conservative' && 'Price -20%, Yield -15%, Discount Rate +2%'}
          {scenario === 'expected' && 'Baseline ECOCROP and Market Parameters'}
          {scenario === 'optimistic' && 'Price +20%, Yield +15%, Discount Rate -1%'}
        </div>
      </div>
    </div>
  );
};

export default InvestorControls;
