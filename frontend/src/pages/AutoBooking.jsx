import React, { useState, useEffect } from 'react';
import {
  getAutoBookingRules,
  createAutoBookingRule,
  updateAutoBookingRule,
  deleteAutoBookingRule,
  getAutoBookingAudit,
} from '../api/autoBooking';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { formatCurrency, formatDateTime } from '../utils/formatters';
import { VEHICLE_TYPES } from '../utils/constants';
import toast from 'react-hot-toast';
import { FiPlus, FiTrash2, FiClock, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';

export const AutoBooking = () => {
  const [rules, setRules] = useState([]);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('rules'); // 'rules' or 'audit'

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [ruleName, setRuleName] = useState('Daily Office Parking');
  const [area, setArea] = useState('Hitech City');
  const [vehicleType, setVehicleType] = useState('CAR');
  const [startTime, setStartTime] = useState('09:30');
  const [durationMins, setDurationMins] = useState(480); // 8 hours
  const [maxPrice, setMaxPrice] = useState(400); // Rs 400
  const [leadTime, setLeadTime] = useState(60); // 60 mins before
  const [weeklyCap, setWeeklyCap] = useState(5);
  const [submitting, setSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [rulesData, auditData] = await Promise.all([
        getAutoBookingRules(),
        getAutoBookingAudit(),
      ]);
      setRules(rulesData);
      setAudit(auditData);
    } catch {
      // Handled silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleRule = async (rule) => {
    try {
      await updateAutoBookingRule(rule.id, { enabled: !rule.enabled });
      toast.success(`Rule ${!rule.enabled ? 'activated' : 'paused'}`);
      fetchData();
    } catch {
      toast.error('Failed to update rule.');
    }
  };

  const handleDeleteRule = async (id) => {
    if (!window.confirm('Delete this auto-booking rule?')) return;
    try {
      await deleteAutoBookingRule(id);
      toast.success('Rule deleted.');
      fetchData();
    } catch {
      toast.error('Failed to delete rule.');
    }
  };

  const handleCreateRule = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await createAutoBookingRule({
        name: ruleName,
        rule: {
          area,
          vehicle_type: vehicleType,
          start_time: startTime,
          duration_minutes: Number(durationMins),
          max_price_paise: Number(maxPrice) * 100,
          days: [0, 1, 2, 3, 4], // Monday - Friday
        },
        lead_time_minutes: Number(leadTime),
        weekly_booking_cap: Number(weeklyCap),
        enabled: true,
      });
      toast.success('Auto-booking rule created!');
      setModalOpen(false);
      fetchData();
    } catch {
      toast.error('Failed to create auto-booking rule.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Preference-Based Auto-Booking (AI Module 2)
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Automatically reserve and hold your preferred slots before your commute. Off by default (FR-AB1).
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold">
            <button
              onClick={() => setActiveTab('rules')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'rules' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
              }`}
            >
              My Rules ({rules.length})
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                activeTab === 'audit' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
              }`}
            >
              Audit Trail ({audit.length})
            </button>
          </div>

          <Button variant="primary" size="sm" onClick={() => setModalOpen(true)}>
            <FiPlus className="mr-1.5" /> Add Rule
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : activeTab === 'rules' ? (
        <div className="space-y-4">
          {rules.length > 0 ? (
            rules.map((r) => (
              <Card key={r.id} className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-2.5">
                      <h3 className="font-bold text-slate-900 text-base">{r.name}</h3>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full font-bold border ${
                          r.enabled
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : 'bg-slate-100 text-slate-600 border-slate-200'
                        }`}
                      >
                        {r.enabled ? 'Active' : 'Paused'}
                      </span>
                    </div>
                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-2">
                      <span>Area: <strong className="text-slate-700">{r.rule?.area}</strong></span>
                      <span>Time: <strong className="text-slate-700">{r.rule?.start_time}</strong></span>
                      <span>Cap: <strong className="text-slate-700">₹{r.rule?.max_price_paise / 100}</strong></span>
                      <span>Lead Time: <strong className="text-slate-700">{r.lead_time_minutes}m</strong></span>
                      <span>Weekly Cap: <strong className="text-slate-700">{r.weekly_booking_cap} bookings</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => handleToggleRule(r)}
                      className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                        r.enabled
                          ? 'border-amber-300 text-amber-700 hover:bg-amber-50'
                          : 'border-emerald-300 text-emerald-700 hover:bg-emerald-50'
                      }`}
                    >
                      {r.enabled ? 'Pause Rule' : 'Activate Rule'}
                    </button>
                    <button
                      onClick={() => handleDeleteRule(r.id)}
                      className="text-slate-400 hover:text-rose-600 p-1.5"
                    >
                      <FiTrash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <Card className="p-12 text-center">
              <FiClock className="w-12 h-12 text-slate-300 mx-auto mb-3" />
              <h3 className="font-bold text-slate-800 text-base">No auto-booking rules configured</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
                Create a recurring commute rule to have slots booked and held automatically for you every morning.
              </p>
              <div className="mt-5">
                <Button variant="primary" onClick={() => setModalOpen(true)}>
                  Create Your First Rule
                </Button>
              </div>
            </Card>
          )}
        </div>
      ) : (
        /* Audit Trail Tab */
        <div className="space-y-3">
          {audit.length > 0 ? (
            audit.map((a) => (
              <Card key={a.id} className="p-4 text-xs">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span
                      className={`font-bold px-2 py-0.5 rounded text-[11px] ${
                        a.decision === 'BOOKED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {a.decision}
                    </span>
                    <span className="font-medium text-slate-800">{a.decision_reason}</span>
                  </div>
                  <span className="text-slate-400">{formatDateTime(a.created_at)}</span>
                </div>
              </Card>
            ))
          ) : (
            <Card className="p-10 text-center text-xs text-slate-400">
              No auto-booking audit logs recorded yet.
            </Card>
          )}
        </div>
      )}

      {/* Create Rule Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200 animate-in fade-in zoom-in-95">
            <h3 className="font-bold text-slate-900 text-lg mb-4">New Auto-Booking Rule</h3>
            <form onSubmit={handleCreateRule} className="space-y-4 text-xs">
              <Input
                label="Rule Name"
                value={ruleName}
                onChange={(e) => setRuleName(e.target.value)}
                required
              />
              <Input
                label="Target Area / Landmark"
                value={area}
                onChange={(e) => setArea(e.target.value)}
                required
              />
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                    Vehicle Type
                  </label>
                  <select
                    value={vehicleType}
                    onChange={(e) => setVehicleType(e.target.value)}
                    className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                  >
                    {VEHICLE_TYPES.map((v) => (
                      <option key={v.value} value={v.value}>
                        {v.label}
                      </option>
                    ))}
                  </select>
                </div>
                <Input
                  label="Target Arrival Time"
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <Input
                  label="Max Price (₹)"
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(e.target.value)}
                  required
                />
                <Input
                  label="Lead Time (mins)"
                  type="number"
                  value={leadTime}
                  onChange={(e) => setLeadTime(e.target.value)}
                  required
                />
                <Input
                  label="Weekly Limit"
                  type="number"
                  value={weeklyCap}
                  onChange={(e) => setWeeklyCap(e.target.value)}
                  required
                />
              </div>

              <div className="pt-4 flex justify-end space-x-3 border-t border-slate-100">
                <Button variant="outline" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" loading={submitting}>
                  Save & Enable Rule
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
