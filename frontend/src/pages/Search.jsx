import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { SearchForm } from '../components/search/SearchForm';
import { LocationCard } from '../components/search/LocationCard';
import { MapView } from '../components/search/MapView';
import { BookingModal } from '../components/booking/BookingModal';
import { searchParking, reverseGeocodeCoords } from '../api/search';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { FiList, FiMap, FiAlertCircle } from 'react-icons/fi';
import toast from 'react-hot-toast';

export const Search = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState('split'); // 'split', 'list', 'map'
  const [selectedLocation, setSelectedLocation] = useState(null);
  
  // Dynamic destination coordinates (selected via map, live GPS, or suggestions)
  const initialLat = searchParams.get('lat') ? Number(searchParams.get('lat')) : null;
  const initialLng = searchParams.get('lng') ? Number(searchParams.get('lng')) : null;
  const [destinationCoords, setDestinationCoords] = useState(
    initialLat && initialLng ? { lat: initialLat, lng: initialLng } : null
  );
  const [destinationName, setDestinationName] = useState(searchParams.get('place_name') || 'Hitech City');

  // Booking Modal State
  const [bookingModalOpen, setBookingModalOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [modalLocation, setModalLocation] = useState(null);

  const executeSearch = async (params) => {
    setLoading(true);
    try {
      const data = await searchParking(params);
      setResults(data);
      if (data?.target_lat && data?.target_lng) {
        setDestinationCoords({ lat: data.target_lat, lng: data.target_lng });
      }
      if (data?.place_name) {
        setDestinationName(data.place_name);
      }
    } catch (err) {
      toast.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const pLat = searchParams.get('lat') ? Number(searchParams.get('lat')) : null;
    const pLng = searchParams.get('lng') ? Number(searchParams.get('lng')) : null;
    const pName = searchParams.get('place_name') || 'Hitech City';

    if (pLat && pLng) {
      setDestinationCoords({ lat: pLat, lng: pLng });
    } else {
      setDestinationCoords(null);
    }
    setDestinationName(pName);

    const params = {
      place_name: pName,
      lat: pLat || undefined,
      lng: pLng || undefined,
      date: searchParams.get('date') || new Date().toISOString().split('T')[0],
      start_time: searchParams.get('start_time') || '10:00',
      duration_minutes: Number(searchParams.get('duration_minutes')) || 120,
      vehicle_type: searchParams.get('vehicle_type') || 'CAR',
      max_budget_inr: searchParams.get('max_budget_inr') ? Number(searchParams.get('max_budget_inr')) : undefined,
    };
    executeSearch(params);
  }, [searchParams]);

  const handleFormSearch = (params) => {
    const nextParams = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        nextParams.set(k, v);
      }
    });
    setSearchParams(nextParams);
  };

  // Map click handler to set destination directly by clicking any spot
  const handleMapClick = async (latlng) => {
    try {
      const geo = await reverseGeocodeCoords(latlng.lat, latlng.lng);
      const place = geo.display_name || `Location (${latlng.lat.toFixed(3)}, ${latlng.lng.toFixed(3)})`;
      setDestinationCoords({ lat: latlng.lat, lng: latlng.lng });
      setDestinationName(place);
      toast.success(`📍 Destination set: ${place}`);

      const nextParams = new URLSearchParams(searchParams);
      nextParams.set('place_name', place);
      nextParams.set('lat', latlng.lat.toFixed(6));
      nextParams.set('lng', latlng.lng.toFixed(6));
      setSearchParams(nextParams);
    } catch (err) {
      const fallback = `Pinned Location (${latlng.lat.toFixed(3)}, ${latlng.lng.toFixed(3)})`;
      setDestinationCoords({ lat: latlng.lat, lng: latlng.lng });
      setDestinationName(fallback);
      const nextParams = new URLSearchParams(searchParams);
      nextParams.set('place_name', fallback);
      nextParams.set('lat', latlng.lat.toFixed(6));
      nextParams.set('lng', latlng.lng.toFixed(6));
      setSearchParams(nextParams);
    }
  };

  const handleSelectSlot = (slot, location) => {
    setSelectedSlot(slot);
    setModalLocation(location);
    setBookingModalOpen(true);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Search Header Form */}
      <SearchForm
        initialValues={{
          place_name: destinationName,
          lat: destinationCoords?.lat,
          lng: destinationCoords?.lng,
          date: searchParams.get('date') || '',
          start_time: searchParams.get('start_time') || '',
          duration_minutes: Number(searchParams.get('duration_minutes')) || 120,
          vehicle_type: searchParams.get('vehicle_type') || 'CAR',
          max_budget_inr: searchParams.get('max_budget_inr') || '',
        }}
        onSearch={handleFormSearch}
        loading={loading}
      />

      {/* Basic Fallback Warning if AI Service is Down (FR-R4) */}
      {results?.ranking_type === 'basic' && (
        <div className="flex items-center text-xs text-amber-800 bg-amber-50 border border-amber-200 px-4 py-2.5 rounded-xl">
          <FiAlertCircle className="mr-2 text-base shrink-0" />
          <span>
            AI recommender is offline or timed out; displaying basic distance-sorted results.
          </span>
        </div>
      )}

      {/* View Toggle Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            {results?.total_locations || 0} Parking Locations Found within 5 km
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Available slots around {destinationName || 'your destination'} (verified prices)
          </p>
        </div>

        <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold">
          <button
            onClick={() => setViewMode('split')}
            className={`hidden lg:flex items-center px-3 py-1.5 rounded-lg transition-colors ${
              viewMode === 'split' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            Split View
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`flex items-center px-3 py-1.5 rounded-lg transition-colors ${
              viewMode === 'list' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiList className="mr-1.5" /> List
          </button>
          <button
            onClick={() => setViewMode('map')}
            className={`flex items-center px-3 py-1.5 rounded-lg transition-colors ${
              viewMode === 'map' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiMap className="mr-1.5" /> Map
          </button>
        </div>
      </div>

      {/* Main Results View */}
      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[550px]">
          {/* List of cards */}
          {(viewMode === 'split' || viewMode === 'list') && (
            <div className={`space-y-4 ${viewMode === 'split' ? 'lg:col-span-6' : 'lg:col-span-12'}`}>
              {results?.locations?.length > 0 ? (
                results.locations.map((loc) => (
                  <LocationCard
                    key={loc.location_id}
                    location={loc}
                    onSelectSlot={handleSelectSlot}
                    isSelected={selectedLocation?.location_id === loc.location_id}
                  />
                ))
              ) : (
                <div className="bg-white rounded-2xl border border-slate-200/90 shadow-sm p-6 sm:p-8 space-y-5 text-center">
                  <div className="w-14 h-14 bg-amber-50 text-amber-600 rounded-full flex items-center justify-center mx-auto text-2xl shadow-inner">
                    🅿️
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-lg">
                      No parking stations found within 5 km
                    </h3>
                    <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                      There are currently no active parking facilities within a 5 km radius of{' '}
                      <strong className="text-slate-800">{destinationName}</strong>.
                    </p>
                  </div>

                  {results?.nearest_location && (
                    <div className="mt-4 text-left bg-gradient-to-r from-blue-50/80 to-indigo-50/60 border border-blue-200/90 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                      <div className="space-y-1">
                        <span className="text-[10px] font-extrabold uppercase tracking-wider text-blue-700 bg-blue-100/90 px-2.5 py-0.5 rounded-full inline-block">
                          Nearest Available Station ({results.nearest_location.distance_km} km away)
                        </span>
                        <h4 className="font-bold text-slate-900 text-sm sm:text-base">
                          {results.nearest_location.name}
                        </h4>
                        <p className="text-xs text-slate-600">
                          {results.nearest_location.address}
                        </p>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          const nextParams = new URLSearchParams(searchParams);
                          nextParams.set('place_name', results.nearest_location.name);
                          nextParams.set('lat', results.nearest_location.lat);
                          nextParams.set('lng', results.nearest_location.lng);
                          setSearchParams(nextParams);
                        }}
                        className="inline-flex items-center justify-center px-4 py-2.5 text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-xl shadow-sm transition-all hover:shadow-md shrink-0 cursor-pointer"
                      >
                        Search Around This Station ({results.nearest_location.distance_km} km)
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* Leaflet Map */}
          {(viewMode === 'split' || viewMode === 'map') && (
            <div className={`sticky top-24 ${viewMode === 'split' ? 'lg:col-span-6 h-[600px]' : 'lg:col-span-12 h-[650px]'}`}>
              <MapView
                locations={results?.locations || []}
                onSelectLocation={(loc) => setSelectedLocation(loc)}
                selectedLocationId={selectedLocation?.location_id}
                onMapClick={handleMapClick}
                destinationCoords={destinationCoords}
                destinationName={destinationName}
              />
            </div>
          )}
        </div>
      )}

      {/* Reservation & Payment Modal */}
      <BookingModal
        isOpen={bookingModalOpen}
        onClose={() => setBookingModalOpen(false)}
        slot={selectedSlot}
        location={modalLocation}
      />
    </div>
  );
};
