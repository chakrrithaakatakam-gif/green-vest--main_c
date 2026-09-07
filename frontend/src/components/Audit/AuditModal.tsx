import React from 'react';
import { X, CheckCircle2, AlertTriangle, Shield, FileText } from 'lucide-react';
import type { PlantationStrategy } from '../../types';

interface AuditModalProps {
  strategy: PlantationStrategy | null;
  onClose: () => void;
}

export const AuditModal: React.FC<AuditModalProps> = ({ strategy, onClose }) => {
  if (!strategy) return null;

  const { audit_trail, score_breakdown } = strategy;

  return (
    <div className="fixed inset-0 z-[2000] bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel max-w-2xl w-full rounded-2xl border border-slate-700/80 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-slate-900/80">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400">
              <FileText className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white tracking-tight">
                Explainability & Scientific Audit Trail
              </h3>
              <p className="text-xs text-slate-400 font-mono">
                {strategy.common_name} ({strategy.scientific_name}) • Rank #{strategy.rank}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 overflow-y-auto space-y-4 text-xs">
          {/* Multi-Objective Score Breakdown Table */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
            <span className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider block">
              Multi-Objective GreenVest Score Formula
            </span>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center font-mono">
              <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
                <span className="text-[10px] text-slate-500 block">Suitability</span>
                <strong className="text-emerald-400 text-sm">
                  {score_breakdown.suitability_score?.toFixed(0)}%
                </strong>
                <span className="text-[9px] text-slate-500 block">
                  (+{score_breakdown.weighted_suitability})
                </span>
              </div>
              <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
                <span className="text-[10px] text-slate-500 block">Carbon Index</span>
                <strong className="text-sky-400 text-sm">
                  {score_breakdown.carbon_score?.toFixed(0)}%
                </strong>
                <span className="text-[9px] text-slate-500 block">
                  (+{score_breakdown.weighted_carbon})
                </span>
              </div>
              <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
                <span className="text-[10px] text-slate-500 block">Financial DCF</span>
                <strong className="text-amber-400 text-sm">
                  {score_breakdown.financial_score?.toFixed(0)}%
                </strong>
                <span className="text-[9px] text-slate-500 block">
                  (+{score_breakdown.weighted_financial})
                </span>
              </div>
              <div className="p-2 rounded bg-slate-950/70 border border-slate-800/80">
                <span className="text-[10px] text-slate-500 block">Risk Penalty</span>
                <strong className="text-rose-400 text-sm">
                  -{score_breakdown.risk_penalty?.toFixed(0)}%
                </strong>
                <span className="text-[9px] text-slate-500 block">
                  (-{score_breakdown.weighted_risk_deduction})
                </span>
              </div>
            </div>
            <div className="text-right text-[11px] font-mono text-emerald-300 font-semibold pt-1">
              Final GreenVest Score: {strategy.greenvest_score.toFixed(1)} / 100
            </div>
          </div>

          {/* Strengths */}
          {audit_trail.strengths.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] uppercase font-semibold text-emerald-400 tracking-wider flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Validated Strengths</span>
              </span>
              <ul className="space-y-1 pl-4 list-disc text-slate-300 leading-relaxed">
                {audit_trail.strengths.map((str, idx) => (
                  <li key={idx}>{str}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Environmental Constraints */}
          {audit_trail.constraints.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] uppercase font-semibold text-amber-400 tracking-wider flex items-center space-x-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Marginal Environmental Envelopes</span>
              </span>
              <ul className="space-y-1 pl-4 list-disc text-slate-300 leading-relaxed">
                {audit_trail.constraints.map((con, idx) => (
                  <li key={idx}>{con}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Risk Factors */}
          {audit_trail.risk_flags.length > 0 && (
            <div className="space-y-1.5">
              <span className="text-[11px] uppercase font-semibold text-rose-400 tracking-wider flex items-center space-x-1.5">
                <Shield className="w-3.5 h-3.5" />
                <span>Identified Risk Flags</span>
              </span>
              <ul className="space-y-1 pl-4 list-disc text-slate-300 leading-relaxed">
                {audit_trail.risk_flags.map((flag, idx) => (
                  <li key={idx}>{flag}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Scientific Provenance References */}
          <div className="pt-3 border-t border-slate-800 space-y-1.5 text-[11px] text-slate-400 font-mono">
            <span className="uppercase text-[10px] text-slate-500 font-semibold block">
              Audited Scientific Provenance
            </span>
            <div>• Botanical Constraints: FAO ECOCROP Database (Validated absolute and optimal ranges)</div>
            <div>• Carbon Growth Curves: FAO Forestry Paper 177 / IPCC 2006 AFOLU Tier 1 Defaults</div>
            <div>• Climate Telemetry: Open-Meteo Historical Climate Reanalysis</div>
            <div>• Soil Chemistry: ISRIC SoilGrids v2.0 REST API (0-30cm pH in H2O)</div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/60 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-emerald-600 text-white font-medium text-xs hover:bg-emerald-500 transition-colors shadow-sm"
          >
            Close Audit Log
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuditModal;
