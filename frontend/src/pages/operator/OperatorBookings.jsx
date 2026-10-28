import React, { useState, useEffect } from 'react';
import { getOperatorBookings } from '../../api/operator';
import { Card } from '../../components/common/Card';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { formatCurrency, formatDateTime } from '../../utils/formatters';
import { BOOKING_STATUS_COLORS } from '../../utils/constants';
import toast from 'react-hot-toast';
import { FiCalendar, FiClock, FiMapPin, FiTruck, FiRefreshCw } from 'react-icons/fi';

export const OperatorBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const data = await getOperatorBookings();
      setBookings(data || []);
    } catch {
      toast.error('Failed to load operator bookings.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const filteredBookings = bookings.filter((b) => {
    if (filter === 'ALL') return true;
    return b.status === filter;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Location Reservations</h1>
          <p className="text-xs text-slate-500 mt-0.5">Live incoming customer bookings for your parking locations</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchBookings}
            className="inline-flex items-center px-3 py-1.5 text-xs font-semibold bg-white border border-slate-200 rounded-lg text-slate-600 hover:text-slate-900 shadow-2xs"
          >
            <FiRefreshCw className="mr-1.5" /> Refresh
          </button>
          {/* Status Filter */}
          <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold">
            {['ALL', 'CONFIRMED', 'PENDING_PAYMENT', 'CANCELLED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`px-3 py-1 rounded-lg transition-colors ${
                  filter === st ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
                }`}
              >
                {st.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="py-24">
          <LoadingSpinner size="lg" />
        </div>
      ) : filteredBookings.length > 0 ? (
        <Card className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 uppercase font-semibold text-[11px] tracking-wider">
                  <th className="py-3 px-4">Booking ID</th>
                  <th className="py-3 px-4">Location</th>
                  <th className="py-3 px-4">Slot</th>
                  <th className="py-3 px-4">Start Time</th>
                  <th className="py-3 px-4">End Time</th>
                  <th className="py-3 px-4">Total Amount</th>
                  <th className="py-3 px-4">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredBookings.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-slate-800">
                      #{b.id}
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-900">
                      {b.location_name}
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-mono bg-blue-50 text-blue-700 px-2 py-0.5 rounded font-bold">
                        {b.slot_code}
                      </span>{' '}
                      <span className="text-slate-400 text-[11px]">({b.vehicle_type})</span>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {formatDateTime(b.start_at)}
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      {formatDateTime(b.end_at)}
                    </td>
                    <td className="py-3 px-4 font-bold text-slate-900">
                      {formatCurrency(b.total_paise)}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`text-[11px] px-2.5 py-0.5 rounded-full border font-semibold ${
                          BOOKING_STATUS_COLORS[b.status] || 'bg-slate-100 text-slate-700 border-slate-200'
                        }`}
                      >
                        {b.status.replace('_', ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      ) : (
        <Card className="p-12 text-center">
          <FiCalendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-bold text-slate-800 text-base">No bookings found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            No reservations matching this filter have been made for your locations yet.
          </p>
        </Card>
      )}
    </div>
  );
};
