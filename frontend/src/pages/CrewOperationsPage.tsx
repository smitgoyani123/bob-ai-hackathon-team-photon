import React, { useState } from 'react';
import { 
  Users, 
  Wrench, 
  CheckCircle2, 
  Clock
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  PieChart, 
  Pie, 
  Cell, 
  Tooltip, 
  Legend 
} from 'recharts';
import type { Crew } from '../types/grid';

interface CrewOperationsPageProps {
  crews: Crew[];
  onSelectEquipment: (id: string) => void;
  onNavigateToEquipment: () => void;
}

export const CrewOperationsPage: React.FC<CrewOperationsPageProps> = ({
  crews,
  onSelectEquipment,
  onNavigateToEquipment,
}) => {
  const [filterSkill, setFilterSkill] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');

  const totalCrews = crews.length;
  const availableCrews = crews.filter(c => c.status.toLowerCase() === 'available').length;
  const busyCrews = crews.filter(c => c.status.toLowerCase() === 'busy').length;
  const totalAssignedAssets = crews.reduce((acc, c) => acc + c.assigned_count, 0);

  const skillCounts: Record<string, number> = {};
  crews.forEach((c) => {
    const s = c.skill.toLowerCase();
    skillCounts[s] = (skillCounts[s] || 0) + 1;
  });

  const skillPieData = Object.entries(skillCounts).map(([skill, count]) => ({
    name: skill.charAt(0).toUpperCase() + skill.slice(1),
    value: count,
  }));

  const SKILL_COLORS: Record<string, string> = {
    Electrical: '#38bdf8',
    Mechanical: '#f59e0b',
    Civil: '#10b981',
  };

  const filteredCrews = crews.filter((c) => {
    if (filterSkill !== 'ALL' && c.skill.toLowerCase() !== filterSkill.toLowerCase()) return false;
    if (filterStatus !== 'ALL' && c.status.toLowerCase() !== filterStatus.toLowerCase()) return false;
    return true;
  });

  return (
    <div className="page-content">
      
      {/* Fleet KPI Banner */}
      <div className="kpi-grid">
        <div className="glass-panel kpi-card">
          <div className="kpi-header">
            <span className="kpi-title">Total Field Fleet</span>
            <div className="kpi-icon" style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8' }}>
              <Users size={18} />
            </div>
          </div>
          <div className="kpi-val">{totalCrews}</div>
          <div className="kpi-footer">Across Bangalore Zones</div>
        </div>

        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid #10b981' }}>
          <div className="kpi-header">
            <span className="kpi-title">Available for Dispatch</span>
            <div className="kpi-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981' }}>
              <CheckCircle2 size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#10b981' }}>{availableCrews}</div>
          <div className="kpi-footer">Ready for rapid deployment</div>
        </div>

        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid #eab308' }}>
          <div className="kpi-header">
            <span className="kpi-title">Currently Engaged</span>
            <div className="kpi-icon" style={{ background: 'rgba(234, 179, 8, 0.15)', color: '#eab308' }}>
              <Clock size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#fde047' }}>{busyCrews}</div>
          <div className="kpi-footer">On active field service</div>
        </div>

        <div className="glass-panel kpi-card" style={{ borderLeft: '4px solid #f97316' }}>
          <div className="kpi-header">
            <span className="kpi-title">Pre-Positioned Targets</span>
            <div className="kpi-icon" style={{ background: 'rgba(249, 115, 22, 0.15)', color: '#f97316' }}>
              <Wrench size={18} />
            </div>
          </div>
          <div className="kpi-val" style={{ color: '#f97316' }}>{totalAssignedAssets}</div>
          <div className="kpi-footer">High & Critical assets mapped</div>
        </div>
      </div>

      {/* Roster & Skill Distribution Split */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Left: Skill Composition Pie */}
        <div className="glass-panel" style={{ gridColumn: 'span 4', height: '340px' }}>
          <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Specialized Skill Composition</h3>
          <p className="subtitle" style={{ marginBottom: '0.5rem' }}>Distribution of certified technicians</p>
          <div style={{ height: '240px', width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={skillPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {skillPieData.map((entry) => (
                    <Cell key={entry.name} fill={SKILL_COLORS[entry.name] || '#38bdf8'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0c1322', border: '1px solid var(--border-glow)', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '0.78rem' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Right: Filter Toolbar & Info */}
        <div className="glass-panel" style={{ gridColumn: 'span 8', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#fff' }}>Automated Proximity Dispatch Protocol</h3>
          <p className="subtitle" style={{ marginTop: '4px', marginBottom: '1.25rem', lineHeight: '1.5' }}>
            GridGuard AI applies <strong>Haversine geodesic distance</strong> algorithms combined with strict 
            <strong> skill compatibility rules</strong> (Electrical → Transformers & Switches, Mechanical → Switches & Lines, Civil → Lines & Foundations) 
            to ensure that only the closest qualified and available crew is assigned before an asset trips.
          </p>

          <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Skill Filter:</span>
              <select className="form-select" value={filterSkill} onChange={(e) => setFilterSkill(e.target.value)}>
                <option value="ALL">All Skills</option>
                <option value="electrical">Electrical</option>
                <option value="mechanical">Mechanical</option>
                <option value="civil">Civil</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Status Filter:</span>
              <select className="form-select" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                <option value="ALL">All Statuses</option>
                <option value="available">Available</option>
                <option value="busy">Busy</option>
              </select>
            </div>

            <span style={{ marginLeft: 'auto', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
              Showing {filteredCrews.length} Crews
            </span>
          </div>
        </div>

      </div>

      {/* Crew Cards Roster */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
        {filteredCrews.map((crew) => {
          const isAvail = crew.status.toLowerCase() === 'available';
          return (
            <div key={crew.crew_id} className="glass-panel" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column' }}>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{
                    width: '36px',
                    height: '36px',
                    borderRadius: '10px',
                    background: isAvail ? 'rgba(16, 185, 129, 0.15)' : 'rgba(234, 179, 8, 0.15)',
                    color: isAvail ? '#10b981' : '#fde047',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 800,
                    fontSize: '0.85rem'
                  }}>
                    {crew.crew_id}
                  </div>
                  <div>
                    <h4 style={{ margin: 0, fontSize: '0.95rem' }}>Crew {crew.crew_id}</h4>
                    <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'capitalize' }}>
                      Certified {crew.skill} Team
                    </span>
                  </div>
                </div>

                <span className={`badge badge-${isAvail ? 'low' : 'medium'}`}>
                  {crew.status}
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.75rem', marginBottom: '12px', padding: '8px 10px', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
                <div>Capacity: <strong style={{ color: '#fff' }}>{crew.capacity} Technicians</strong></div>
                <div>Available: <strong style={{ color: '#fff' }}>{crew.available_from?.split(' ')[1] || '06:00'}</strong></div>
                <div style={{ gridColumn: 'span 2', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
                  Base: {crew.latitude.toFixed(4)}, {crew.longitude.toFixed(4)}
                </div>
              </div>

              {/* Assigned Targets */}
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
                  Pre-positioned Assets ({crew.assignments?.length || 0}):
                </div>

                {crew.assignments && crew.assignments.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    {crew.assignments.map((asgn) => (
                      <div 
                        key={asgn.equipment_id}
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          padding: '6px 10px',
                          background: 'rgba(249, 115, 22, 0.08)',
                          border: '1px solid rgba(249, 115, 22, 0.25)',
                          borderRadius: '6px',
                          cursor: 'pointer'
                        }}
                        onClick={() => {
                          onSelectEquipment(asgn.equipment_id);
                          onNavigateToEquipment();
                        }}
                      >
                        <div>
                          <strong style={{ color: '#fff', fontSize: '0.8rem' }}>{asgn.equipment_id}</strong>
                          <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginLeft: '6px' }}>
                            {asgn.type}
                          </span>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                          <span className="badge badge-high" style={{ fontSize: '0.65rem' }}>{asgn.distance_km} km</span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', padding: '8px', background: 'rgba(255,255,255,0.01)', borderRadius: '6px' }}>
                    Standby reserve. No immediate critical assignments.
                  </div>
                )}
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
};
