import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Cloud, ShieldCheck, Info } from 'lucide-react';
import type { CarbonProjection } from '../../types';

interface CarbonProjectionChartProps {
  projection: CarbonProjection | null | undefined;
  commonName: string;
}

export const CarbonProjectionChart: React.FC<CarbonProjectionChartProps> = ({
  projection,
  commonName,
}) => {
  if (!projection) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-center flex flex-col items-center justify-center space-y-2">
        <Cloud className="w-8 h-8 text-slate-600 mb-1" />
        <h4 className="text-sm font-medium text-slate-300">No Carbon Trajectory Loaded</h4>
        <p className="text-xs text-slate-400">Select a plantation strategy above to inspect the 20-year carbon growth model.</p>
      </div>
    );
  }

  const chartData = projection.trajectory.map((pt) => ({
    year: `Yr ${pt.year}`,
    cumulative_co2e: pt.cumulative_co2e_t_ha,
    annual_increment: pt.annual_co2e_increment_t_ha,
    agb: pt.above_ground_biomass_t_ha,
  }));

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <Cloud className="w-4 h-4 text-emerald-400" />
            <span>20-Year Biophysical Carbon Sequestration</span>
          </h3>
          <p className="text-xs text-slate-400">
            Species: <strong className="text-emerald-300">{commonName}</strong> ({projection.scientific_name})
          </p>
        </div>

        {/* Quick KPI stats */}
        <div className="flex items-center space-x-3 text-xs font-mono">
          <div className="bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase block">20-Yr Cumulative</span>
            <span className="text-emerald-400 font-bold text-sm">
              {projection.cumulative_20yr_co2e_t_ha.toFixed(1)} <span className="text-[10px] text-slate-400">tCO2e/ha</span>
            </span>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg">
            <span className="text-slate-400 text-[10px] uppercase block">Mean Annual Increment</span>
            <span className="text-sky-400 font-bold text-sm">
              {projection.mean_annual_co2e_t_ha.toFixed(1)} <span className="text-[10px] text-slate-400">tCO2e/ha/yr</span>
            </span>
          </div>
        </div>
      </div>

      {/* Trajectory Recharts View */}
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="carbonGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 10 }} />
            <YAxis
              yAxisId="left"
              stroke="#64748b"
              tick={{ fontSize: 10 }}
              label={{ value: 'Cumulative tCO2e/ha', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#64748b"
              tick={{ fontSize: 10 }}
              label={{ value: 'Annual Increment', angle: 90, position: 'insideRight', fill: '#64748b', fontSize: 10 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#090d16',
                borderColor: '#1e293b',
                borderRadius: '8px',
                fontSize: '11px',
                color: '#f8fafc',
              }}
            />
            <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
            <Area
              yAxisId="left"
              type="monotone"
              dataKey="cumulative_co2e"
              name="Cumulative Biomass Carbon (tCO2e/ha)"
              stroke="#10b981"
              strokeWidth={2.5}
              fill="url(#carbonGradient)"
            />
            <Bar
              yAxisId="right"
              dataKey="annual_increment"
              name="Annual Increment (tCO2e/ha/yr)"
              fill="#38bdf8"
              opacity={0.7}
              radius={[3, 3, 0, 0]}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Labeled IPCC Tier 1 Scientific Assumptions Box */}
      <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-slate-300">
          <Info className="w-3.5 h-3.5 text-emerald-400" />
          <span>Biophysical Modeling Assumptions & IPCC Provenance</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs text-slate-400 font-mono">
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
            <span className="text-[10px] text-slate-500 block">Root-to-Shoot Ratio</span>
            <strong className="text-slate-300">0.24</strong> (IPCC Tier 1 AFOLU)
          </div>
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
            <span className="text-[10px] text-slate-500 block">Carbon Fraction</span>
            <strong className="text-slate-300">0.47</strong> (IPCC Forestry default)
          </div>
          <div className="bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
            <span className="text-[10px] text-slate-500 block">Biomass Model</span>
            <strong className="text-slate-300">Sigmoidal Logistic AGB</strong>
          </div>
        </div>
      </div>

      {/* Mandatory Regulatory Disclaimer */}
      <div className="rounded-xl p-3 bg-emerald-950/20 border border-emerald-500/20 flex items-start space-x-2.5 text-xs text-slate-300">
        <ShieldCheck className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
        <p className="text-[11px] leading-relaxed text-slate-400">
          <strong className="text-emerald-300">Regulatory Disclaimer: </strong>
          {projection.disclaimer}
        </p>
      </div>
    </div>
  );
};

export default CarbonProjectionChart;
