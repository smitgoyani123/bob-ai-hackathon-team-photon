import React, { useState, useMemo } from 'react';
import { 
  Search, 
  ArrowUpDown, 
  ExternalLink, 
  Building2
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell
} from 'recharts';
import type { Equipment } from '../types/grid';

interface RiskCommandPageProps {
  predictions: Equipment[];
  onSelectEquipment: (id: string) => void;
  onNavigateToEquipment: () => void;
}

type SortField = 'priority_score' | 'failure_probability' | 'weather_risk' | 'grid_impact' | 'equipment_id';
type SortOrder = 'asc' | 'desc';

export const RiskCommandPage: React.FC<RiskCommandPageProps> = ({
  predictions,
  onSelectEquipment,
  onNavigateToEquipment,
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('ALL');
  const [typeFilter, setTypeFilter] = useState<string>('ALL');
  const [criticalFacilityOnly, setCriticalFacilityOnly] = useState(false);
  
  const [sortField, setSortField] = useState<SortField>('priority_score');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const filteredPredictions = useMemo(() => {
    return predictions.filter((p) => {
      if (searchTerm) {
        const query = searchTerm.toLowerCase();
        const matchesId = p.equipment_id.toLowerCase().includes(query);
        const matchesType = p.type.toLowerCase().includes(query);
        const matchesAction = p.maintenance_action.toLowerCase().includes(query);
        if (!matchesId && !matchesType && !matchesAction) return false;
      }
      if (riskFilter !== 'ALL' && p.risk_level !== riskFilter) return false;
      if (typeFilter !== 'ALL' && p.type.toLowerCase() !== typeFilter.toLowerCase()) return false;
      if (criticalFacilityOnly && p.critical_facility !== 1) return false;
      return true;
    }).sort((a, b) => {
      const valA = a[sortField];
      const valB = b[sortField];
      if (typeof valA === 'string') {
        return sortOrder === 'asc' ? valA.localeCompare(valB as string) : (valB as string).localeCompare(valA);
      }
      return sortOrder === 'asc' ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
    });
  }, [predictions, searchTerm, riskFilter, typeFilter, criticalFacilityOnly, sortField, sortOrder]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('desc');
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

  const typeAggregates = useMemo(() => {
    const types = ['Transformer', 'Switch', 'Line'];
    return types.map(t => {
      const items = predictions.filter(p => p.type.toLowerCase() === t.toLowerCase());
      const highOrCrit = items.filter(p => p.risk_level === 'HIGH' || p.risk_level === 'CRITICAL').length;
      const avgPriority = items.length > 0
        ? Math.round(items.reduce((acc, p) => acc + p.priority_score, 0) / items.length)
        : 0;
      return {
        type: t,
        total: items.length,
        highOrCrit,
        avgPriority
      };
    });
  }, [predictions]);

  return (
    <div className="page-content">
      {/* Top Filter Toolbar */}
      <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
          
          {/* Search Box */}
          <div style={{ position: 'relative', minWidth: '240px', flex: '1 1 240px' }}>
            <Search size={16} color="var(--text-dim)" style={{ position: 'absolute', left: 12, top: 11 }} />
            <input 
              type="text"
              className="form-input"
              style={{ width: '100%', paddingLeft: '36px' }}
              placeholder="Search by Asset ID, Type, Action..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* Risk Level Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Risk:</span>
            <select 
              className="form-select"
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
            >
              <option value="ALL">All Risk Levels</option>
              <option value="CRITICAL">Critical (80-100)</option>
              <option value="HIGH">High (60-80)</option>
              <option value="MEDIUM">Medium (30-60)</option>
              <option value="LOW">Low (0-30)</option>
            </select>
          </div>

          {/* Equipment Type Filter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Type:</span>
            <select 
              className="form-select"
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
            >
              <option value="ALL">All Types</option>
              <option value="Transformer">Transformers</option>
              <option value="Switch">Switches</option>
              <option value="Line">Transmission Lines</option>
            </select>
          </div>

          {/* Critical Facility Toggle */}
          <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <input 
              type="checkbox"
              checked={criticalFacilityOnly}
              onChange={(e) => setCriticalFacilityOnly(e.target.checked)}
              style={{ accentColor: '#38bdf8', width: '16px', height: '16px' }}
            />
            <Building2 size={16} color={criticalFacilityOnly ? '#38bdf8' : 'var(--text-dim)'} />
            <span>Critical Facility Only</span>
          </label>

          <div style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
            Showing <strong>{filteredPredictions.length}</strong> of {predictions.length} Assets
          </div>
        </div>
      </div>

      {/* Analytical Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Risk Distribution by Equipment Type */}
        <div className="glass-panel" style={{ gridColumn: 'span 5', height: '300px' }}>
          <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Risk Profile by Asset Class</h3>
          <p className="subtitle" style={{ marginBottom: '0.75rem' }}>Asset count vs high/critical risk count</p>
          <ResponsiveContainer width="100%" height="80%">
            <BarChart data={typeAggregates} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="type" stroke="var(--text-dim)" />
              <YAxis stroke="var(--text-dim)" />
              <Tooltip 
                contentStyle={{ background: '#0c1322', border: '1px solid var(--border-glow)', borderRadius: '8px' }}
              />
              <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: '8px' }} />
              <Bar dataKey="total" fill="#38bdf8" name="Total Monitored" radius={[4, 4, 0, 0]} />
              <Bar dataKey="highOrCrit" fill="#f97316" name="High/Critical Risk" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* 2D Risk Dispersion Plot */}
        <div className="glass-panel" style={{ gridColumn: 'span 7', height: '300px' }}>
          <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Failure Probability vs Grid Impact</h3>
          <p className="subtitle" style={{ marginBottom: '0.75rem' }}>X: Failure Probability • Y: Grid Consequence Score • Size: Weather Risk</p>
          <ResponsiveContainer width="100%" height="80%">
            <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: -10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis 
                type="number" 
                dataKey="failure_probability" 
                name="Failure Prob" 
                stroke="var(--text-dim)"
                domain={[0, 1]}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
              />
              <YAxis 
                type="number" 
                dataKey="grid_impact" 
                name="Grid Impact" 
                stroke="var(--text-dim)"
                domain={[0, 100]}
              />
              <ZAxis type="number" dataKey="weather_risk" range={[60, 360]} />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload as Equipment;
                    return (
                      <div style={{ background: '#0c1322', border: '1px solid var(--border-glow)', borderRadius: '8px', padding: '8px 12px' }}>
                        <div style={{ fontWeight: 700, color: '#fff' }}>{d.equipment_id} ({d.type})</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Failure Prob: {(d.failure_probability * 100).toFixed(1)}%</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Grid Impact: {d.grid_impact}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Weather Risk: {d.weather_risk}</div>
                        <div style={{ fontSize: '0.75rem', color: '#f97316' }}>Priority Score: {d.priority_score}</div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter data={filteredPredictions}>
                {filteredPredictions.map((entry, idx) => (
                  <Cell 
                    key={`sc-${idx}`} 
                    fill={getRiskColor(entry.risk_level)} 
                    style={{ cursor: 'pointer' }}
                    onClick={() => {
                      onSelectEquipment(entry.equipment_id);
                      onNavigateToEquipment();
                    }}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>

      </div>

      {/* Main Prioritized Equipment Table */}
      <div className="glass-panel" style={{ padding: '1rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '1rem' }}>Asset Priority Hierarchy</h3>
            <p className="subtitle">Click any asset row to view complete AI Explainability and Dispatch Card</p>
          </div>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th onClick={() => handleSort('equipment_id')} style={{ cursor: 'pointer' }}>
                  Asset ID <ArrowUpDown size={12} />
                </th>
                <th>Type</th>
                <th>Risk Level</th>
                <th onClick={() => handleSort('priority_score')} style={{ cursor: 'pointer' }}>
                  Priority <ArrowUpDown size={12} />
                </th>
                <th onClick={() => handleSort('failure_probability')} style={{ cursor: 'pointer' }}>
                  Failure Prob <ArrowUpDown size={12} />
                </th>
                <th onClick={() => handleSort('weather_risk')} style={{ cursor: 'pointer' }}>
                  Weather Risk <ArrowUpDown size={12} />
                </th>
                <th onClick={() => handleSort('grid_impact')} style={{ cursor: 'pointer' }}>
                  Grid Impact <ArrowUpDown size={12} />
                </th>
                <th>Recommended Action</th>
                <th>Assigned Crew</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredPredictions.map((item) => (
                <tr 
                  key={item.equipment_id}
                  onClick={() => {
                    onSelectEquipment(item.equipment_id);
                    onNavigateToEquipment();
                  }}
                >
                  <td style={{ color: 'var(--text-bright)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span>{item.equipment_id}</span>
                      {item.critical_facility === 1 && (
                        <span title="Powers Critical Facility (Hospital/Metro)">
                          <Building2 size={13} color="#fde047" />
                        </span>
                      )}
                    </div>
                  </td>
                  <td>{item.type}</td>
                  <td>
                    <span className={`badge badge-${item.risk_level.toLowerCase()}`}>
                      {item.risk_level}
                    </span>
                  </td>
                  <td>
                    <span style={{ 
                      fontFamily: 'var(--font-mono)', 
                      fontWeight: 700, 
                      fontSize: '0.95rem',
                      color: getRiskColor(item.risk_level) 
                    }}>
                      {item.priority_score.toFixed(1)}
                    </span>
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>
                    {(item.failure_probability * 100).toFixed(1)}%
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>
                    {item.weather_risk.toFixed(1)}
                  </td>
                  <td style={{ fontFamily: 'var(--font-mono)' }}>
                    {item.grid_impact.toFixed(1)}
                  </td>
                  <td>
                    <span style={{ 
                      color: item.maintenance_action === 'Immediate Inspection' ? '#ef4444' : 
                             item.maintenance_action === 'Preventive Maintenance' ? '#f97316' : 
                             item.maintenance_action === 'Monitor' ? '#fde047' : '#86efac',
                      fontSize: '0.78rem',
                      fontWeight: 600
                    }}>
                      {item.maintenance_action}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.78rem' }}>
                    {item.assigned_crew !== 'N/A - below threshold' && item.assigned_crew !== 'No suitable crew available' ? (
                      <span style={{ color: '#38bdf8', fontWeight: 600 }}>
                        {item.assigned_crew} ({item.crew_distance_km ?? '—'} km)
                      </span>
                    ) : (
                      <span style={{ color: 'var(--text-dim)' }}>{item.assigned_crew}</span>
                    )}
                  </td>
                  <td>
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectEquipment(item.equipment_id);
                        onNavigateToEquipment();
                      }}
                    >
                      <ExternalLink size={12} />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
