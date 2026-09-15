import React, { useState } from 'react';
import { 
  Cpu, 
  AlertTriangle, 
  CheckCircle2, 
  Building2, 
  Send,
  Sparkles
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar
} from 'recharts';
import type { Equipment } from '../types/grid';

interface EquipmentIntelligencePageProps {
  predictions: Equipment[];
  selectedId: string;
  onSelectEquipment: (id: string) => void;
}

export const EquipmentIntelligencePage: React.FC<EquipmentIntelligencePageProps> = ({
  predictions,
  selectedId,
  onSelectEquipment,
}) => {
  const [dispatchConfirmed, setDispatchConfirmed] = useState(false);

  const currentAsset = predictions.find((p) => p.equipment_id === selectedId) || predictions[0];

  if (!currentAsset) {
    return (
      <div className="page-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>No equipment records loaded.</p>
      </div>
    );
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#10b981';
      default: return '#38bdf8';
    }
  };

  const radarData = [
    { subject: 'Failure Risk', value: Math.round(currentAsset.failure_probability * 100) },
    { subject: 'Weather Risk', value: Math.round(currentAsset.weather_risk) },
    { subject: 'Grid Impact', value: Math.round(currentAsset.grid_impact) },
    { subject: 'Priority Score', value: Math.round(currentAsset.priority_score) },
    { subject: 'Operating Load', value: Math.round(currentAsset.load) },
    { subject: 'Asset Health', value: Math.round(currentAsset.health) },
  ];

  const handleDispatch = () => {
    setDispatchConfirmed(true);
    setTimeout(() => setDispatchConfirmed(false), 3500);
  };

  return (
    <div className="page-content">
      
      {/* Top Selector & Asset Overview Strip */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={20} color="#38bdf8" />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Select Grid Asset:</span>
          </div>

          <select 
            className="form-select"
            value={currentAsset.equipment_id}
            onChange={(e) => onSelectEquipment(e.target.value)}
            style={{ minWidth: '180px', fontWeight: 600 }}
          >
            {predictions.map((p) => (
              <option key={p.equipment_id} value={p.equipment_id}>
                {p.equipment_id} — {p.type} ({p.risk_level} {p.priority_score.toFixed(1)})
              </option>
            ))}
          </select>

          <span className={`badge badge-${currentAsset.risk_level.toLowerCase()}`}>
            {currentAsset.risk_level} RISK
          </span>

          {currentAsset.critical_facility === 1 && (
            <span className="badge badge-critical">
              <Building2 size={13} /> Critical Facility Link
            </span>
          )}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '18px' }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Priority Score</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: getRiskColor(currentAsset.risk_level) }}>
              {currentAsset.priority_score.toFixed(1)} / 100
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Action Required</div>
            <div style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-bright)' }}>
              {currentAsset.maintenance_action}
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Telemetry + Radar + Explainability */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Left Column: Asset Telemetry Specs */}
        <div className="glass-panel" style={{ gridColumn: 'span 4' }}>
          <h3 style={{ margin: 0, fontSize: '0.95rem', marginBottom: '1rem' }}>Physical & Operational Telemetry</h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Equipment Type</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>{currentAsset.type}</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Service Age</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>{currentAsset.age} Years</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Health Score</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: currentAsset.health < 40 ? '#ef4444' : '#10b981', marginTop: '2px' }}>
                {currentAsset.health} / 100
              </div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Operating Load</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: currentAsset.load > 75 ? '#f97316' : '#38bdf8', marginTop: '2px' }}>
                {currentAsset.load}%
              </div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Operating Temp</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: currentAsset.temperature > 75 ? '#ef4444' : '#fff', marginTop: '2px' }}>
                {currentAsset.temperature}°C
              </div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Rated Voltage</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>{currentAsset.voltage} kV</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Customers Served</div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>{currentAsset.customers_served.toLocaleString()}</div>
            </div>

            <div style={{ padding: '10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>GIS Coordinates</div>
              <div style={{ fontSize: '0.78rem', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)', marginTop: '4px' }}>
                {currentAsset.latitude.toFixed(4)}, {currentAsset.longitude.toFixed(4)}
              </div>
            </div>
          </div>

          {/* Environmental Conditions */}
          <div style={{ marginTop: '1rem', padding: '10px', background: 'rgba(56, 189, 248, 0.05)', borderRadius: '8px', border: '1px solid rgba(56, 189, 248, 0.2)' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', marginBottom: '6px' }}>Local Zone Weather Telemetry</div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>Rain: {currentAsset.weather_rainfall} mm</span>
              <span>Wind: {currentAsset.weather_wind} km/h</span>
              <span>Temp: {currentAsset.weather_temperature}°C</span>
              <span>Storm: {currentAsset.weather_storm > 0 ? 'Active' : 'None'}</span>
            </div>
          </div>
        </div>

        {/* Middle Column: Radar Health & Operational Signature */}
        <div className="glass-panel" style={{ gridColumn: 'span 4' }}>
          <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Multi-Signal Operational Signature</h3>
          <p className="subtitle" style={{ marginBottom: '0.5rem' }}>Normalized 6-vector risk geometry</p>
          <div style={{ height: '270px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
                <PolarGrid stroke="rgba(255,255,255,0.12)" />
                <PolarAngleAxis dataKey="subject" stroke="var(--text-muted)" tick={{ fontSize: 11 }} />
                <PolarRadiusAxis domain={[0, 100]} stroke="rgba(255,255,255,0.2)" />
                <Radar 
                  name={currentAsset.equipment_id} 
                  dataKey="value" 
                  stroke={getRiskColor(currentAsset.risk_level)} 
                  fill={getRiskColor(currentAsset.risk_level)} 
                  fillOpacity={0.4} 
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right Column: AI Explainability Decision Card */}
        <div className="glass-panel" style={{ gridColumn: 'span 4', display: 'flex', flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.5rem' }}>
            <Sparkles size={18} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: '0.95rem' }}>AI Decision Explainability</h3>
          </div>
          <p className="subtitle" style={{ marginBottom: '1rem' }}>
            Deterministic rule-grounded threshold evaluation (Zero hallucination)
          </p>

          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px', overflowY: 'auto' }}>
            {currentAsset.risk_reasons && currentAsset.risk_reasons.length > 0 ? (
              currentAsset.risk_reasons.map((reason, idx) => (
                <div 
                  key={idx}
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '10px',
                    padding: '8px 12px',
                    background: 'rgba(239, 68, 68, 0.08)',
                    border: '1px solid rgba(239, 68, 68, 0.25)',
                    borderRadius: '8px',
                    fontSize: '0.8rem',
                    color: 'var(--text-bright)'
                  }}
                >
                  <AlertTriangle size={15} color="#ef4444" style={{ flexShrink: 0, marginTop: '2px' }} />
                  <span>{reason}</span>
                </div>
              ))
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', color: '#10b981', fontSize: '0.825rem' }}>
                <CheckCircle2 size={16} />
                <span>All parameters within standard operating thresholds.</span>
              </div>
            )}
          </div>

          {/* Assigned Crew & Dispatch */}
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Assigned Field Crew:</span>
              <strong style={{ color: '#38bdf8', fontSize: '0.85rem' }}>
                {currentAsset.assigned_crew}
              </strong>
            </div>

            {currentAsset.crew_distance_km !== null && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                <span>Haversine Transit Distance:</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{currentAsset.crew_distance_km} km</span>
              </div>
            )}

            <button 
              className={`btn ${dispatchConfirmed ? 'btn-secondary' : 'btn-primary'}`} 
              style={{ width: '100%' }}
              onClick={handleDispatch}
              disabled={dispatchConfirmed || currentAsset.assigned_crew === 'N/A - below threshold'}
            >
              {dispatchConfirmed ? (
                <>
                  <CheckCircle2 size={15} color="#10b981" />
                  <span>Dispatch Order Broadcasted to Crew!</span>
                </>
              ) : (
                <>
                  <Send size={14} />
                  <span>Dispatch Crew {currentAsset.assigned_crew}</span>
                </>
              )}
            </button>
          </div>
        </div>

      </div>

    </div>
  );
};
