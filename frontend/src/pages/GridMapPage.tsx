import React, { useState, useMemo, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { 
  Layers, 
  ExternalLink,
  Locate,
  CloudRain,
  Navigation2
} from 'lucide-react';
import type { Equipment, Crew, RiskLevel } from '../types/grid';

interface GridMapPageProps {
  predictions: Equipment[];
  crews: Crew[];
  onSelectEquipment: (id: string) => void;
  onNavigateToEquipment: () => void;
}

// Controller component to smoothly pan/zoom map and handle resize
function MapController({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.invalidateSize();
  }, [map]);

  useEffect(() => {
    map.flyTo(center, zoom, { duration: 1.2 });
  }, [center, zoom, map]);

  return null;
}

// Custom SVG Pin for equipment with risk badge
const createEquipmentIcon = (risk: RiskLevel, id: string) => {
  const colors: Record<RiskLevel, { bg: string; border: string; glow: string }> = {
    CRITICAL: { bg: '#ef4444', border: '#ffffff', glow: 'rgba(239, 68, 68, 0.9)' },
    HIGH: { bg: '#f97316', border: '#ffffff', glow: 'rgba(249, 115, 22, 0.85)' },
    MEDIUM: { bg: '#eab308', border: '#ffffff', glow: 'rgba(234, 179, 8, 0.7)' },
    LOW: { bg: '#10b981', border: '#ffffff', glow: 'rgba(16, 185, 129, 0.6)' },
  };

  const c = colors[risk] || colors.LOW;
  const isHighRisk = risk === 'CRITICAL' || risk === 'HIGH';

  const html = `
    <div style="
      position: relative;
      width: 34px;
      height: 34px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
    ">
      ${isHighRisk ? `
        <div style="
          position: absolute;
          width: 42px;
          height: 42px;
          border-radius: 50%;
          border: 2px solid ${c.bg};
          animation: pulse-crit 1.4s infinite;
          opacity: 0.85;
        "></div>
      ` : ''}
      <div style="
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: ${c.bg};
        border: 2px solid #ffffff;
        box-shadow: 0 0 14px ${c.glow};
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-family: monospace;
        font-size: 11px;
        font-weight: 800;
      ">
        ${id}
      </div>
    </div>
  `;

  return L.divIcon({
    html,
    className: 'leaflet-custom-marker',
    iconSize: [34, 34],
    iconAnchor: [17, 17],
  });
};

