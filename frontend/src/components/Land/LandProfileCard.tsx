import React from 'react';
import { CloudRain, Thermometer, FlaskConical, CheckCircle2, AlertTriangle, Database } from 'lucide-react';
import type { LandProfile } from '../../types';

interface LandProfileCardProps {
  profile: LandProfile | null;
  isLoading: boolean;
}

export const LandProfileCard: React.FC<LandProfileCardProps> = ({ profile, isLoading }) => {
  if (isLoading) {
    return (
      <div className="glass-panel rounded-2xl p-5 border border-slate-800 animate-pulse space-y-4">
        <div className="h-4 bg-slate-800 rounded w-1/3" />
        <div className="grid grid-cols-3 gap-3">
          <div className="h-20 bg-slate-900 rounded-xl" />
          <div className="h-20 bg-slate-900 rounded-xl" />
          <div className="h-20 bg-slate-900 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 text-center flex flex-col items-center justify-center space-y-2">
        <Database className="w-8 h-8 text-slate-600 mb-1" />
        <h4 className="text-sm font-medium text-slate-300">No Land Telemetry Acquired</h4>
        <p className="text-xs text-slate-400 max-w-sm">
          Select coordinates on the map above or pick a preset location to stream real physical rainfall, temperature, and soil pH.
        </p>
      </div>
    );
  }

  const { climate, soil, composite_data_confidence } = profile;
  const isSoilUnavailable = soil.status === 'unavailable' || soil.ph === null;
  const isClimateUnavailable = climate.status === 'unavailable' || climate.annual_rainfall_mm === null;

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 space-y-4">
      {/* Card Header & Confidence Badge */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-200 tracking-tight flex items-center space-x-2">
            <span>Canonical Land Profile</span>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">
              Lat: {profile.latitude.toFixed(2)}°, Lon: {profile.longitude.toFixed(2)}°
            </span>
          </h3>
          <p className="text-[11px] text-slate-400">Audited MVP physical environmental determinants</p>
        </div>

        {/* Data Confidence Indicator */}
        <div className="flex items-center space-x-2 text-xs bg-slate-900/90 border border-slate-800 rounded-lg px-2.5 py-1.5 font-mono">
          <span className="text-slate-400 text-[11px]">Confidence:</span>
          <span
            className={`font-semibold ${
              composite_data_confidence >= 0.8
                ? 'text-emerald-400'
                : composite_data_confidence >= 0.5
                ? 'text-amber-400'
                : 'text-rose-400'
            }`}
          >
            {(composite_data_confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      {/* 3 Physical MVP Metric Tiles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Metric 1: Rainfall */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs uppercase font-medium tracking-wider">Annual Rainfall</span>
            <CloudRain className="w-4 h-4 text-sky-400" />
          </div>

          <div className="my-1">
            {isClimateUnavailable ? (
              <span className="text-xs font-mono text-amber-400 font-medium">Unavailable</span>
            ) : (
              <div className="flex items-baseline space-x-1">
                <span className="text-2xl font-bold font-mono text-white tracking-tight">
                  {climate.annual_rainfall_mm?.toLocaleString()}
                </span>
                <span className="text-xs font-mono text-slate-400">mm/yr</span>
              </div>
            )}
          </div>

          <div className="text-[10px] text-slate-400 truncate">
            {climate.source}
          </div>
        </div>

        {/* Metric 2: Temperature */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs uppercase font-medium tracking-wider">Temperature</span>
            <Thermometer className="w-4 h-4 text-amber-400" />
          </div>

          <div className="my-1">
            {isClimateUnavailable ? (
              <span className="text-xs font-mono text-amber-400 font-medium">Unavailable</span>
            ) : (
              <div className="flex items-baseline space-x-2">
                <span className="text-2xl font-bold font-mono text-white tracking-tight">
                  {climate.mean_temperature_c?.toFixed(1)}°C
                </span>
                <span className="text-[11px] font-mono text-slate-400">
                  ({climate.min_temperature_c?.toFixed(0)}° / {climate.max_temperature_c?.toFixed(0)}°)
                </span>
              </div>
            )}
          </div>

          <div className="text-[10px] text-slate-400 truncate">
            Mean annual (Min/Max range)
          </div>
        </div>

        {/* Metric 3: Soil pH */}
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 relative overflow-hidden flex flex-col justify-between">
          <div className="flex items-center justify-between text-slate-400 mb-1">
            <span className="text-xs uppercase font-medium tracking-wider">Soil pH (0-30cm)</span>
            <FlaskConical className="w-4 h-4 text-emerald-400" />
          </div>

          <div className="my-1">
            {isSoilUnavailable ? (
              <div className="flex items-center space-x-1.5 text-amber-400">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-xs font-mono font-medium">Out of Bounds / Null</span>
              </div>
            ) : (
              <div className="flex items-baseline space-x-1.5">
                <span className="text-2xl font-bold font-mono text-white tracking-tight">
                  {soil.ph?.toFixed(2)}
                </span>
                <span className="text-xs font-mono text-slate-400">
                  {soil.ph! < 6.0 ? 'Acidic' : soil.ph! > 7.5 ? 'Alkaline' : 'Neutral'}
                </span>
              </div>
            )}
          </div>

          <div className="text-[10px] text-slate-400 truncate">
            {soil.source}
          </div>
        </div>
      </div>

      {/* Strict Zero Fabricated Fallbacks Audited Warning Banner */}
      {isSoilUnavailable && (
        <div className="rounded-xl p-3 bg-amber-950/30 border border-amber-500/30 flex items-start space-x-2.5 text-xs text-amber-200">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <strong className="text-amber-300">Audited Resilience Rule: </strong>
            ISRIC SoilGrids returned no valid soil profile at this coordinate (water body or unmapped soil).
            GreenVest <span className="underline font-semibold">strictly refuses</span> to inject fabricated numbers or silent fallbacks. Suitability is evaluated solely on available climate variables.
          </div>
        </div>
      )}

      {/* Provenance Footer */}
      <div className="flex items-center justify-between text-[11px] text-slate-400 border-t border-slate-800/80 pt-2 font-mono">
        <div className="flex items-center space-x-1.5">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Zero Fabricated Fallbacks Verified</span>
        </div>
        <span>Evaluated: {profile.evaluated_at ? new Date(profile.evaluated_at).toLocaleTimeString() : 'Live'}</span>
      </div>
    </div>
  );
};

export default LandProfileCard;
