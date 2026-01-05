/**
 * API client for backend services.
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

/**
 * Fetch historical time series data.
 */
export async function getSeries(role, location) {
  const url = new URL(`${API_BASE}/series`);
  url.searchParams.append('role', role);
  url.searchParams.append('location', location);
  
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Failed to fetch series: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Fetch forecast data.
 */
export async function getForecast(role, location, horizon = 8) {
  const url = new URL(`${API_BASE}/forecast`);
  url.searchParams.append('role', role);
  url.searchParams.append('location', location);
  url.searchParams.append('horizon', horizon.toString());
  
  const response = await fetch(url.toString());
  if (!response.ok) {
    throw new Error(`Failed to fetch forecast: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Check API health.
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) {
    throw new Error('API is not healthy');
  }
  return await response.json();
}
