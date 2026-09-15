import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  RotateCcw, 
  Cpu
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';
import type { Equipment, FeatureImportance } from '../types/grid';

interface AiInsightsPageProps {
  predictions: Equipment[];
  featureImportance: FeatureImportance[];
  selectedId: string;
  onSelectEquipment: (id: string) => void;
}

export const AiInsightsPage: React.FC<AiInsightsPageProps> = ({
  predictions,
  featureImportance,
  selectedId,
  onSelectEquipment,
}) => {
  const currentAsset = predictions.find(p => p.equipment_id === selectedId) || predictions[0];

  const [simWind, setSimWind] = useState(currentAsset ? currentAsset.weather_wind : 45);
  const [simRain, setSimRain] = useState(currentAsset ? currentAsset.weather_rainfall : 25);
  const [simTemp, setSimTemp] = useState(currentAsset ? currentAsset.weather_temperature : 35);
  const [simLoad, setSimLoad] = useState(currentAsset ? currentAsset.load : 65);
  const [simStorm, setSimStorm] = useState(currentAsset ? currentAsset.weather_storm : 0);
  const [simFlood, setSimFlood] = useState(currentAsset ? currentAsset.weather_flood_risk : 0.2);

  useEffect(() => {
    if (currentAsset) {
      setSimWind(currentAsset.weather_wind);
      setSimRain(currentAsset.weather_rainfall);
      setSimTemp(currentAsset.weather_temperature);
      setSimLoad(currentAsset.load);
      setSimStorm(currentAsset.weather_storm);
      setSimFlood(currentAsset.weather_flood_risk);
    }
  }, [currentAsset?.equipment_id]);

  const simulation = React.useMemo(() => {
    if (!currentAsset) return null;

    const EPS = 1e-9;
    const rainMin = 0.0;
    const rainMax = 120.0;
    const windMin = 0.0;
    const windMax = 90.0;

    const norm = (v: number, lo: number, hi: number) => 
      hi > lo ? ((v - lo) / (hi - lo + EPS)) * 100 : 50.0;

    const simRainR = norm(simRain, rainMin, rainMax);
    const simWindR = norm(simWind, windMin, windMax);
    const simTempR = Math.max(0, (simTemp - 35) / Math.max(1, 45 - 35)) * 100;
    const simStormR = simStorm * 60 + simFlood * 40;

    const simWr = Math.min(100, Math.max(0, 0.40 * simRainR + 0.30 * simWindR + 0.20 * simTempR + 0.10 * simStormR));

    const baseFp = currentAsset.failure_probability;
    const baseGi = currentAsset.grid_impact;
    const baseLoad = Math.max(1, currentAsset.load);

    const loadRatio = simLoad / baseLoad;
    const simGi = Math.min(100, Math.max(0, baseGi * loadRatio));

    const simPs = Math.min(100, Math.max(0, 0.50 * (baseFp * 100) + 0.20 * simWr + 0.30 * simGi));

    let simRisk = 'LOW';
    let simAction = 'Normal Maintenance';
    if (simPs >= 80) {
      simRisk = 'CRITICAL';
      simAction = 'Immediate Inspection';
    } else if (simPs >= 60) {
      simRisk = 'HIGH';
      simAction = 'Preventive Maintenance';
    } else if (simPs >= 30) {
      simRisk = 'MEDIUM';
      simAction = 'Monitor';
    }

    return {
      baseline: {
        priority: currentAsset.priority_score,
        weather: currentAsset.weather_risk,
        gridImpact: currentAsset.grid_impact,
        risk: currentAsset.risk_level,
        action: currentAsset.maintenance_action,
      },
      simulated: {
        priority: Math.round(simPs * 10) / 10,
        weather: Math.round(simWr * 10) / 10,
        gridImpact: Math.round(simGi * 10) / 10,
        risk: simRisk,
        action: simAction,
        priorityDelta: Math.round((simPs - currentAsset.priority_score) * 10) / 10,
        weatherDelta: Math.round((simWr - currentAsset.weather_risk) * 10) / 10,
        gridDelta: Math.round((simGi - currentAsset.grid_impact) * 10) / 10,
      }
    };
  }, [currentAsset, simWind, simRain, simTemp, simLoad, simStorm, simFlood]);

  const handleReset = () => {
    if (currentAsset) {
      setSimWind(currentAsset.weather_wind);
      setSimRain(currentAsset.weather_rainfall);
      setSimTemp(currentAsset.weather_temperature);
      setSimLoad(currentAsset.load);
      setSimStorm(currentAsset.weather_storm);
      setSimFlood(currentAsset.weather_flood_risk);
    }
  };

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#10b981';
      default: return '#38bdf8';
    }
  };

  return (
    <div className="page-content">
      
      {/* Top Model Architecture Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Model Specs Card */}
        <div className="glass-panel" style={{ gridColumn: 'span 4' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.5rem' }}>
            <Cpu size={18} color="#38bdf8" />
            <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Random Forest ML Core</h3>
          </div>
          <p className="subtitle" style={{ marginBottom: '1rem' }}>
            scikit-learn failure classifier predicting 7-day failure horizon
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.8rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-dim)' }}>Architecture:</span>
              <strong style={{ color: '#fff' }}>RandomForest (100 Trees)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-dim)' }}>Validation Accuracy:</span>
              <strong style={{ color: '#10b981' }}>1.00 (100%)</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-dim)' }}>Feature Vectors:</span>
              <strong style={{ color: '#38bdf8' }}>21 Engineered Features</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: '6px' }}>
              <span style={{ color: 'var(--text-dim)' }}>Class Balancing:</span>
              <strong style={{ color: '#fff' }}>Balanced Weights (Synthetic/Edge)</strong>
            </div>
          </div>
        </div>

        {/* Global Feature Importance Chart */}
        <div className="glass-panel" style={{ gridColumn: 'span 8', height: '240px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Global Feature Importance</h3>
              <p className="subtitle">Top predictive signals driving failure probability</p>
            </div>
            <span className="badge badge-cyan">Model Weights</span>
          </div>

          <div style={{ height: '170px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart 
                data={featureImportance.slice(0, 8)} 
                layout="vertical"
                margin={{ top: 5, right: 20, bottom: 5, left: 70 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="var(--text-dim)" domain={[0, 'auto']} />
                <YAxis 
                  type="category" 
                  dataKey="feature" 
                  stroke="var(--text-muted)" 
                  tick={{ fontSize: 11, fill: 'var(--text-muted)' }} 
                />
                <Tooltip 
                  contentStyle={{ background: '#0c1322', border: '1px solid var(--border-glow)', borderRadius: '8px' }}
                  formatter={(val: any) => [`${(Number(val) * 100).toFixed(1)}%`, 'Weight']}
                />
                <Bar dataKey="importance" fill="#38bdf8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Interactive What-If Scenario Simulator */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Sliders size={22} color="#38bdf8" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#fff' }}>Interactive What-If Scenario Simulator</h3>
              <p className="subtitle">Simulate extreme weather, load surges, or storm spikes to observe real-time priority escalation</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <select 
              className="form-select"
              value={currentAsset?.equipment_id}
              onChange={(e) => onSelectEquipment(e.target.value)}
              style={{ fontWeight: 600 }}
            >
              {predictions.map((p) => (
                <option key={p.equipment_id} value={p.equipment_id}>
                  Target: {p.equipment_id} ({p.type})
                </option>
              ))}
            </select>

            <button className="btn btn-secondary btn-sm" onClick={handleReset}>
              <RotateCcw size={14} />
              <span>Reset Baseline</span>
            </button>
          </div>
        </div>

        {/* Sliders Grid + Result Comparison */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.75rem' }}>
          
          {/* 6 Simulation Sliders */}
          <div style={{ gridColumn: 'span 7', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            {/* Wind */}
            <div className="slider-container">
              <div className="slider-label-row">
                <span>Wind Speed (km/h)</span>
                <span className="slider-val">{simWind.toFixed(1)} km/h</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="120" 
                step="1"
                value={simWind}
                onChange={(e) => setSimWind(parseFloat(e.target.value))}
              />
            </div>

            {/* Rainfall */}
            <div className="slider-container">
              <div className="slider-label-row">
                <span>Precipitation / Rainfall (mm)</span>
                <span className="slider-val">{simRain.toFixed(1)} mm</span>
              </div>
              <input 
                type="range" 
                min="0" 
                max="150" 
                step="1"
                value={simRain}
                onChange={(e) => setSimRain(parseFloat(e.target.value))}
              />
            </div>

            {/* Temperature */}
            <div className="slider-container">
              <div className="slider-label-row">
                <span>Operating Ambient Temp (°C)</span>
                <span className="slider-val">{simTemp.toFixed(1)} °C</span>
              </div>
              <input 
                type="range" 
                min="20" 
                max="50" 
                step="0.5"
                value={simTemp}
                onChange={(e) => setSimTemp(parseFloat(e.target.value))}
              />
            </div>

            {/* Load % */}
            <div className="slider-container">
              <div className="slider-label-row">
                <span>Equipment Grid Load (%)</span>
                <span className="slider-val">{simLoad.toFixed(1)} %</span>
              </div>
              <input 
                type="range" 
                min="10" 
                max="130" 
                step="1"
                value={simLoad}
                onChange={(e) => setSimLoad(parseFloat(e.target.value))}
              />
            </div>

            {/* Storm & Flood */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '4px' }}>
              <div className="slider-container">
                <div className="slider-label-row">
                  <span>Severe Storm Flag</span>
                  <span className="slider-val">{simStorm === 1 ? 'ACTIVE (1.0)' : 'NONE (0.0)'}</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="1"
                  value={simStorm}
                  onChange={(e) => setSimStorm(parseInt(e.target.value))}
                />
              </div>

              <div className="slider-container">
                <div className="slider-label-row">
                  <span>Flood Risk Factor</span>
                  <span className="slider-val">{simFlood.toFixed(2)}</span>
                </div>
                <input 
                  type="range" 
                  min="0" 
                  max="1" 
                  step="0.05"
                  value={simFlood}
                  onChange={(e) => setSimFlood(parseFloat(e.target.value))}
                />
              </div>
            </div>

          </div>

          {/* Live Dynamic Output Comparison Box */}
          {simulation && (
            <div style={{ gridColumn: 'span 5', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ padding: '1.25rem', background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-glow)', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)' }}>Simulated Priority Outcome</span>
                  <span className={`badge badge-${simulation.simulated.risk.toLowerCase()}`}>
                    {simulation.simulated.risk}
                  </span>
                </div>

                {/* Score Comparison */}
                <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Simulated Score</div>
                    <div style={{ fontSize: '2.2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: getRiskColor(simulation.simulated.risk) }}>
                      {simulation.simulated.priority}
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Baseline Score</div>
                    <div style={{ fontSize: '1.3rem', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                      {simulation.baseline.priority}
                    </div>
                  </div>
                </div>

                {/* Metric Deltas */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', paddingTop: '8px', borderTop: '1px solid var(--border-subtle)', fontSize: '0.78rem' }}>
                  <div>
                    <div style={{ color: 'var(--text-dim)' }}>Weather Risk:</div>
                    <div style={{ fontWeight: 700, color: '#38bdf8' }}>
                      {simulation.simulated.weather}{' '}
                      <span style={{ fontSize: '0.72rem', color: simulation.simulated.weatherDelta >= 0 ? '#f97316' : '#10b981' }}>
                        ({simulation.simulated.weatherDelta >= 0 ? '+' : ''}{simulation.simulated.weatherDelta})
                      </span>
                    </div>
                  </div>

                  <div>
                    <div style={{ color: 'var(--text-dim)' }}>Grid Impact:</div>
                    <div style={{ fontWeight: 700, color: '#f59e0b' }}>
                      {simulation.simulated.gridImpact}{' '}
                      <span style={{ fontSize: '0.72rem', color: simulation.simulated.gridDelta >= 0 ? '#f97316' : '#10b981' }}>
                        ({simulation.simulated.gridDelta >= 0 ? '+' : ''}{simulation.simulated.gridDelta})
                      </span>
                    </div>
                  </div>
                </div>

                {/* Action Escalation */}
                <div style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Escalated Operational Protocol:</div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#fff', marginTop: '2px' }}>
                    {simulation.simulated.action}
                  </div>
                </div>

              </div>
            </div>
          )}

        </div>

      </div>

    </div>
  );
};
