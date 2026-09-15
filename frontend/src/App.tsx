import { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import type { PageId } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { OverviewPage } from './pages/OverviewPage';
import { RiskCommandPage } from './pages/RiskCommandPage';
import { GridMapPage } from './pages/GridMapPage';
import { EquipmentIntelligencePage } from './pages/EquipmentIntelligencePage';
import { CrewOperationsPage } from './pages/CrewOperationsPage';
import { AiInsightsPage } from './pages/AiInsightsPage';
import { AlertCenterPage } from './pages/AlertCenterPage';
import type { Equipment, SummaryData, Crew, FeatureImportance } from './types/grid';
import './index.css';

const API_BASE = 'http://localhost:8000';

export function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('overview');
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [predictions, setPredictions] = useState<Equipment[]>([]);
  const [crews, setCrews] = useState<Crew[]>([]);
  const [featureImportance, setFeatureImportance] = useState<FeatureImportance[]>([]);
  const [selectedEquipmentId, setSelectedEquipmentId] = useState<string>('T001');
  const [backendConnected, setBackendConnected] = useState<boolean>(false);
  const [isPipelineRunning, setIsPipelineRunning] = useState<boolean>(false);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [lastUpdated, setLastUpdated] = useState<string>('Just now');
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null);

  const showToast = (message: string, type: 'success' | 'info' | 'error' = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4500);
  };

  const loadData = useCallback(async () => {
    try {
      const healthRes = await fetch(`${API_BASE}/api/health`, { signal: AbortSignal.timeout(3000) });
      if (healthRes.ok) {
        setBackendConnected(true);
      }

      const summaryRes = await fetch(`${API_BASE}/api/summary`);
      if (summaryRes.ok) {
        const summaryJson = await summaryRes.json();
        setSummary(summaryJson);
      }

      const predRes = await fetch(`${API_BASE}/api/predictions`);
      if (predRes.ok) {
        const predJson = await predRes.json();
        setPredictions(predJson);
        if (predJson.length > 0 && !selectedEquipmentId) {
          setSelectedEquipmentId(predJson[0].equipment_id);
        }
      }

      const crewRes = await fetch(`${API_BASE}/api/crews`);
      if (crewRes.ok) {
        const crewJson = await crewRes.json();
        setCrews(crewJson);
      }

      const fiRes = await fetch(`${API_BASE}/api/feature-importance`);
      if (fiRes.ok) {
        const fiJson = await fiRes.json();
        if (Array.isArray(fiJson)) {
          setFeatureImportance(fiJson);
        }
      }

      setLastUpdated(new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
    } catch (err) {
      console.warn('Backend connection notice:', err);
      setBackendConnected(false);
    }
  }, [selectedEquipmentId]);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 20000);
    return () => clearInterval(interval);
  }, [loadData]);

  const handleTriggerPipeline = async () => {
    setIsPipelineRunning(true);
    showToast('Triggering full GridGuard AI pipeline recalculation...', 'info');
    try {
      const res = await fetch(`${API_BASE}/api/pipeline/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ force_retrain: false }),
      });
      if (res.ok) {
        await loadData();
        showToast('AI Pipeline execution completed! Predictions & crew routes refreshed.', 'success');
      } else {
        showToast('Pipeline execution error. Please check server logs.', 'error');
      }
    } catch {
      showToast('Cannot connect to backend pipeline runner.', 'error');
    } finally {
      setIsPipelineRunning(false);
    }
  };

  const handleUploadCsv = async (file: File) => {
    setIsUploading(true);
    showToast(`Uploading and processing ${file.name}...`, 'info');
    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_BASE}/api/upload/equipment`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      if (res.ok) {
        await loadData();
        showToast(`Success! Ingested ${data.rows_processed} assets. Dashboard and GIS map refreshed.`, 'success');
      } else {
        showToast(data.detail || 'Failed to upload CSV file', 'error');
      }
    } catch {
      showToast('Error communicating with backend during CSV upload.', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        currentPage={currentPage}
        onSelectPage={setCurrentPage}
        summary={summary}
        backendConnected={backendConnected}
      />

      <div className="main-wrapper">
        <Navbar 
          currentPage={currentPage}
          onRefreshData={loadData}
          onTriggerPipeline={handleTriggerPipeline}
          onUploadCsv={handleUploadCsv}
          lastUpdated={lastUpdated}
          isPipelineRunning={isPipelineRunning}
          isUploading={isUploading}
          alertCount={summary?.active_alerts || 0}
        />

        {notification && (
          <div style={{
            position: 'absolute',
            top: '76px',
            right: '24px',
            zIndex: 9999,
            padding: '10px 18px',
            borderRadius: '8px',
            background: notification.type === 'success' ? '#065f46' : notification.type === 'error' ? '#991b1b' : '#1e3a8a',
            color: '#ffffff',
            fontSize: '0.825rem',
            fontWeight: 600,
            boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
            border: '1px solid rgba(255,255,255,0.2)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            {notification.message}
          </div>
        )}

        {currentPage === 'overview' && (
          <OverviewPage 
            summary={summary}
            predictions={predictions}
            onSelectEquipment={setSelectedEquipmentId}
            onNavigatePage={(p) => setCurrentPage(p as PageId)}
          />
        )}

        {currentPage === 'risk' && (
          <RiskCommandPage 
            predictions={predictions}
            onSelectEquipment={setSelectedEquipmentId}
            onNavigateToEquipment={() => setCurrentPage('equipment')}
          />
        )}

        {currentPage === 'map' && (
          <GridMapPage 
            predictions={predictions}
            crews={crews}
            onSelectEquipment={setSelectedEquipmentId}
            onNavigateToEquipment={() => setCurrentPage('equipment')}
          />
        )}

        {currentPage === 'equipment' && (
          <EquipmentIntelligencePage 
            predictions={predictions}
            selectedId={selectedEquipmentId}
            onSelectEquipment={setSelectedEquipmentId}
          />
        )}

        {currentPage === 'crews' && (
          <CrewOperationsPage 
            crews={crews}
            onSelectEquipment={setSelectedEquipmentId}
            onNavigateToEquipment={() => setCurrentPage('equipment')}
          />
        )}

        {currentPage === 'simulator' && (
          <AiInsightsPage 
            predictions={predictions}
            featureImportance={featureImportance}
            selectedId={selectedEquipmentId}
            onSelectEquipment={setSelectedEquipmentId}
          />
        )}

        {currentPage === 'alerts' && (
          <AlertCenterPage 
            predictions={predictions}
            onSelectEquipment={setSelectedEquipmentId}
            onNavigateToEquipment={() => setCurrentPage('equipment')}
          />
        )}
      </div>
    </div>
  );
}

export default App;
