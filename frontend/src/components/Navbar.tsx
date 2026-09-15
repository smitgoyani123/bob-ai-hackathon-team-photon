import React, { useState, useRef } from 'react';
import { RefreshCw, ShieldAlert, Sparkles, Upload, FileDown } from 'lucide-react';
import type { PageId } from './Sidebar';

interface NavbarProps {
  currentPage: PageId;
  onRefreshData: () => Promise<void>;
  onTriggerPipeline: () => Promise<void>;
  onUploadCsv: (file: File) => Promise<void>;
  lastUpdated: string;
  isPipelineRunning: boolean;
  isUploading: boolean;
  alertCount: number;
}

const PAGE_TITLES: Record<PageId, { title: string; subtitle: string }> = {
  overview: {
    title: 'Command Center & Executive Telemetry',
    subtitle: 'Real-time grid health, predictive failure matrix, and automated operations queue',
  },
  risk: {
    title: 'Risk Command & Asset Prioritization',
    subtitle: 'Deep-dive risk scoring, multi-dimensional risk matrix, and equipment hierarchy',
  },
  map: {
    title: 'Live Geographic Information System (GIS)',
    subtitle: 'Real-time spatial distribution, equipment telemetry pins, and crew pre-positioning lines',
  },
  equipment: {
    title: 'Equipment Intelligence & AI Decision Card',
    subtitle: 'Transparent deterministic explainability, telemetry breakdown, and dispatch protocols',
  },
  crews: {
    title: 'Field Crew Operations & Dispatch Fleet',
    subtitle: 'Technician availability, specialized skill mapping, and Haversine proximity routes',
  },
  simulator: {
    title: 'AI Insights & What-If Scenario Simulator',
    subtitle: 'Random Forest feature importances and interactive parametric grid stress testing',
  },
  alerts: {
    title: 'Grid Alert Center & Dispatch Protocols',
    subtitle: 'Actionable high-priority risk warnings, audit trails, and exportable operational reports',
  },
};

export const Navbar: React.FC<NavbarProps> = ({
  currentPage,
  onRefreshData,
  onTriggerPipeline,
  onUploadCsv,
  lastUpdated,
  isPipelineRunning,
  isUploading,
  alertCount,
}) => {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const meta = PAGE_TITLES[currentPage] || PAGE_TITLES.overview;

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefreshData();
    setTimeout(() => setIsRefreshing(false), 400);
  };

  const handleFileInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      await onUploadCsv(file);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleDownloadTemplate = () => {
    const templateContent = [
      'equipment_id,type,age,health,load,temperature,voltage,customers_served,critical_facility,latitude,longitude',
      'T101,Transformer,22,45.0,82.5,78.0,33,6200,1,12.985000,77.580000',
      'T102,Transformer,15,68.0,55.0,62.5,11,3800,0,12.950000,77.540000',
      'S101,Switch,28,32.0,89.0,84.0,66,8500,1,13.020000,77.610000',
      'L101,Line,35,28.0,91.0,88.0,132,9200,1,12.920000,77.670000'
    ].join('\n');
    
    const blob = new Blob([templateContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'equipment_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <header className="top-navbar">
      <div className="header-title-box">
        <h1>{meta.title}</h1>
        <p>{meta.subtitle}</p>
      </div>

      <div className="header-actions">
        {alertCount > 0 && (
          <div className="badge badge-critical" style={{ padding: '6px 12px', fontSize: '0.75rem' }}>
            <ShieldAlert size={14} />
            <span>{alertCount} Active Alerts</span>
          </div>
        )}

        <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginRight: '4px' }}>
          Updated: <span style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{lastUpdated}</span>
        </div>

        {/* Hidden file input for CSV upload */}
        <input 
          type="file"
          ref={fileInputRef}
          accept=".csv"
          onChange={handleFileInputChange}
          style={{ display: 'none' }}
        />

        {/* Template download */}
        <button 
          className="btn btn-secondary btn-sm"
          onClick={handleDownloadTemplate}
          title="Download Sample Equipment CSV Template"
        >
          <FileDown size={14} />
          <span>CSV Template</span>
        </button>

        {/* Upload CSV */}
        <button 
          className="btn btn-secondary btn-sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={isUploading || isPipelineRunning}
          title="Upload real-time or custom equipment CSV dataset"
        >
          <Upload size={14} color="#38bdf8" />
          <span>{isUploading ? 'Ingesting CSV...' : 'Import CSV'}</span>
        </button>

        <button 
          className="btn btn-secondary btn-sm" 
          onClick={handleRefresh}
          title="Refresh real-time data"
          disabled={isRefreshing}
        >
          <RefreshCw size={14} className={isRefreshing ? 'spin' : ''} />
          <span>Sync</span>
        </button>

        <button 
          className="btn btn-primary btn-sm" 
          onClick={onTriggerPipeline}
          disabled={isPipelineRunning || isUploading}
          title="Run full data load, preprocessing, ML training, weather & grid calculation"
        >
          {isPipelineRunning ? (
            <>
              <RefreshCw size={14} className="spin" />
              <span>Computing AI Pipeline...</span>
            </>
          ) : (
            <>
              <Sparkles size={14} />
              <span>Run AI Pipeline</span>
            </>
          )}
        </button>
      </div>
    </header>
  );
};
