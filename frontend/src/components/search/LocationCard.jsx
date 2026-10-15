import React from 'react';
import { FiMapPin, FiCheck, FiZap, FiShield } from 'react-icons/fi';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { Button } from '../common/Button';
import { formatCurrency, formatDistance } from '../../utils/formatters';

export const LocationCard = ({ location, onSelectSlot, isSelected }) => {
  const topSlot = location.slots?.[0];

  return (
    <Card
      hover
      className={`p-5 transition-all ${
        isSelected ? 'ring-2 ring-blue-600 border-blue-600 shadow-md' : ''
      }`}
    >
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        {/* Left: Info */}
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            <h3 className="font-bold text-base text-slate-900">{location.name}</h3>
            {location.pay_at_venue && (
              <Badge variant="success" size="sm">Pay at Venue</Badge>
            )}
          </div>
          <p className="text-xs text-slate-500 mt-1 flex items-center">
            <FiMapPin className="text-slate-400 mr-1 shrink-0" />
            <span className="truncate">{location.address}</span>
            <span className="mx-2 text-slate-300">•</span>
            <span className="font-semibold text-blue-600">{formatDistance(location.distance_m)} away</span>
          </p>

          {/* Facilities */}
          {location.facilities?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2.5">
              {location.facilities.map((fac) => (
                <span
                  key={fac}
                  className="text-[10px] uppercase font-bold tracking-wider bg-slate-100 text-slate-600 px-2 py-0.5 rounded"
                >
                  {fac.replace('_', ' ')}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Right: Slots summary & Best Price */}
        <div className="text-right sm:border-l sm:border-slate-100 sm:pl-4 sm:min-w-[130px]">
          <span className="text-[11px] text-slate-400 uppercase tracking-wider block">From</span>
          <span className="text-xl font-extrabold text-slate-900 block">
            {topSlot ? formatCurrency(topSlot.total_price_paise) : 'N/A'}
          </span>
          <span className="text-xs text-emerald-600 font-semibold block mt-0.5">
            {location.available_slots_count} slots free
          </span>
        </div>
      </div>

      {/* Available Slots list */}
      {location.slots && location.slots.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100 space-y-2">
          {location.slots.map((slot) => (
            <div
              key={slot.slot_id}
              className="flex items-center justify-between bg-slate-50/80 hover:bg-blue-50/60 p-2.5 rounded-xl border border-slate-200/60 transition-colors"
            >
              <div className="flex items-center space-x-2.5">
                <span className="font-mono font-bold text-xs bg-white text-slate-800 px-2.5 py-1 rounded-md border border-slate-200 shadow-2xs">
                  {slot.slot_code}
                </span>
                <span className="text-xs text-slate-600 font-medium">{slot.vehicle_type}</span>
                {/* Reason tags */}
                <div className="hidden sm:flex items-center space-x-1">
                  {slot.reason_tags?.map((t, idx) => (
                    <Badge key={idx} variant="primary" size="sm">
                      {t}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span className="font-extrabold text-sm text-slate-900">
                  {formatCurrency(slot.total_price_paise)}
                </span>
                <Button
                  size="sm"
                  variant="primary"
                  onClick={() => onSelectSlot(slot, location)}
                >
                  Book Slot
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};
