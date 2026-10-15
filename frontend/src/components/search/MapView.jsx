import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
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

// Component to dynamically adjust map bounds based on locations
const MapBoundsUpdater = ({ locations }) => {
  const map = useMap();

  useEffect(() => {
    if (locations && locations.length > 0) {
      const bounds = L.latLngBounds(locations.map((l) => [l.lat, l.lng]));
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  }, [locations, map]);

  return null;
};

export const MapView = ({ locations, onSelectLocation, selectedLocationId }) => {
  const defaultCenter = [17.4435, 78.3772]; // Hyderabad Hitech City

  return (
    <div className="h-full w-full rounded-2xl overflow-hidden border border-slate-200/80 shadow-sm relative min-h-[400px]">
      <MapContainer
        center={defaultCenter}
        zoom={13}
        scrollWheelZoom={true}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapBoundsUpdater locations={locations} />

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
