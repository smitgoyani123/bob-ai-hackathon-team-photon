import { useState, useMemo } from 'react';
import { 
  ShieldAlert, 
  Check, 
  CheckCheck, 
  ExternalLink, 
  Filter, 
  Building2,
  FileSpreadsheet,
  FileCode
} from 'lucide-react';
import type { Equipment } from '../types/grid';

interface AlertCenterPageProps {
  predictions: Equipment[];
  onSelectEquipment: (id: string) => void;
  onNavigateToEquipment: () => void;
}

export const AlertCenterPage = ({
  predictions,
  onSelectEquipment,
  onNavigateToEquipment,
}: AlertCenterPageProps) => {
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [acknowledgedMap, setAcknowledgedMap] = useState<Record<string, boolean>>({});

  const allAlerts = useMemo(() => {
    return predictions.filter(p => p.risk_level === 'CRITICAL' || p.risk_level === 'HIGH' || p.risk_level === 'MEDIUM')
      .sort((a, b) => b.priority_score - a.priority_score);
  }, [predictions]);

  const filteredAlerts = useMemo(() => {
    return allAlerts.filter(a => {
      if (severityFilter === 'UNACK' && acknowledgedMap[a.equipment_id]) return false;
      if (severityFilter !== 'ALL' && severityFilter !== 'UNACK' && a.risk_level !== severityFilter) return false;
      return true;
    });
  }, [allAlerts, severityFilter, acknowledgedMap]);

  const handleToggleAcknowledge = (id: string) => {
    setAcknowledgedMap(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const handleAcknowledgeAll = () => {
    const updated: Record<string, boolean> = {};
    allAlerts.forEach(a => { updated[a.equipment_id] = true; });
    setAcknowledgedMap(updated);
  };

  const handleExportCSV = () => {
    if (predictions.length === 0) return;
    const headers = [
      'equipment_id', 'type', 'risk_level', 'priority_score', 
      'failure_probability', 'weather_risk', 'grid_impact', 
      'maintenance_action', 'assigned_crew', 'crew_distance_km'
    ];
    const rows = predictions.map(p => [
      p.equipment_id,
      p.type,
      p.risk_level,
      p.priority_score,
      (p.failure_probability * 100).toFixed(1) + '%',
      p.weather_risk,
      p.grid_impact,
      `"${p.maintenance_action}"`,
      p.assigned_crew,
      p.crew_distance_km ?? ''
    ]);

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `gridguard_operational_report_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(predictions, null, 2));
    const link = document.createElement('a');
    link.setAttribute('href', dataStr);
    link.setAttribute('download', `gridguard_predictions_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="page-content">
      
      {/* Alert Header Toolbar */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Filter size={16} color="#38bdf8" />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Filter Severity:</span>
          </div>

          <select 
            className="form-select"
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
          >
            <option value="ALL">All Grid Alerts ({allAlerts.length})</option>
            <option value="UNACK">Unacknowledged</option>
            <option value="CRITICAL">Critical Severity Only</option>
            <option value="HIGH">High Severity Only</option>
            <option value="MEDIUM">Medium Warnings</option>
          </select>

          <button className="btn btn-secondary btn-sm" onClick={handleAcknowledgeAll}>
            <CheckCheck size={14} />
            <span>Acknowledge All</span>
          </button>
        </div>

        {/* Export Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <button className="btn btn-secondary btn-sm" onClick={handleExportCSV}>
            <FileSpreadsheet size={14} color="#10b981" />
            <span>Export CSV Report</span>
          </button>

          <button className="btn btn-secondary btn-sm" onClick={handleExportJSON}>
            <FileCode size={14} color="#38bdf8" />
            <span>Export JSON Telemetry</span>
          </button>
        </div>
      </div>

      {/* Alerts Feed List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {filteredAlerts.length === 0 ? (
          <div className="glass-panel" style={{ textAlign: 'center', padding: '3rem' }}>
            <ShieldAlert size={36} color="var(--color-low)" style={{ margin: '0 auto 12px' }} />
            <h3>No Active Alerts for Current Filter</h3>
            <p className="subtitle">All high and critical risk grid conditions have been acknowledged or resolved.</p>
          </div>
        ) : (
          filteredAlerts.map((alert) => {
            const isAck = !!acknowledgedMap[alert.equipment_id];
            return (
              <div 
                key={alert.equipment_id}
                className="glass-panel"
                style={{
                  padding: '1.25rem',
                  display: 'flex',
                  alignItems: 'flex-start',
                  justifyContent: 'space-between',
                  borderLeft: `5px solid ${alert.risk_level === 'CRITICAL' ? '#ef4444' : alert.risk_level === 'HIGH' ? '#f97316' : '#eab308'}`,
                  opacity: isAck ? 0.75 : 1,
                  background: isAck ? 'rgba(15, 23, 42, 0.4)' : undefined,
                  gap: '16px',
                  flexWrap: 'wrap'
                }}
              >
                {/* Left Info */}
                <div style={{ flex: '1 1 400px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '1.05rem', fontWeight: 800, color: '#fff', fontFamily: 'var(--font-mono)' }}>
                      {alert.equipment_id}
                    </span>
                    <span className={`badge badge-${alert.risk_level.toLowerCase()}`}>
                      {alert.risk_level} ALERT
                    </span>
                    {alert.critical_facility === 1 && (
                      <span className="badge badge-critical" style={{ fontSize: '0.68rem' }}>
                        <Building2 size={12} /> Critical Facility (Hospital/Metro)
                      </span>
                    )}
                    {isAck && (
                      <span className="badge badge-low" style={{ fontSize: '0.68rem' }}>
                        <Check size={12} /> Acknowledged
                      </span>
                    )}
                  </div>

                  <div style={{ fontSize: '0.825rem', color: 'var(--text-bright)', marginBottom: '8px' }}>
                    {alert.type} • Priority Score: <strong style={{ color: alert.risk_level === 'CRITICAL' ? '#ef4444' : '#f97316' }}>{alert.priority_score}</strong> • Failure Probability: <strong>{(alert.failure_probability * 100).toFixed(1)}%</strong>
                  </div>

                  {/* Risk Reasons */}
                  {alert.risk_reasons && alert.risk_reasons.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                      {alert.risk_reasons.slice(0, 3).map((r, i) => (
                        <span key={i} style={{ fontSize: '0.72rem', padding: '3px 8px', background: 'rgba(255,255,255,0.04)', borderRadius: '4px', border: '1px solid var(--border-subtle)', color: 'var(--text-muted)' }}>
                          • {r}
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                    Serving {alert.customers_served.toLocaleString()} customers • Weather Risk: {alert.weather_risk} • Grid Impact: {alert.grid_impact}
                  </div>
                </div>

                {/* Right Dispatch & Action Controls */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>Recommended Action</div>
                    <div style={{ fontSize: '0.85rem', fontWeight: 700, color: alert.risk_level === 'CRITICAL' ? '#ef4444' : '#f97316' }}>
                      {alert.maintenance_action}
                    </div>
                  </div>

                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                    Crew: <strong style={{ color: '#38bdf8' }}>{alert.assigned_crew}</strong> ({alert.crew_distance_km ?? '—'} km)
                  </div>

                  <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => handleToggleAcknowledge(alert.equipment_id)}
                    >
                      <Check size={14} color={isAck ? '#10b981' : undefined} />
                      <span>{isAck ? 'Unmark' : 'Acknowledge'}</span>
                    </button>

                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => {
                        onSelectEquipment(alert.equipment_id);
                        onNavigateToEquipment();
                      }}
                    >
                      <ExternalLink size={14} />
                      <span>Investigate</span>
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

    </div>
  );
};
