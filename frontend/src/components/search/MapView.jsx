import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import { formatCurrency } from '../../utils/formatters';

// Fix default leaflet marker icon issues in Webpack/Vite
const defaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Destination Target Pin Icon
const destinationIcon = L.divIcon({
  className: 'custom-destination-marker',
  html: `<div style="position: relative; display: flex; align-items: center; justify-content: center; width: 36px; height: 36px;">
    <div style="position: absolute; width: 36px; height: 36px; background-color: rgba(239, 68, 68, 0.35); border-radius: 9999px; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
    <div style="width: 32px; height: 32px; background-color: #ef4444; border: 2.5px solid white; border-radius: 9999px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; font-size: 16px;">
      📍
    </div>
  </div>`,
  iconSize: [36, 36],
  iconAnchor: [18, 36],
  popupAnchor: [0, -36],
});

// User Live Location Icon
const userLiveIcon = L.divIcon({
  className: 'custom-user-live-marker',
  html: `<div style="position: relative; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
    <div style="position: absolute; width: 28px; height: 28px; background-color: rgba(59, 130, 246, 0.4); border-radius: 9999px; animation: ping 1.8s cubic-bezier(0, 0, 0.2, 1) infinite;"></div>
    <div style="width: 16px; height: 16px; background-color: #2563eb; border: 2.5px solid white; border-radius: 9999px; box-shadow: 0 2px 4px rgba(0,0,0,0.25);"></div>
  </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

// Map click listener component
const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click(e) {
      if (onMapClick) {
        onMapClick(e.latlng);
      }
    },
  });
  return null;
};

// Component to dynamically adjust map bounds or pan to selected destination
const MapBoundsUpdater = ({ locations, destinationCoords }) => {
  const map = useMap();

  useEffect(() => {
    if (destinationCoords && destinationCoords.lat && destinationCoords.lng) {
      map.flyTo([destinationCoords.lat, destinationCoords.lng], 14, { duration: 1.2 });
    } else if (locations && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map((l) => [l.lat, l.lng]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  }, [locations, destinationCoords, map]);

  return null;
};

export const MapView = ({
  locations = [],
  onSelectLocation,
  selectedLocationId,
  onMapClick,
  destinationCoords = null,
  destinationName = '',
  userLiveCoords = null,
}) => {
  const defaultCenter = destinationCoords?.lat && destinationCoords?.lng
    ? [destinationCoords.lat, destinationCoords.lng]
    : [17.4435, 78.3772]; // Hyderabad Hitech City

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden border border-slate-200/80 shadow-sm relative min-h-[400px]">
      {/* Interactive Helper Badge */}
      <div className="absolute top-3 left-3 z-[1000] bg-white/95 backdrop-blur-md px-3.5 py-1.5 rounded-full border border-slate-200 shadow-md text-xs font-semibold text-slate-700 flex items-center pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-blue-600 mr-2 animate-pulse"></span>
        Click anywhere on map to set destination
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="h-full w-full cursor-crosshair"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapClickHandler onMapClick={onMapClick} />
        <MapBoundsUpdater locations={locations} destinationCoords={destinationCoords} />

        {/* Selected Destination Pin */}
        {destinationCoords && destinationCoords.lat && destinationCoords.lng && (
          <Marker
            position={[destinationCoords.lat, destinationCoords.lng]}
            icon={destinationIcon}
          >
            <Popup autoPan={false}>
              <div className="p-1">
                <span className="text-[10px] font-bold text-red-600 uppercase tracking-wider block">
                  Target Destination
                </span>
                <h4 className="font-extrabold text-slate-900 text-sm mt-0.5">
                  {destinationName || 'Pinned Destination'}
                </h4>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Lat: {destinationCoords.lat.toFixed(4)}, Lng: {destinationCoords.lng.toFixed(4)}
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* User Live Location Beacon */}
        {userLiveCoords && userLiveCoords.lat && userLiveCoords.lng && (
          <Marker
            position={[userLiveCoords.lat, userLiveCoords.lng]}
            icon={userLiveIcon}
          >
            <Popup autoPan={false}>
              <div className="p-1">
                <span className="text-[10px] font-bold text-blue-600 uppercase tracking-wider block">
                  Your Current Location
                </span>
                <p className="text-xs font-semibold text-slate-800 mt-0.5">
                  GPS Live Signal
                </p>
              </div>
            </Popup>
          </Marker>
        )}

        {/* Parking Locations */}
        {locations.map((loc) => {
          const topSlot = loc.slots?.[0];
          return (
            <Marker
              key={loc.location_id}
              position={[loc.lat, loc.lng]}
              icon={defaultIcon}
              eventHandlers={{
                click: () => onSelectLocation && onSelectLocation(loc),
              }}
            >
              <Popup>
                <div className="p-1 max-w-[200px]">
                  <h4 className="font-bold text-slate-900 text-sm">{loc.name}</h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">{loc.address}</p>
                  <div className="mt-2 flex items-center justify-between text-xs pt-1.5 border-t border-slate-100">
                    <span className="font-semibold text-emerald-600">
                      {loc.available_slots_count} free
                    </span>
                    <span className="font-extrabold text-slate-900">
                      {topSlot ? formatCurrency(topSlot.total_price_paise) : ''}
                    </span>
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
};
