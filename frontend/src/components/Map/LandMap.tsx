import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { Navigation, Compass } from 'lucide-react';
import type { Coordinate } from '../../types';

interface LandMapProps {
  selectedCoord: Coordinate | null;
  onSelectCoord: (coord: Coordinate) => void;
  isLoading: boolean;
}

// Custom crisp SVG Pin Icon to avoid Vite Leaflet asset path issues
const customPinIcon = L.divIcon({
  className: 'custom-map-marker',
  html: `
    <div style="position: relative; width: 34px; height: 34px; display: flex; align-items: center; justify-content: center;">
      <div style="position: absolute; width: 100%; height: 100%; background: rgba(16, 185, 129, 0.35); border-radius: 50%; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
      <div style="position: relative; width: 26px; height: 26px; background: #059669; border: 2px solid #ffffff; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.5);">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 2a8 8 0 0 0-8 8c0 5.25 8 12 8 12s8-6.75 8-12a8 8 0 0 0-8-8z"/>
          <circle cx="12" cy="10" r="3"/>
        </svg>
      </div>
    </div>
  `,
  iconSize: [34, 34],
  iconAnchor: [17, 17],
});

// Click handler component inside MapContainer
function MapClickHandler({ onSelectCoord }: { onSelectCoord: (coord: Coordinate) => void }) {
  useMapEvents({
    click(e) {
      onSelectCoord({
        latitude: Number(e.latlng.lat.toFixed(4)),
        longitude: Number(e.latlng.lng.toFixed(4)),
      });
    },
  });
  return null;
}

// Re-center component
function MapRecenter({ coord }: { coord: Coordinate | null }) {
  const map = useMapEvents({});
  useEffect(() => {
    if (coord) {
      map.flyTo([coord.latitude, coord.longitude], Math.max(map.getZoom(), 7), {
        duration: 1.2,
      });
    }
  }, [coord, map]);
  return null;
}

export const PRESET_LOCATIONS: { name: string; tag: string; coord: Coordinate; desc: string }[] = [
  {
    name: 'Kerala Tropics',
    tag: 'Tropical Agroforestry',
    coord: { latitude: 10.53, longitude: 76.21 },
    desc: 'High annual precipitation (2,800mm), fertile acidic loam — ideal for Teak & Spices',
  },
  {
    name: 'Costa Rica Highlands',
    tag: 'Wet Cloud Forest',
    coord: { latitude: 10.31, longitude: -84.82 },
    desc: 'Hyper-humid volcanic soils — optimal for Cocoa & Coffee agroforestry',
  },
  {
    name: 'Cascadia Foothills',
    tag: 'Temperate Forestry',
    coord: { latitude: 44.56, longitude: -123.26 },
    desc: 'Cool temperate valley, seasonal rainfall — optimal for Pine & Poplar',
  },
  {
    name: 'Andalusia Valley',
    tag: 'Mediterranean Arid',
    coord: { latitude: 37.38, longitude: -5.98 },
    desc: 'Moderate winter rain, calcareous alkaline soil — optimal for Olive',
  },
  {
    name: 'Kitui Basin',
    tag: 'Semi-Arid Savanna',
    coord: { latitude: -1.37, longitude: 38.01 },
    desc: 'Low rainfall (550mm) — stress-test for drought-hardy Moringa & Neem',
  },
  {
    name: 'Gulf of Guinea',
    tag: 'Ocean / Off-Grid',
    coord: { latitude: 0.0, longitude: 0.0 },
    desc: 'Atlantic Ocean — Demonstrates strict zero-fallback unavailable state',
  },
];

export const LandMap: React.FC<LandMapProps> = ({
  selectedCoord,
  onSelectCoord,
  isLoading,
}) => {
  const defaultCenter: [number, number] = [15.0, 30.0];

  return (
    <div className="flex flex-col space-y-4">
      {/* Preset Location Quick Pills */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 text-xs scrollbar-thin">
        <span className="text-slate-400 font-medium whitespace-nowrap flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-emerald-400" /> Presets:
        </span>
        {PRESET_LOCATIONS.map((preset) => {
          const isSelected =
            selectedCoord &&
            Math.abs(selectedCoord.latitude - preset.coord.latitude) < 0.01 &&
            Math.abs(selectedCoord.longitude - preset.coord.longitude) < 0.01;
          return (
            <button
              key={preset.name}
              type="button"
              onClick={() => onSelectCoord(preset.coord)}
              disabled={isLoading}
              className={`px-2.5 py-1 rounded-lg border whitespace-nowrap transition-all text-xs flex items-center space-x-1.5 ${
                isSelected
                  ? 'bg-emerald-500/20 border-emerald-500 text-emerald-300 font-medium'
                  : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:text-white'
              }`}
              title={preset.desc}
            >
              <span>{preset.name}</span>
              <span className="text-[10px] opacity-60 font-mono">({preset.tag})</span>
            </button>
          );
        })}
      </div>

      {/* Map Container */}
      <div className="relative w-full h-[400px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl">
        <MapContainer
          center={selectedCoord ? [selectedCoord.latitude, selectedCoord.longitude] : defaultCenter}
          zoom={selectedCoord ? 7 : 3}
          scrollWheelZoom={true}
          className="w-full h-full"
        >
          {/* Dark Carto Tiles */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />

          <MapClickHandler onSelectCoord={onSelectCoord} />
          <MapRecenter coord={selectedCoord} />

          {selectedCoord && (
            <Marker
              position={[selectedCoord.latitude, selectedCoord.longitude]}
              icon={customPinIcon}
            >
              <Popup>
                <div className="p-1 text-xs">
                  <div className="font-semibold text-emerald-400 mb-0.5">Target Project Coordinate</div>
                  <div className="font-mono text-slate-200">
                    Lat: {selectedCoord.latitude.toFixed(4)}°, Lon: {selectedCoord.longitude.toFixed(4)}°
                  </div>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>

        {/* Floating Coordinate HUD */}
        <div className="absolute bottom-3 left-3 z-[1000] bg-slate-950/90 backdrop-blur-md border border-slate-800/90 rounded-lg px-3 py-1.5 text-xs text-slate-300 font-mono shadow-lg flex items-center space-x-2">
          <Navigation className="w-3.5 h-3.5 text-emerald-400" />
          {selectedCoord ? (
            <span>
              Lat: <strong className="text-white">{selectedCoord.latitude.toFixed(4)}°</strong> | Lon:{' '}
              <strong className="text-white">{selectedCoord.longitude.toFixed(4)}°</strong>
            </span>
          ) : (
            <span className="text-slate-400">Click anywhere on the map to pin land coordinates</span>
          )}
        </div>

        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 z-[1001] bg-slate-950/70 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
            <div className="w-10 h-10 rounded-full border-2 border-emerald-500 border-t-transparent animate-spin" />
            <span className="text-xs font-medium text-emerald-300 tracking-wide font-mono">
              Streaming Climate & Soil Telemetry...
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default LandMap;
