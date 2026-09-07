import {
  ResponsiveContainer,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
  ComposedChart,
} from 'recharts';
import { DollarSign, Sliders, ShieldAlert } from 'lucide-react';
import type { FinancialMetrics } from '../../types';

interface FinancialAnalysisViewProps {
  metrics: FinancialMetrics | null | undefined;
  commonName: string;
  carbonPrice: number;
  discountRate: number;
  areaHectares: number;
  onUpdateCarbonPrice: (val: number) => void;
  onUpdateDiscountRate: (val: number) => void;
  onUpdateArea: (val: number) => void;
}

export const FinancialAnalysisView: React.FC<FinancialAnalysisViewProps> = ({
  metrics,
  commonName,
  carbonPrice,
  discountRate,
  areaHectares,
  onUpdateCarbonPrice,
  onUpdateDiscountRate,
  onUpdateArea,
}) => {
  if (!metrics) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-center flex flex-col items-center justify-center space-y-2">
        <DollarSign className="w-8 h-8 text-slate-600 mb-1" />
        <h4 className="text-sm font-medium text-slate-300">No Financial DCF Model Loaded</h4>
        <p className="text-xs text-slate-400">Select a plantation strategy above to inspect discounted cash flow projections.</p>
      </div>
    );
  }

  const chartData = metrics.cash_flows.map((cf) => ({
    year: `Yr ${cf.year}`,
    net_cf: cf.net_cash_flow_usd_ha,
    cum_cf: cf.cumulative_cash_flow_usd_ha,
    dcf: cf.discounted_cash_flow_usd_ha,
  }));

  const totalNpvScaled = metrics.npv_usd_ha * areaHectares;
  const totalCapexScaled = (metrics.cash_flows[0]?.capex_usd_ha || 0) * areaHectares;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <DollarSign className="w-4 h-4 text-amber-400" />
            <span>20-Year Discounted Cash Flow (DCF) Financial Model</span>
          </h3>
          <p className="text-xs text-slate-400">
            Investment analysis for <strong className="text-emerald-300">{commonName}</strong> across {areaHectares} ha
          </p>
        </div>

        <div className="text-xs font-mono text-slate-400 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-lg">
          Buffer Deduction: <strong className="text-emerald-400">15%</strong> (Standard Risk Pool)
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* Card 1: 20-Yr Net Present Value */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider block">
            Net Present Value (NPV)
          </span>
          <div className="text-xl font-bold font-mono text-emerald-400">
            ${totalNpvScaled.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </div>
          <span className="text-[10px] font-mono text-slate-500 block">
            (${metrics.npv_usd_ha.toLocaleString()}/ha @ {(discountRate * 100).toFixed(0)}%)
          </span>
        </div>

        {/* Card 2: IRR */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider block">
            Internal Rate of Return (IRR)
          </span>
          <div className="text-xl font-bold font-mono text-sky-400">
            {metrics.irr_pct !== null ? `${metrics.irr_pct.toFixed(1)}%` : 'N/A'}
          </div>
          <span className="text-[10px] font-mono text-slate-500 block">
            Benchmark: {(discountRate * 100).toFixed(0)}% hurdle
          </span>
        </div>

        {/* Card 3: Payback Period */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider block">
            Payback Horizon
          </span>
          <div className="text-xl font-bold font-mono text-amber-400">
            {metrics.payback_period_years ? `${metrics.payback_period_years.toFixed(1)} Yrs` : '> 20 Yrs'}
          </div>
          <span className="text-[10px] font-mono text-slate-500 block">
            Discounted: {metrics.discounted_payback_years ? `${metrics.discounted_payback_years.toFixed(1)} Yrs` : 'N/A'}
          </span>
        </div>

        {/* Card 4: Total ROI % */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
          <span className="text-[10px] uppercase font-semibold text-slate-400 tracking-wider block">
            Return on Investment (ROI)
          </span>
          <div className="text-xl font-bold font-mono text-emerald-400">
            {metrics.roi_pct.toFixed(0)}%
          </div>
          <span className="text-[10px] font-mono text-slate-500 block">
            Total CAPEX: ${totalCapexScaled.toLocaleString()}
          </span>
        </div>
      </div>

      {/* Cash Flow Trajectory Chart */}
      <div className="h-[280px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" stroke="#64748b" tick={{ fontSize: 10 }} />
            <YAxis
              stroke="#64748b"
              tick={{ fontSize: 10 }}
              label={{ value: 'USD ($/ha)', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
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
            <Bar dataKey="net_cf" name="Annual Net Cash Flow ($/ha)" fill="#38bdf8" radius={[3, 3, 0, 0]} />
            <Line
              type="monotone"
              dataKey="cum_cf"
              name="Cumulative Cash Flow ($/ha)"
              stroke="#10b981"
              strokeWidth={2.5}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="dcf"
              name="Discounted Cash Flow ($/ha)"
              stroke="#f59e0b"
              strokeWidth={1.5}
              strokeDasharray="4 4"
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Interactive Financial Sensitivity Sliders */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-300">
          <div className="flex items-center space-x-1.5">
            <Sliders className="w-3.5 h-3.5 text-amber-400" />
            <span>Interactive Financial Sensitivity Controls</span>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">Dynamic DCF Recalculation</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs font-mono">
          {/* Slider 1: Carbon Price */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-slate-400 text-[11px]">
              <span>Carbon Price:</span>
              <strong className="text-emerald-300">${carbonPrice.toFixed(0)} / tCO2e</strong>
            </div>
            <input
              type="range"
              min="10"
              max="100"
              step="5"
              value={carbonPrice}
              onChange={(e) => onUpdateCarbonPrice(Number(e.target.value))}
              className="w-full accent-emerald-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Slider 2: Discount Rate */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-slate-400 text-[11px]">
              <span>Discount Rate (r):</span>
              <strong className="text-sky-300">{(discountRate * 100).toFixed(1)}%</strong>
            </div>
            <input
              type="range"
              min="0.04"
              max="0.18"
              step="0.01"
              value={discountRate}
              onChange={(e) => onUpdateDiscountRate(Number(e.target.value))}
              className="w-full accent-sky-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Slider 3: Land Area */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-slate-400 text-[11px]">
              <span>Project Area:</span>
              <strong className="text-amber-300">{areaHectares.toFixed(1)} Hectares</strong>
            </div>
            <input
              type="range"
              min="1"
              max="50"
              step="1"
              value={areaHectares}
              onChange={(e) => onUpdateArea(Number(e.target.value))}
              className="w-full accent-amber-500 h-1.5 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>
        </div>
      </div>

      {/* Financial Disclaimer */}
      <div className="rounded-xl p-3 bg-amber-950/20 border border-amber-500/20 flex items-start space-x-2.5 text-xs text-slate-300">
        <ShieldAlert className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
        <p className="text-[11px] leading-relaxed text-slate-400">
          <strong className="text-amber-300">Investment Model Disclaimer: </strong>
          {metrics.disclaimer}
        </p>
      </div>
    </div>
  );
};

export default FinancialAnalysisView;
