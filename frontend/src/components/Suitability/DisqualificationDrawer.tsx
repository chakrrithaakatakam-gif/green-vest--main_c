import React, { useState } from 'react';
import { ChevronDown, ChevronUp, XCircle, AlertOctagon } from 'lucide-react';
import type { PlantEvaluationResult } from '../../types';

interface DisqualificationDrawerProps {
  disqualified: PlantEvaluationResult[];
}

export const DisqualificationDrawer: React.FC<DisqualificationDrawerProps> = ({ disqualified }) => {
  const [isOpen, setIsOpen] = useState<boolean>(false);

  if (!disqualified || disqualified.length === 0) {
    return null;
  }

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-3">
      {/* Header Toggle */}
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between cursor-pointer group select-none"
      >
        <div className="flex items-center space-x-2">
          <AlertOctagon className="w-4 h-4 text-rose-400" />
          <h3 className="text-xs uppercase font-semibold tracking-wider text-slate-300 group-hover:text-white transition-colors">
            Disqualified Candidates (Stage 1 Hard Bounds Filter)
          </h3>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 font-mono">
            {disqualified.length} Eliminated
          </span>
        </div>

        <button
          type="button"
          className="text-slate-400 group-hover:text-white transition-colors p-1"
        >
          {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      <p className="text-xs text-slate-400">
        Plants strictly disqualified by physical environmental thresholds (Rainfall, Temperature, Soil pH) without synthetic overrides.
      </p>

      {/* Accordion Content */}
      {isOpen && (
        <div className="space-y-2 pt-2 border-t border-slate-800/80 max-h-[350px] overflow-y-auto pr-1">
          {disqualified.map((item) => (
            <div
              key={item.plant.crop_id}
              className="p-3 rounded-xl bg-slate-900/60 border border-rose-950/40 space-y-1.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <XCircle className="w-3.5 h-3.5 text-rose-400 flex-shrink-0" />
                  <span className="text-xs font-semibold text-slate-200">{item.plant.common_name}</span>
                  <span className="text-[11px] text-slate-400 italic">({item.plant.scientific_name})</span>
                </div>
                {item.plant.use_category && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                    {item.plant.use_category}
                  </span>
                )}
              </div>

              {/* Reasons */}
              <div className="space-y-1 pl-5">
                {item.feasibility.failure_reasons.map((reason, rIdx) => (
                  <div key={rIdx} className="text-[11px] font-mono text-rose-300/90 leading-relaxed">
                    • {reason}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DisqualificationDrawer;
