import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBookings } from '../api/bookings';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { Countdown } from '../components/common/Countdown';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { formatCurrency, formatDateTime } from '../utils/formatters';
import { BOOKING_STATUS_COLORS } from '../utils/constants';
import { FiCalendar, FiClock, FiMapPin, FiChevronRight } from 'react-icons/fi';

export const MyBookings = () => {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('ALL');

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const data = await getBookings(filter === 'ALL' ? undefined : filter);
      setBookings(data.bookings || []);
    } catch (err) {
      // Handled silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [filter]);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">My Bookings</h1>
          <p className="text-xs text-slate-500 mt-0.5">Manage your active reservations, parking passes, and receipts</p>
        </div>

        {/* Filter Tabs */}
        <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold self-start">
          {['ALL', 'CONFIRMED', 'PENDING_PAYMENT', 'CANCELLED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1.5 rounded-lg transition-colors ${
                filter === status ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
              }`}
            >
              {status.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : bookings.length > 0 ? (
        <div className="space-y-3">
          {bookings.map((b) => (
            <Link key={b.id} to={`/bookings/${b.id}`} className="block">
              <Card hover className="p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono font-bold text-xs bg-slate-100 text-slate-800 px-2 py-0.5 rounded">
                        #{b.id}
                      </span>
                      <h3 className="font-bold text-slate-900 text-base">{b.location_name}</h3>
                      <span
                        className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${
                          BOOKING_STATUS_COLORS[b.status] || 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {b.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-2">
                      <span className="flex items-center">
                        <FiMapPin className="mr-1 text-slate-400" /> Slot {b.slot_code} ({b.vehicle_type})
                      </span>
                      <span className="flex items-center">
                        <FiCalendar className="mr-1 text-slate-400" /> {formatDateTime(b.start_at)}
                      </span>
                      <span className="flex items-center">
                        <FiClock className="mr-1 text-slate-400" /> to {formatDateTime(b.end_at)}
                      </span>
                    </div>

                    {b.status === 'PENDING_PAYMENT' && b.time_remaining_seconds > 0 && (
                      <div className="mt-2.5">
                        <Countdown
                          initialSeconds={b.time_remaining_seconds}
                          onExpire={fetchBookings}
                          label="Unpaid hold expires in"
                        />
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between sm:justify-end sm:space-x-6 border-t sm:border-t-0 pt-3 sm:pt-0 border-slate-100">
                    <div className="text-right">
                      <span className="text-[11px] text-slate-400 uppercase tracking-wider block">Total</span>
                      <span className="text-lg font-black text-slate-900">{formatCurrency(b.total_paise)}</span>
                    </div>
                    <FiChevronRight className="text-slate-400 w-5 h-5 hidden sm:block" />
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      ) : (
        <Card className="p-12 text-center">
          <FiCalendar className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-bold text-slate-800 text-base">No bookings found</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            You don't have any {filter !== 'ALL' ? filter.toLowerCase().replace('_', ' ') : ''} bookings yet.
          </p>
          <div className="mt-5">
            <Link to="/search" className="inline-block">
              <span className="bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs px-4 py-2 rounded-lg shadow-sm">
                Search Parking Now
              </span>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
};
