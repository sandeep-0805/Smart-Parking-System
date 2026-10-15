import React, { useState } from 'react';
import { FiSearch, FiMapPin, FiCalendar, FiClock, FiDollarSign, FiSliders } from 'react-icons/fi';
import { Button } from '../common/Button';
import { VEHICLE_TYPES, FACILITY_OPTIONS } from '../../utils/constants';

export const SearchForm = ({ initialValues = {}, onSearch, loading = false }) => {
  const [placeName, setPlaceName] = useState(initialValues.place_name || 'Hitech City');
  const [date, setDate] = useState(initialValues.date || new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState(initialValues.start_time || '10:00');
  const [durationMins, setDurationMins] = useState(initialValues.duration_minutes || 120);
  const [vehicleType, setVehicleType] = useState(initialValues.vehicle_type || 'CAR');
  const [maxBudget, setMaxBudget] = useState(initialValues.max_budget_inr || '');
  const [facilities, setFacilities] = useState(initialValues.facilities || []);
  const [showFilters, setShowFilters] = useState(false);

  const handleFacilityToggle = (facId) => {
    setFacilities((prev) =>
      prev.includes(facId) ? prev.filter((f) => f !== facId) : [...prev, facId]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({
      place_name: placeName,
      date,
      start_time: startTime,
      duration_minutes: Number(durationMins),
      vehicle_type: vehicleType,
      max_budget_inr: maxBudget ? Number(maxBudget) : undefined,
      facilities: facilities.length > 0 ? facilities : undefined,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200/80 shadow-md p-5 sm:p-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Location input */}
        <div className="md:col-span-2">
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center">
            <FiMapPin className="text-blue-600 mr-1" /> Destination / Area
          </label>
          <div className="relative">
            <input
              type="text"
              value={placeName}
              onChange={(e) => setPlaceName(e.target.value)}
              placeholder="e.g. Hitech City, Inorbit Mall, Gachibowli..."
              className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
              required
            />
          </div>
        </div>

        {/* Date */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center">
            <FiCalendar className="text-blue-600 mr-1" /> Date
          </label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
            required
          />
        </div>

        {/* Start Time */}
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5 flex items-center">
            <FiClock className="text-blue-600 mr-1" /> Arrival Time
          </label>
          <input
            type="time"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
            required
          />
        </div>
      </div>

      {/* Row 2: Duration & Vehicle */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-100">
        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Duration
          </label>
          <select
            value={durationMins}
            onChange={(e) => setDurationMins(e.target.value)}
            className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value={30}>30 mins</option>
            <option value={60}>1 hour</option>
            <option value={120}>2 hours</option>
            <option value={180}>3 hours</option>
            <option value={240}>4 hours</option>
            <option value={480}>8 hours (Full day)</option>
            <option value={1440}>24 hours</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Vehicle Type
          </label>
          <select
            value={vehicleType}
            onChange={(e) => setVehicleType(e.target.value)}
            className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {VEHICLE_TYPES.map((v) => (
              <option key={v.value} value={v.value}>
                {v.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
            Max Budget (₹)
          </label>
          <input
            type="number"
            value={maxBudget}
            onChange={(e) => setMaxBudget(e.target.value)}
            placeholder="No limit"
            min={0}
            step={10}
            className="w-full px-3 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Facilities toggle */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-bold text-slate-500 uppercase mr-1">Facilities:</span>
          {FACILITY_OPTIONS.map((fac) => (
            <label
              key={fac.id}
              className={`cursor-pointer inline-flex items-center text-xs px-2.5 py-1 rounded-lg border transition-colors ${
                facilities.includes(fac.id)
                  ? 'bg-blue-50 text-blue-700 border-blue-300 font-semibold'
                  : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100'
              }`}
            >
              <input
                type="checkbox"
                checked={facilities.includes(fac.id)}
                onChange={() => handleFacilityToggle(fac.id)}
                className="hidden"
              />
              {fac.label}
            </label>
          ))}
        </div>

        <Button type="submit" loading={loading} variant="primary" size="lg" className="w-full sm:w-auto px-8">
          <FiSearch className="mr-2" /> Search Slots
        </Button>
      </div>
    </form>
  );
};