// Custom DivIcon for Crew Station
const createCrewIcon = (crewId: string, status: string) => {
  const isAvail = status.toLowerCase() === 'available';
  const html = `
    <div style="
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: ${isAvail ? '#0284c7' : '#475569'};
      border: 2px solid #ffffff;
      box-shadow: 0 0 14px rgba(2, 132, 199, 0.8);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-family: monospace;
      font-size: 11px;
      font-weight: 800;
      cursor: pointer;
    ">
      ${crewId}
    </div>
  `;

  return L.divIcon({
    html,
    className: 'leaflet-custom-crew',
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

type MapLayerType = 'streets' | 'satellite' | 'voyager' | 'dark';

export const GridMapPage: React.FC<GridMapPageProps> = ({
  predictions,
  crews,
  onSelectEquipment,
  onNavigateToEquipment,
}) => {
  const [mapLayer, setMapLayer] = useState<MapLayerType>('streets');
  const [showLiveWeatherRadar, setShowLiveWeatherRadar] = useState(false);
  const [showCrews, setShowCrews] = useState(true);
  const [showDispatchLines, setShowDispatchLines] = useState(true);
  const [riskFilter, setRiskFilter] = useState<string>('ALL');

  // Bangalore Grid Region Coordinates
  const [mapCenter, setMapCenter] = useState<[number, number]>([12.982, 77.594]);
  const [mapZoom, setMapZoom] = useState<number>(11);

  const filteredEquipment = useMemo(() => {
    return predictions.filter((p) => {
      if (!p.latitude || !p.longitude) return false;
      if (riskFilter !== 'ALL' && p.risk_level !== riskFilter) return false;
      return true;
    });
  }, [predictions, riskFilter]);

  const dispatchLines = useMemo(() => {
    if (!showDispatchLines) return [];
    
    const lines: Array<{
      id: string;
      positions: [number, number][];
      equipmentId: string;
      crewId: string;
      distance: number | null;
      risk: RiskLevel;
    }> = [];

    const crewMap = new Map<string, Crew>();
    crews.forEach((c) => crewMap.set(c.crew_id, c));

    predictions.forEach((eq) => {
      if ((eq.risk_level === 'HIGH' || eq.risk_level === 'CRITICAL') && eq.assigned_crew) {
        const crew = crewMap.get(eq.assigned_crew);
        if (crew && crew.latitude && crew.longitude && eq.latitude && eq.longitude) {
          lines.push({
            id: `${eq.equipment_id}-${crew.crew_id}`,
            positions: [
              [eq.latitude, eq.longitude],
              [crew.latitude, crew.longitude],
            ],
            equipmentId: eq.equipment_id,
            crewId: crew.crew_id,
            distance: eq.crew_distance_km,
            risk: eq.risk_level,
          });
        }
      }
    });

    return lines;
  }, [predictions, crews, showDispatchLines]);

  const handleFlyToAsset = (eqId: string) => {
    const target = predictions.find(p => p.equipment_id === eqId);
    if (target && target.latitude && target.longitude) {
      setMapCenter([target.latitude, target.longitude]);
      setMapZoom(14);
      onSelectEquipment(eqId);
    }
  };

  const handleResetBangaloreView = () => {
    setMapCenter([12.982, 77.594]);
    setMapZoom(11);
  };

  return (
    <div className="page-content" style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)' }}>
      
      {/* Real-time Map Control Floating Bar */}
      <div className="glass-panel" style={{ padding: '0.75rem 1.25rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
        
        {/* Left: Map Mode Selector & Weather Radar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={16} color="#38bdf8" />
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-bright)' }}>Real Map Layer:</span>
          </div>

          <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.8)', padding: '2px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <button 
              className={`btn btn-sm ${mapLayer === 'streets' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ border: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
              onClick={() => setMapLayer('streets')}
            >
              🗺️ OpenStreetMap Real
            </button>
            <button 
              className={`btn btn-sm ${mapLayer === 'satellite' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ border: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
              onClick={() => setMapLayer('satellite')}
            >
              🛰️ Real Aerial Satellite
            </button>
            <button 
              className={`btn btn-sm ${mapLayer === 'voyager' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ border: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
              onClick={() => setMapLayer('voyager')}
            >
              🏙️ City Navigation
            </button>
            <button 
              className={`btn btn-sm ${mapLayer === 'dark' ? 'btn-primary' : 'btn-secondary'}`}
              style={{ border: 'none', padding: '4px 10px', fontSize: '0.75rem' }}
              onClick={() => setMapLayer('dark')}
            >
              🌙 Dark Ops
            </button>
          </div>

          <button 
            className={`btn btn-sm ${showLiveWeatherRadar ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setShowLiveWeatherRadar(!showLiveWeatherRadar)}
            title="Toggle Live Real-Time Precipitation Weather Radar"
          >
            <CloudRain size={14} color={showLiveWeatherRadar ? '#ffffff' : '#38bdf8'} />
            <span>Live Weather Radar</span>
          </button>
        </div>

        {/* Right: Asset Locator & View Reset */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Navigation2 size={15} color="#38bdf8" />
            <select 
              className="form-select"
              onChange={(e) => handleFlyToAsset(e.target.value)}
              defaultValue=""
              style={{ padding: '5px 10px', fontSize: '0.75rem', minWidth: '150px' }}
            >
              <option value="" disabled>Fly to Grid Asset...</option>
              {predictions.map(p => (
                <option key={p.equipment_id} value={p.equipment_id}>
                  {p.equipment_id} ({p.type} - {p.risk_level})
                </option>
              ))}
            </select>
          </div>

          <select 
            className="form-select"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            style={{ padding: '5px 10px', fontSize: '0.75rem' }}
          >
            <option value="ALL">All Risks ({predictions.length})</option>
            <option value="CRITICAL">Critical Only</option>
            <option value="HIGH">High Risk Only</option>
            <option value="MEDIUM">Medium Risk Only</option>
            <option value="LOW">Low Risk Only</option>
          </select>

          <button 
            className="btn btn-secondary btn-sm"
            onClick={handleResetBangaloreView}
            title="Reset to Bangalore Grid Center"
          >
            <Locate size={14} />
            <span>Reset View</span>
          </button>
        </div>
      </div>

      {/* Full GIS Interactive Map Canvas */}
      <div 
        className="glass-panel" 
        style={{ 
          flex: 1, 
          minHeight: '580px', 
          padding: 0, 
          position: 'relative', 
          overflow: 'hidden',
          borderRadius: '16px',
          border: '1px solid var(--border-glow)'
        }}
      >
        <MapContainer 
          center={mapCenter} 
          zoom={mapZoom} 
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%' }}
        >
          <MapController center={mapCenter} zoom={mapZoom} />

          {/* Layer 1: Real-World OpenStreetMap Standard (Real roads, landmarks, cities, topology) */}
          {mapLayer === 'streets' && (
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
              maxZoom={19}
            />
          )}

          {/* Layer 2: Real Aerial Satellite (Esri World Imagery - Real physical infrastructure, power lines, ground) */}
          {mapLayer === 'satellite' && (
            <TileLayer
              attribution='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
              url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
              maxZoom={18}
            />
          )}

          {/* Layer 3: Carto Voyager Detailed Street Navigation */}
          {mapLayer === 'voyager' && (
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
              maxZoom={19}
            />
          )}

          {/* Layer 4: Carto Dark Ops */}
          {mapLayer === 'dark' && (
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
              maxZoom={19}
            />
          )}

          {/* Optional Real-Time Live Rain & Precipitation Radar Layer */}
          {showLiveWeatherRadar && (
            <TileLayer
              attribution='Weather Radar &copy; RainViewer'
              url="https://tilecache.rainviewer.com/v2/radar/nowcast_latest/256/{z}/{x}/{y}/2/1_1.png"
              opacity={0.65}
              maxZoom={18}
            />
          )}

          {/* Pre-positioning Dispatch Polylines */}
          {dispatchLines.map((line) => (
            <Polyline
              key={line.id}
              positions={line.positions}
              pathOptions={{
                color: line.risk === 'CRITICAL' ? '#ef4444' : '#f97316',
                weight: 3.5,
                dashArray: '8, 8',
                opacity: 0.9,
              }}
            />
          ))}

          {/* Grid Equipment Markers */}
          {filteredEquipment.map((eq) => (
            <Marker 
              key={eq.equipment_id}
              position={[eq.latitude, eq.longitude]}
              icon={createEquipmentIcon(eq.risk_level, eq.equipment_id)}
            >
              <Popup>
                <div style={{ minWidth: '230px', padding: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '1rem', color: '#fff' }}>Asset {eq.equipment_id}</strong>
                    <span className={`badge badge-${eq.risk_level.toLowerCase()}`}>{eq.risk_level}</span>
                  </div>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    {eq.type} • Age: {eq.age} yrs • Health: <strong>{eq.health}/100</strong>
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '0.75rem', marginBottom: '8px' }}>
                    <div>Priority: <strong style={{ color: '#f97316' }}>{eq.priority_score}</strong></div>
                    <div>Failure Prob: <strong>{(eq.failure_probability * 100).toFixed(1)}%</strong></div>
                    <div>Weather Risk: <strong>{eq.weather_risk}</strong></div>
                    <div>Grid Impact: <strong>{eq.grid_impact}</strong></div>
                  </div>

                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '8px', fontFamily: 'monospace' }}>
                    Location: {eq.latitude.toFixed(5)}° N, {eq.longitude.toFixed(5)}° E
                  </div>

                  {eq.assigned_crew && eq.assigned_crew !== 'N/A - below threshold' && (
                    <div style={{ fontSize: '0.75rem', padding: '6px', background: 'rgba(56, 189, 248, 0.12)', borderRadius: '6px', marginBottom: '8px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                      Pre-positioned Crew: <strong style={{ color: '#38bdf8' }}>{eq.assigned_crew}</strong> ({eq.crew_distance_km ?? '—'} km)
                    </div>
                  )}

                  <button 
                    className="btn btn-primary btn-sm"
                    style={{ width: '100%' }}
                    onClick={() => {
                      onSelectEquipment(eq.equipment_id);
                      onNavigateToEquipment();
                    }}
                  >
                    <ExternalLink size={12} />
                    <span>Open in AI Decision Card</span>
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Field Crew Base Stations */}
          {showCrews && crews.map((crew) => (
            <Marker
              key={crew.crew_id}
              position={[crew.latitude, crew.longitude]}
              icon={createCrewIcon(crew.crew_id, crew.status)}
            >
              <Popup>
                <div style={{ minWidth: '200px', padding: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <strong style={{ fontSize: '0.95rem', color: '#fff' }}>Field Crew {crew.crew_id}</strong>
                    <span className={`badge badge-${crew.status === 'available' ? 'low' : 'medium'}`}>
                      {crew.status}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '6px' }}>
                    Skill: <strong style={{ color: '#38bdf8', textTransform: 'capitalize' }}>{crew.skill}</strong> • Capacity: {crew.capacity} engineers
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '8px' }}>
                    Pre-positioned Targets: <strong>{crew.assigned_count}</strong>
                  </div>

                  {crew.assignments && crew.assignments.length > 0 && (
                    <div style={{ fontSize: '0.72rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                      {crew.assignments.map((a) => (
                        <div key={a.equipment_id} style={{ padding: '4px 6px', background: 'rgba(255,255,255,0.05)', borderRadius: '4px' }}>
                          Target: <strong>{a.equipment_id}</strong> ({a.distance_km} km) • {a.action}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Bottom GIS Status Footer */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.75rem', fontSize: '0.78rem', color: 'var(--text-dim)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <span>Real-time GPS: <strong>Bangalore Grid Sector (BESCOM Area)</strong></span>
          <span>• Active Substation Nodes: <strong>30 Equipment Sites</strong></span>
          <span>• Rapid Response Crews: <strong>{crews.length} Units Deployed</strong></span>
        </div>
        <div style={{ display: 'flex', gap: '14px' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
            <input type="checkbox" checked={showCrews} onChange={(e) => setShowCrews(e.target.checked)} />
            <span>Crews</span>
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
            <input type="checkbox" checked={showDispatchLines} onChange={(e) => setShowDispatchLines(e.target.checked)} />
            <span>Pre-positioning Lines</span>
          </label>
        </div>
      </div>

    </div>
  );
};
