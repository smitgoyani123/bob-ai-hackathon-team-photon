export type RiskLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';

export interface Equipment {
  equipment_id: string;
  type: string;
  age: number;
  health: number;
  load: number;
  temperature: number;
  voltage: number;
  customers_served: number;
  critical_facility: number;
  latitude: number;
  longitude: number;
  weather_rainfall: number;
  weather_wind: number;
  weather_temperature: number;
  weather_storm: number;
  weather_flood_risk: number;
  failure_probability: number;
  weather_risk: number;
  grid_impact: number;
  priority_score: number;
  risk_level: RiskLevel;
  maintenance_action: string;
  assigned_crew: string;
  crew_distance_km: number | null;
  risk_reasons?: string[];
}

export interface SummaryData {
  total_equipment: number;
  risk_counts: Record<RiskLevel, number>;
  system_health_score: number;
  avg_failure_probability: number;
  avg_weather_risk: number;
  avg_grid_impact: number;
  critical_facilities: number;
  total_crews: number;
  available_crews: number;
  active_alerts: number;
}

export interface CrewAssignment {
  equipment_id: string;
  type: string;
  risk_level: RiskLevel;
  priority_score: number;
  distance_km: number | null;
  action: string;
}

export interface Crew {
  crew_id: string;
  latitude: number;
  longitude: number;
  status: string;
  skill: string;
  capacity: number;
  available_from: string;
  assignments: CrewAssignment[];
  assigned_count: number;
}

export interface FeatureImportance {
  feature: string;
  importance: number;
  importance_pct: number;
}

export interface SimulationResult {
  equipment_id: string;
  baseline: {
    failure_probability: number;
    weather_risk: number;
    grid_impact: number;
    priority_score: number;
    risk_level: string;
    maintenance_action: string;
  };
  simulated: {
    weather_risk: number;
    grid_impact: number;
    priority_score: number;
    risk_level: string;
    maintenance_action: string;
    weather_delta: number;
    priority_delta: number;
  };
}
