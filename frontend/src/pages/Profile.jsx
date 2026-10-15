import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { updatePreferences } from '../api/auth';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';
import { VEHICLE_TYPES, FACILITY_OPTIONS } from '../utils/constants';
import toast from 'react-hot-toast';

export const Profile = () => {
  const { user, preferences, refreshUser } = useAuth();
  const [vehicleType, setVehicleType] = useState('CAR');
  const [facilities, setFacilities] = useState([]);
  const [maxDistance, setMaxDistance] = useState(1000);
  const [maxBudget, setMaxBudget] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (preferences) {
      setVehicleType(preferences.default_vehicle_type || 'CAR');
      setFacilities(
        Array.isArray(preferences.preferred_facilities)
          ? preferences.preferred_facilities
          : []
      );
      setMaxDistance(preferences.max_walking_distance_m || 1000);
      setMaxBudget(preferences.max_budget_paise ? preferences.max_budget_paise / 100 : '');
    }
  }, [preferences]);

  const toggleFacility = (facId) => {
    setFacilities((prev) =>
      prev.includes(facId) ? prev.filter((f) => f !== facId) : [...prev, facId]
    );
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await updatePreferences({
        default_vehicle_type: vehicleType,
        preferred_facilities: facilities,
        max_walking_distance_m: Number(maxDistance),
        max_budget_paise: maxBudget ? Number(maxBudget) * 100 : null,
      });
      await refreshUser();
      toast.success('Parking preferences updated successfully!');
    } catch {
      toast.error('Failed to update preferences.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 tracking-tight">Profile & Preferences</h1>
        <p className="text-xs text-slate-500 mt-0.5">Customize your AI recommendation scoring factors</p>
      </div>

      {/* Account Info */}
      <Card className="p-6">
        <h3 className="font-bold text-slate-800 text-sm mb-4">Account Information</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div>
            <span className="text-slate-400 uppercase font-semibold">Full Name</span>
            <p className="font-bold text-slate-800 text-sm mt-0.5">{user?.full_name}</p>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-semibold">Email</span>
            <p className="font-bold text-slate-800 text-sm mt-0.5">{user?.email}</p>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-semibold">Account Role</span>
            <p className="font-bold text-blue-600 text-sm mt-0.5">{user?.role}</p>
          </div>
          <div>
            <span className="text-slate-400 uppercase font-semibold">Phone</span>
            <p className="font-bold text-slate-800 text-sm mt-0.5">{user?.phone || 'Not provided'}</p>
          </div>
        </div>
      </Card>

      {/* Preferences Form */}
      <Card className="p-6">
        <h3 className="font-bold text-slate-800 text-sm mb-4">Default Parking Preferences</h3>
        <form onSubmit={handleSave} className="space-y-5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                Default Vehicle Type
              </label>
              <select
                value={vehicleType}
                onChange={(e) => setVehicleType(e.target.value)}
                className="w-full px-3.5 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {VEHICLE_TYPES.map((v) => (
                  <option key={v.value} value={v.value}>
                    {v.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <Input
                label="Max Walking Distance (meters)"
                type="number"
                value={maxDistance}
                onChange={(e) => setMaxDistance(e.target.value)}
                min={100}
                max={5000}
                step={50}
              />
            </div>
          </div>

          <div>
            <Input
              label="Default Max Budget (₹ per booking)"
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              placeholder="Leave empty for no limit"
              min={0}
              step={10}
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
              Preferred Facilities (Weights AI Recommendation Scoring)
            </label>
            <div className="flex flex-wrap gap-2">
              {FACILITY_OPTIONS.map((fac) => (
                <label
                  key={fac.id}
                  className={`cursor-pointer inline-flex items-center text-xs px-3 py-1.5 rounded-lg border transition-colors ${
                    facilities.includes(fac.id)
                      ? 'bg-blue-50 text-blue-700 border-blue-400 font-bold'
                      : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={facilities.includes(fac.id)}
                    onChange={() => toggleFacility(fac.id)}
                    className="hidden"
                  />
                  {fac.label}
                </label>
              ))}
            </div>
          </div>

          <Button type="submit" variant="primary" loading={loading} className="w-full sm:w-auto px-6">
            Save Preferences
          </Button>
        </form>
      </Card>
    </div>
  );
};
