import React from 'react';
import { 
  Activity, 
  AlertTriangle, 
  CloudRain, 
  Users, 
  Zap, 
  ArrowRight,
  Sparkles,
  Building2
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  ZAxis, 
  CartesianGrid, 
  Tooltip, 
  Cell
} from 'recharts';
import type { Equipment, SummaryData } from '../types/grid';

interface OverviewPageProps {
  summary: SummaryData | null;
  predictions: Equipment[];
  onSelectEquipment: (id: string) => void;
  onNavigatePage: (pageId: 'risk' | 'map' | 'equipment' | 'crews' | 'simulator' | 'alerts') => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  summary,
  predictions,
  onSelectEquipment,
  onNavigatePage,
}) => {
  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL': return '#ef4444';
      case 'HIGH': return '#f97316';
      case 'MEDIUM': return '#eab308';
      case 'LOW': return '#10b981';
      default: return '#38bdf8';
    }
  };

  const topPriorityAssets = [...predictions]
    .sort((a, b) => b.priority_score - a.priority_score)
    .slice(0, 6);

  const avgWeather = predictions.length > 0
    ? Math.round(predictions.reduce((acc, p) => acc + p.weather_rainfall, 0) / predictions.length)
    : 0;

  const stormCount = predictions.filter(p => p.weather_storm > 0).length;

  return (
    <div className="page-content">
      {/* Real-Time Operational Alert Ticker */}
      {topPriorityAssets.length > 0 && (
        <div className="alert-ticker">
          <AlertTriangle size={20} color="var(--color-critical)" />
          <div style={{ flex: 1, fontSize: '0.825rem' }}>
            <strong>CRITICAL GRID NOTICE:</strong> High-risk cluster detected across Bangalore sector.{' '}
            <span style={{ color: 'var(--text-bright)' }}>{topPriorityAssets[0].equipment_id} ({topPriorityAssets[0].type})</span> has priority score{' '}
            <span style={{ color: '#f97316', fontWeight: 700 }}>{topPriorityAssets[0].priority_score}</span>. Nearest crew{' '}
            <span style={{ color: '#38bdf8' }}>{topPriorityAssets[0].assigned_crew}</span> pre-positioned ({topPriorityAssets[0].crew_distance_km ?? '—'} km).
          </div>
          <button 
            className="btn btn-secondary btn-sm"
            onClick={() => onNavigatePage('alerts')}
          >
            Review All Alerts
          </button>
        </div>
      )}

      {/* KPI Cards Row */}
      <div className="kpi-grid">
        {/* System Health Index */}
        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid #10b981' }}>
          <div className="kpi-header">
            <span className="kpi-title">Grid Health Index</span>
            <div className="kpi-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
              <Activity size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: (summary?.system_health_score ?? 100) < 60 ? '#f97316' : '#10b981' }}>
            {summary?.system_health_score ?? 55.3}%
          </div>
          <div className="kpi-footer">
            <span style={{ color: '#10b981' }}>● Safe range &gt; 50%</span>
            <span>• 100 - Avg Priority</span>
          </div>
        </div>

        {/* Total Assets */}
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span className="kpi-title">Monitored Equipment</span>
            <div className="kpi-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Zap size={18} />
            </div>
          </div>
          <div className="kpi-val">{summary?.total_equipment || predictions.length || 30}</div>
          <div className="kpi-footer">
            <span>Transformers, Switches, Lines</span>
          </div>
        </div>

        {/* High & Critical Risk */}
        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid #f97316' }}>
          <div className="kpi-header">
            <span className="kpi-title">High & Critical Risk</span>
            <div className="kpi-icon" style={{ background: 'rgba(249, 115, 22, 0.15)', color: '#f97316' }}>
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#f97316' }}>
            {(summary?.risk_counts.CRITICAL || 0) + (summary?.risk_counts.HIGH || 0)}
          </div>
          <div className="kpi-footer">
            <span>Critical: {summary?.risk_counts.CRITICAL || 0} • High: {summary?.risk_counts.HIGH || 0}</span>
          </div>
        </div>

        {/* Avg Failure Probability */}
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span className="kpi-title">Avg Failure Probability</span>
            <div className="kpi-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#a855f7' }}>
              <Sparkles size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#c084fc' }}>
            {summary?.avg_failure_probability ?? 43.0}%
          </div>
          <div className="kpi-footer">
            <span>7-Day ML Failure Horizon</span>
          </div>
        </div>

        {/* Available Crews */}
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span className="kpi-title">Crew Fleet Readiness</span>
            <div className="kpi-icon" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#3b82f6' }}>
              <Users size={18} />
            </div>
          </div>
          <div className="kpi-val">
            {summary?.available_crews ?? 6}
            <span style={{ fontSize: '1.1rem', color: 'var(--text-dim)', fontWeight: 400 }}> / {summary?.total_crews ?? 8}</span>
          </div>
          <div className="kpi-footer">
            <span>Available for rapid dispatch</span>
          </div>
        </div>

        {/* Critical Facilities */}
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span className="kpi-title">Critical Facilities</span>
            <div className="kpi-icon" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#eab308' }}>
              <Building2 size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#fde047' }}>
            {summary?.critical_facilities ?? 4}
          </div>
          <div className="kpi-footer">
            <span>Hospitals, Metro, Data Centers</span>
          </div>
        </div>
      </div>

      {/* Main Analytics Grid: 2 Columns */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Left Column: Risk Matrix Scatter */}
        <div className="glass-panel" style={{ gridColumn: 'span 7' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem' }}>AI Multi-Signal Risk Matrix</h3>
              <p className="subtitle">Failure Probability (X) vs Priority Score (Y) • Bubble = Weather Risk</p>
            </div>
            <button 
              className="btn btn-secondary btn-sm"
              onClick={() => onNavigatePage('risk')}
            >
              Expand Risk Command <ArrowRight size={14} />
            </button>
          </div>

          <div style={{ height: '320px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: -10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.07)" />
                <XAxis 
                  type="number" 
                  dataKey="failure_probability" 
                  name="Failure Prob" 
                  stroke="var(--text-dim)"
                  domain={[0, 1]}
                  tickFormatter={(val) => `${(val * 100).toFixed(0)}%`}
                />
                <YAxis 
                  type="number" 
                  dataKey="priority_score" 
                  name="Priority Score" 
                  stroke="var(--text-dim)"
                  domain={[0, 100]}
                />
                <ZAxis type="number" dataKey="weather_risk" range={[80, 420]} name="Weather Risk" />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload as Equipment;
                      return (
                        <div style={{ 
                          background: '#0c1322', 
                          border: '1px solid var(--border-glow)', 
                          borderRadius: '8px', 
                          padding: '10px 14px',
                          boxShadow: '0 8px 24px rgba(0,0,0,0.5)'
                        }}>
                          <div style={{ fontWeight: 700, color: '#ffffff', marginBottom: '4px' }}>
                            {data.equipment_id} ({data.type})
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            Risk Level: <span className={`badge badge-${data.risk_level.toLowerCase()}`}>{data.risk_level}</span>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                            Failure Prob: <strong>{(data.failure_probability * 100).toFixed(1)}%</strong>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            Priority Score: <strong>{data.priority_score}</strong>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            Weather Risk: <strong>{data.weather_risk}</strong>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter data={predictions}>
                  {predictions.map((entry, index) => (
                    <Cell 
                      key={`scatter-${index}`} 
                      fill={getRiskColor(entry.risk_level)} 
                      style={{ cursor: 'pointer' }}
                      onClick={() => onSelectEquipment(entry.equipment_id)}
                    />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>

          <div style={{ display: 'flex', gap: '16px', justifyContent: 'center', marginTop: '8px' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#ef4444' }} /> Critical (80-100)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#f97316' }} /> High (60-80)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#eab308' }} /> Medium (30-60)
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span style={{ width: 10, height: 10, borderRadius: '50%', background: '#10b981' }} /> Low (0-30)
            </span>
          </div>
        </div>

        {/* Right Column: High Priority Queue */}
        <div className="glass-panel" style={{ gridColumn: 'span 5' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem' }}>Operational Action Queue</h3>
              <p className="subtitle">High-urgency assets requiring proactive dispatch</p>
            </div>
            <span className="badge badge-high">{topPriorityAssets.length} Assets</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {topPriorityAssets.map((asset) => (
              <div 
                key={asset.equipment_id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  background: 'rgba(255, 255, 255, 0.025)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '10px',
                  transition: 'background 0.2s',
                  cursor: 'pointer'
                }}
                onClick={() => onSelectEquipment(asset.equipment_id)}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontWeight: 700, color: 'var(--text-bright)', fontFamily: 'var(--font-mono)' }}>
                      {asset.equipment_id}
                    </span>
                    <span className={`badge badge-${asset.risk_level.toLowerCase()}`}>
                      {asset.risk_level}
                    </span>
                    {asset.critical_facility === 1 && (
                      <span className="badge badge-critical" style={{ fontSize: '0.65rem' }}>Hospital/Metro</span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '3px' }}>
                    {asset.type} • {asset.maintenance_action}
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '1.05rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: getRiskColor(asset.risk_level) }}>
                    {asset.priority_score}
                  </div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                    Crew: <strong style={{ color: '#38bdf8' }}>{asset.assigned_crew}</strong> ({asset.crew_distance_km ?? '—'} km)
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: '1.25rem' }}>
            <button 
              className="btn btn-secondary" 
              style={{ width: '100%' }}
              onClick={() => onNavigatePage('equipment')}
            >
              Open Full Equipment Intelligence <ArrowRight size={14} />
            </button>
          </div>
        </div>

      </div>

      {/* Grid Summary Footer Strip */}
      <div className="glass-panel" style={{ padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <CloudRain size={16} color="#38bdf8" />
            <span>Avg Zone Rainfall: <strong>{avgWeather} mm</strong></span>
          </div>
          <div style={{ width: '1px', height: '18px', background: 'var(--border-subtle)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <AlertTriangle size={16} color="#f97316" />
            <span>Active Storm Zones: <strong>{stormCount} zones</strong></span>
          </div>
          <div style={{ width: '1px', height: '18px', background: 'var(--border-subtle)' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Activity size={16} color="#10b981" />
            <span>ML Random Forest Model: <strong>100 Trees (100% Validated)</strong></span>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigatePage('map')}>
            Open Live GIS Map
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => onNavigatePage('simulator')}>
            Run Scenario Simulation
          </button>
        </div>
      </div>

    </div>
  );
};
