import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getOperatorDashboard } from '../../api/operator';
import { getLocationForecast } from '../../api/search';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { formatCurrency, formatDateTime } from '../../utils/formatters';
import { FiMapPin, FiTrendingUp, FiLayers, FiDollarSign, FiPlus, FiCpu } from 'react-icons/fi';
import toast from 'react-hot-toast';

export const OperatorDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [forecastModal, setForecastModal] = useState(null);
  const [loadingForecast, setLoadingForecast] = useState(false);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const data = await getOperatorDashboard();
      setDashboard(data);
    } catch {
      toast.error('Failed to load operator metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleShowForecast = async (loc) => {
    setLoadingForecast(true);
    try {
      const data = await getLocationForecast(loc.location_id);
      setForecastModal({ location: loc, forecast: data });
    } catch {
      toast.error('Could not retrieve forecast.');
    } finally {
      setLoadingForecast(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Operator Portal</h1>
          <p className="text-xs text-slate-500 mt-0.5">Live inventory, occupancy metrics, revenue, and ML forecasts</p>
        </div>
        <div className="flex items-center space-x-3">
          <Link to="/operator/locations">
            <Button variant="outline" size="sm">
              Manage Locations
            </Button>
          </Link>
          <Link to="/operator/locations">
            <Button variant="primary" size="sm">
              <FiPlus className="mr-1.5" /> Manage / Add Location
            </Button>
          </Link>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-5">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Total Locations</span>
          <span className="text-3xl font-black text-slate-900 mt-1 block">{dashboard?.total_locations || 0}</span>
          <span className="text-xs text-slate-500 mt-1 block">Active parking lots</span>
        </Card>

        <Card className="p-5">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Current Occupancy</span>
          <div className="flex items-baseline space-x-2 mt-1">
            <span className="text-3xl font-black text-blue-600">
              {Math.round((dashboard?.overall_occupancy_pct || 0) * 100)}%
            </span>
            <span className="text-xs text-slate-500">
              ({dashboard?.occupied_slots} / {dashboard?.total_slots} slots)
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
            <div
              className="bg-blue-600 h-1.5 rounded-full"
              style={{ width: `${Math.round((dashboard?.overall_occupancy_pct || 0) * 100)}%` }}
            ></div>
          </div>
        </Card>

        <Card className="p-5">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Today's Bookings</span>
          <span className="text-3xl font-black text-slate-900 mt-1 block">{dashboard?.today_bookings_count || 0}</span>
          <span className="text-xs text-emerald-600 font-semibold mt-1 block">Confirmed reservations</span>
        </Card>

        <Card className="p-5">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Today's Revenue</span>
          <span className="text-3xl font-black text-slate-900 mt-1 block">
            {formatCurrency(dashboard?.today_revenue_paise || 0)}
          </span>
          <span className="text-xs text-slate-500 mt-1 block">Net recognized</span>
        </Card>
      </div>

      {/* Locations Live Occupancy Cards */}
      <div className="space-y-4">
        <h2 className="text-lg font-extrabold text-slate-900">Locations Status</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {dashboard?.locations?.map((loc) => {
            const occPct = Math.round(loc.occupancy_pct * 100);
            return (
              <Card key={loc.location_id} className="p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-slate-900 text-base">{loc.name}</h3>
                    <span className="text-xs font-semibold text-emerald-600">
                      {loc.available_slots} / {loc.total_slots} slots available
                    </span>
                  </div>
                  <span className="font-bold text-sm text-slate-900">
                    {formatCurrency(loc.today_revenue_paise)}
                  </span>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Live Occupancy</span>
                    <span className="font-bold text-slate-800">{occPct}%</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        occPct > 80 ? 'bg-rose-500' : occPct > 50 ? 'bg-amber-500' : 'bg-emerald-500'
                      }`}
                      style={{ width: `${occPct}%` }}
                    ></div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <Link
                    to={`/operator/locations/${loc.location_id}/slots`}
                    className="font-semibold text-blue-600 hover:text-blue-700"
                  >
                    Manage Slots &rarr;
                  </Link>

                  <button
                    onClick={() => handleShowForecast(loc)}
                    className="inline-flex items-center text-purple-600 hover:text-purple-700 font-semibold"
                  >
                    <FiCpu className="mr-1" /> View Forecast
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Forecast Modal */}
      {forecastModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-purple-600 bg-purple-50 px-2 py-0.5 rounded">
                  AI Module 5 Forecast
                </span>
                <h3 className="font-bold text-slate-900 text-base mt-1">
                  {forecastModal.location.name}
                </h3>
              </div>
              <button
                onClick={() => setForecastModal(null)}
                className="text-slate-400 hover:text-slate-600 text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="py-6 space-y-4">
              <div className="bg-purple-50/70 border border-purple-200/80 rounded-xl p-4 text-center">
                <span className="text-xs text-purple-900 font-medium block">
                  Predicted Free Spaces (Next 45 Mins)
                </span>
                <span className="text-4xl font-black text-purple-900 mt-1 block">
                  {Math.round(forecastModal.forecast.predicted_available)}
                </span>
                <span className="text-xs text-purple-600 block mt-1">
                  Estimated occupancy: {Math.round(forecastModal.forecast.occupancy_pct * 100)}%
                </span>
              </div>

              <div className="text-xs text-slate-500 space-y-2">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span>Uncertainty Range:</span>
                  <strong className="text-slate-800">
                    {Math.round(forecastModal.forecast.uncertainty_low * 100)}% –{' '}
                    {Math.round(forecastModal.forecast.uncertainty_high * 100)}%
                  </strong>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span>Model Artifact Version:</span>
                  <strong className="font-mono text-slate-800">
                    {forecastModal.forecast.model_version}
                  </strong>
                </div>
                <div className="flex justify-between py-1">
                  <span>Forecast Generated At:</span>
                  <span className="text-slate-700">
                    {formatDateTime(forecastModal.forecast.generated_at)}
                  </span>
                </div>
              </div>

              <p className="text-[11px] text-slate-400 italic">
                * Note: Labeled 'Estimate' per PRD Section 4.7. Live reservations always verify database state.
              </p>
            </div>

            <div className="flex justify-end pt-3 border-t border-slate-100">
              <Button variant="outline" size="sm" onClick={() => setForecastModal(null)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
