import React from 'react';
import { 
  Activity, 
  AlertTriangle, 
  MapPin, 
  Cpu, 
  Users, 
  Sliders, 
  Bell, 
  Zap, 
  CheckCircle2 
} from 'lucide-react';
import type { SummaryData } from '../types/grid';

export type PageId = 'overview' | 'risk' | 'map' | 'equipment' | 'crews' | 'simulator' | 'alerts';

interface SidebarProps {
  currentPage: PageId;
  onSelectPage: (page: PageId) => void;
  summary: SummaryData | null;
  backendConnected: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onSelectPage,
  summary,
  backendConnected
}) => {
  const alertCount = summary?.active_alerts || 0;

  const navItems = [
    { id: 'overview' as PageId, label: 'Command Center', icon: Activity },
    { id: 'risk' as PageId, label: 'Risk Command', icon: AlertTriangle, badge: alertCount > 0 ? alertCount : undefined, badgeType: 'critical' },
    { id: 'map' as PageId, label: 'Live Grid Map', icon: MapPin },
    { id: 'equipment' as PageId, label: 'Equipment Intelligence', icon: Cpu },
    { id: 'crews' as PageId, label: 'Crew Operations', icon: Users, badge: summary?.available_crews ? `${summary.available_crews} Avail` : undefined, badgeType: 'low' },
    { id: 'simulator' as PageId, label: 'AI Insights & Sim', icon: Sliders },
    { id: 'alerts' as PageId, label: 'Alert Center', icon: Bell, badge: alertCount > 0 ? alertCount : undefined, badgeType: 'high' },
  ];

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="logo-symbol">
          <Zap size={22} color="#ffffff" />
        </div>
        <div className="logo-text">
          <span>GRIDGUARD</span>
          <span className="logo-sub">AI PLATFORM</span>
        </div>
      </div>

      {/* Navigation */}
      <div className="nav-section-title">Operational Views</div>
      <ul className="nav-links">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <li key={item.id}>
              <button
                className={`nav-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectPage(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
                {item.badge !== undefined && (
                  <span className={`nav-badge badge-${item.badgeType || 'cyan'}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>

      {/* Footer Info */}
      <div className="sidebar-footer">
        <div className="engine-status-pill">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span className={`pulse-dot ${backendConnected ? '' : 'critical'}`} />
            <span style={{ color: 'var(--text-muted)' }}>
              {backendConnected ? 'FastAPI Connected' : 'Connecting API...'}
            </span>
          </div>
          {backendConnected ? (
            <CheckCircle2 size={14} color="var(--color-low)" />
          ) : (
            <AlertTriangle size={14} color="var(--color-critical)" />
          )}
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', textAlign: 'center' }}>
          Bangalore Grid Area • v1.0 Enterprise
        </div>
      </div>
    </aside>
  );
};
