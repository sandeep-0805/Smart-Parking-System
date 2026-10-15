import React, { useState, useEffect, useRef } from 'react';
import {
  FiSearch,
  FiMapPin,
  FiCalendar,
  FiClock,
  FiNavigation,
  FiLoader,
  FiCheck,
} from 'react-icons/fi';
import { Button } from '../common/Button';
import { VEHICLE_TYPES, FACILITY_OPTIONS } from '../../utils/constants';
import { getLocationSuggestions, reverseGeocodeCoords } from '../../api/search';
import toast from 'react-hot-toast';

export const SearchForm = ({ initialValues = {}, onSearch, loading = false }) => {
  const [placeName, setPlaceName] = useState(initialValues.place_name || 'Hitech City');
  const [coords, setCoords] = useState({
    lat: initialValues.lat || null,
    lng: initialValues.lng || null,
  });
  const [date, setDate] = useState(initialValues.date || new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState(initialValues.start_time || '10:00');
  const [durationMins, setDurationMins] = useState(initialValues.duration_minutes || 120);
  const [vehicleType, setVehicleType] = useState(initialValues.vehicle_type || 'CAR');
  const [maxBudget, setMaxBudget] = useState(initialValues.max_budget_inr || '');
  const [facilities, setFacilities] = useState(initialValues.facilities || []);

  // Autocomplete suggestions state
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const dropdownRef = useRef(null);

  // Live Location detection state
  const [detectingLocation, setDetectingLocation] = useState(false);

  // Sync when parent changes initialValues (e.g. from Map click or URL param)
  useEffect(() => {
    if (initialValues.place_name !== undefined && initialValues.place_name !== placeName) {
      setPlaceName(initialValues.place_name);
    }
    if (initialValues.lat !== undefined && initialValues.lng !== undefined) {
      setCoords({ lat: initialValues.lat, lng: initialValues.lng });
    }
  }, [initialValues.place_name, initialValues.lat, initialValues.lng]);

  // Click outside to close suggestion dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions with debounce when placeName has >= 3 chars
  useEffect(() => {
    if (!placeName || placeName.trim().length < 3) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoadingSuggestions(true);
      try {
        const results = await getLocationSuggestions(placeName.trim());
        setSuggestions(results || []);
        setShowSuggestions(true);
        setHighlightedIndex(-1);
      } catch (err) {
        console.error('Error fetching suggestions:', err);
      } finally {
        setLoadingSuggestions(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [placeName]);

  const handleFacilityToggle = (facId) => {
    setFacilities((prev) =>
      prev.includes(facId) ? prev.filter((f) => f !== facId) : [...prev, facId]
    );
  };

  const handleSelectSuggestion = (item) => {
    setPlaceName(item.name);
    setCoords({ lat: item.lat, lng: item.lng });
    setShowSuggestions(false);

    onSearch({
      place_name: item.name,
      lat: item.lat,
      lng: item.lng,
      date,
      start_time: startTime,
      duration_minutes: Number(durationMins),
      vehicle_type: vehicleType,
      max_budget_inr: maxBudget ? Number(maxBudget) : undefined,
      facilities: facilities.length > 0 ? facilities : undefined,
    });
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) return;

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Enter') {
      if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
        e.preventDefault();
        handleSelectSuggestion(suggestions[highlightedIndex]);
      }
    } else if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  // Detect Live Location via HTML5 Geolocation API
  const handleDetectLiveLocation = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser.');
      return;
    }

    setDetectingLocation(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
          const geo = await reverseGeocodeCoords(latitude, longitude);
          const detectedName = geo.display_name || `Current Location (${latitude.toFixed(3)}, ${longitude.toFixed(3)})`;
          setPlaceName(detectedName);
          setCoords({ lat: latitude, lng: longitude });
          setShowSuggestions(false);

          toast.success(`📍 Live location detected: ${detectedName}`);

          onSearch({
            place_name: detectedName,
            lat: latitude,
            lng: longitude,
            date,
            start_time: startTime,
            duration_minutes: Number(durationMins),
            vehicle_type: vehicleType,
            max_budget_inr: maxBudget ? Number(maxBudget) : undefined,
            facilities: facilities.length > 0 ? facilities : undefined,
          });
        } catch (err) {
          const fallbackName = `Current Location (${latitude.toFixed(3)}, ${longitude.toFixed(3)})`;
          setPlaceName(fallbackName);
          setCoords({ lat: latitude, lng: longitude });
          onSearch({
            place_name: fallbackName,
            lat: latitude,
            lng: longitude,
            date,
            start_time: startTime,
            duration_minutes: Number(durationMins),
            vehicle_type: vehicleType,
            max_budget_inr: maxBudget ? Number(maxBudget) : undefined,
            facilities: facilities.length > 0 ? facilities : undefined,
          });
          toast.success('📍 Live coordinates detected!');
        } finally {
          setDetectingLocation(false);
        }
      },
      (error) => {
        setDetectingLocation(false);
        if (error.code === 1) {
          toast.error('Location permission denied. Please allow location access in your browser settings.');
        } else {
          toast.error('Unable to retrieve your live location. Please try again.');
        }
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 }
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    onSearch({
      place_name: placeName,
      lat: coords.lat || undefined,
      lng: coords.lng || undefined,
      date,
      start_time: startTime,
      duration_minutes: Number(durationMins),
      vehicle_type: vehicleType,
      max_budget_inr: maxBudget ? Number(maxBudget) : undefined,
      facilities: facilities.length > 0 ? facilities : undefined,
    });
  };

  const getCategoryBadge = (category) => {
    switch (category) {
      case 'parking':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-100 text-blue-700">
            🅿️ Parking
          </span>
        );
      case 'landmark':
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-purple-100 text-purple-700">
            🏛️ Landmark
          </span>
        );
      default:
        return (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-emerald-100 text-emerald-700">
            📍 Area
          </span>
        );
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200/80 shadow-md p-5 sm:p-6 relative">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Location input with Autocomplete & Live Location Button */}
        <div className="md:col-span-2 relative" ref={dropdownRef}>
          <div className="flex items-center justify-between mb-1.5">
            <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center">
              <FiMapPin className="text-blue-600 mr-1 text-sm" /> Destination / Area
            </label>
            <button
              type="button"
              onClick={handleDetectLiveLocation}
              disabled={detectingLocation}
              className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800 transition-colors bg-blue-50/80 hover:bg-blue-100 px-2.5 py-1 rounded-lg"
              title="Detect my current location"
            >
              {detectingLocation ? (
                <>
                  <FiLoader className="mr-1.5 animate-spin" /> Detecting...
                </>
              ) : (
                <>
                  <FiNavigation className="mr-1.5 text-blue-600" /> Live Location
                </>
              )}
            </button>
          </div>

          <div className="relative">
            <input
              type="text"
              value={placeName}
              onChange={(e) => {
                setPlaceName(e.target.value);
                // Reset coordinate lock on manual typing
                setCoords({ lat: null, lng: null });
              }}
              onFocus={() => {
                if (placeName && placeName.trim().length >= 3 && suggestions.length > 0) {
                  setShowSuggestions(true);
                }
              }}
              onKeyDown={handleKeyDown}
              placeholder="Search any city, area or landmark (e.g. Bangalore, Mumbai, Delhi, Hitech City)..."
              className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium pr-10"
              required
              autoComplete="off"
            />
            {loadingSuggestions && (
              <div className="absolute right-3.5 top-3 text-slate-400">
                <FiLoader className="animate-spin text-sm" />
              </div>
            )}
          </div>

          {/* Autocomplete Dropdown */}
          {showSuggestions && (
            <div className="absolute left-0 right-0 mt-1.5 bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-72 overflow-y-auto divide-y divide-slate-100 animate-in fade-in slide-in-from-top-1 duration-150">
              {loadingSuggestions && suggestions.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 flex items-center justify-center">
                  <FiLoader className="mr-2 animate-spin text-blue-600 text-sm" />
                  Finding matching locations...
                </div>
              ) : suggestions.length > 0 ? (
                suggestions.map((item, index) => (
                  <button
                    key={item.id || index}
                    type="button"
                    onClick={() => handleSelectSuggestion(item)}
                    className={`w-full text-left px-4 py-2.5 flex items-start justify-between hover:bg-blue-50/70 transition-colors ${
                      highlightedIndex === index ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex items-start space-x-2.5 pr-2">
                      <FiMapPin className="text-slate-400 mt-1 shrink-0 text-sm" />
                      <div>
                        <div className="text-sm font-semibold text-slate-900 leading-tight">
                          {item.name}
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                          {item.address}
                        </div>
                      </div>
                    </div>
                    <div className="shrink-0 mt-0.5">
                      {getCategoryBadge(item.category)}
                    </div>
                  </button>
                ))
              ) : (
                <div className="p-4 text-center text-xs text-slate-500">
                  No matching locations found for "{placeName}".
                </div>
              )}
            </div>
          )}
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

      {/* Row 2: Duration & Vehicle & Budget */}
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
