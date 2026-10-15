import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getBooking, cancelBooking, createPaymentOrder, verifyPayment } from '../../api/bookings';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Countdown } from '../components/common/Countdown';
import { LoadingSpinner } from '../common/LoadingSpinner';
import { formatCurrency, formatDateTime } from '../../utils/formatters';
import { BOOKING_STATUS_COLORS } from '../../utils/constants';
import { useAuth } from '../../context/AuthContext';
import { FiMapPin, FiCalendar, FiClock, FiShield, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';
import toast from 'react-hot-toast';

export const BookingDetails = () => {
  const { id } = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [paying, setPaying] = useState(false);
  const { user } = useAuth();
  const navigate = useNavigate();

  const fetchDetails = async () => {
    try {
      setLoading(true);
      const data = await getBooking(id);
      setBooking(data);
    } catch (err) {
      toast.error('Failed to load booking details.');
      navigate('/bookings');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handlePayNow = async () => {
    setPaying(true);
    try {
      const order = await createPaymentOrder(booking.id);
      const options = {
        key: order.key_id,
        amount: order.amount_paise,
        currency: order.currency,
        name: 'SmartParking',
        description: `Payment for Booking #${booking.id}`,
        order_id: order.razorpay_order_id,
        handler: async function (response) {
          try {
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            toast.success('Payment confirmed!');
            fetchDetails();
          } catch {
            toast.error('Payment verification failed.');
          }
        },
        prefill: {
          name: user?.full_name,
          email: user?.email,
          contact: user?.phone || '',
        },
        theme: { color: '#2563eb' },
      };

      if (window.Razorpay) {
        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        // Mock fallback
        toast('Simulating payment capture...');
        await verifyPayment({
          razorpay_order_id: order.razorpay_order_id,
          razorpay_payment_id: `pay_mock_${Date.now()}`,
          razorpay_signature: 'sig_mock_verified',
        });
        toast.success('Mock payment captured!');
        fetchDetails();
      }
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Payment initiation failed.');
    } finally {
      setPaying(false);
    }
  };

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this booking reservation?')) return;
    setCancelling(true);
    try {
      await cancelBooking(booking.id, 'Cancelled from booking details page');
      toast.success('Booking cancelled.');
      fetchDetails();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Cancellation failed.');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) {
    return (
      <div className="py-24">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!booking) return null;

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Card */}
      <Card className="p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-slate-100 gap-3">
          <div>
            <div className="flex items-center space-x-2.5">
              <span className="font-mono font-bold text-sm bg-slate-100 px-2 py-0.5 rounded text-slate-700">
                Booking #{booking.id}
              </span>
              <span
                className={`text-xs px-2.5 py-0.5 rounded-full border font-bold ${
                  BOOKING_STATUS_COLORS[booking.status] || 'bg-slate-100 text-slate-700'
                }`}
              >
                {booking.status.replace('_', ' ')}
              </span>
            </div>
            <h1 className="text-2xl font-black text-slate-900 mt-2">{booking.location_name}</h1>
            <p className="text-xs text-slate-500 mt-0.5 flex items-center">
              <FiMapPin className="mr-1 text-slate-400" /> {booking.location_address}
            </p>
          </div>

          {booking.status === 'PENDING_PAYMENT' && booking.time_remaining_seconds > 0 && (
            <Countdown
              initialSeconds={booking.time_remaining_seconds}
              onExpire={fetchDetails}
              label="Payment Hold Expires"
            />
          )}
        </div>

        {/* Slot Pass & QR */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 py-6 border-b border-slate-100">
          <div className="space-y-3">
            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
                Reserved Slot
              </span>
              <div className="font-mono text-3xl font-black text-blue-600 mt-0.5">
                {booking.slot_code}
              </div>
              <span className="text-xs text-slate-500 font-medium">Vehicle: {booking.vehicle_type}</span>
            </div>

            <div>
              <span className="text-[11px] uppercase font-bold text-slate-400 tracking-wider">
                Booking Window
              </span>
              <p className="text-sm font-semibold text-slate-800 mt-0.5">
                {formatDateTime(booking.start_at)}
              </p>
              <p className="text-xs text-slate-500">to {formatDateTime(booking.end_at)}</p>
            </div>
          </div>

          {/* Digital Entry Pass / QR */}
          <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 flex flex-col items-center justify-center text-center">
            {booking.status === 'CONFIRMED' ? (
              <>
                <div className="w-28 h-28 bg-white border border-slate-300 rounded-lg p-2 flex items-center justify-center shadow-xs">
                  {/* SVG QR Code Simulation */}
                  <div className="grid grid-cols-6 gap-1 w-full h-full p-1 bg-slate-900 rounded">
                    {Array.from({ length: 36 }).map((_, i) => (
                      <div
                        key={i}
                        className={`rounded-2xs ${i % 3 === 0 || i % 7 === 0 ? 'bg-white' : 'bg-transparent'}`}
                      />
                    ))}
                  </div>
                </div>
                <span className="text-[11px] font-bold text-emerald-700 mt-2 flex items-center">
                  <FiCheckCircle className="mr-1" /> Valid Parking Entry Pass
                </span>
                <span className="text-[10px] text-slate-400 mt-0.5 font-mono">
                  REF: PKG-{booking.id}-{booking.slot_code}
                </span>
              </>
            ) : (
              <div className="text-center py-4 text-xs text-slate-400">
                <FiClock className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                Pass generated once payment is confirmed
              </div>
            )}
          </div>
        </div>

        {/* Pricing Summary */}
        <div className="py-6 border-b border-slate-100 flex items-center justify-between">
          <div>
            <span className="text-sm font-bold text-slate-800">Total Price Paid / Quoted</span>
            <p className="text-xs text-slate-500">Fixed at quote time (FR-P3)</p>
          </div>
          <span className="text-2xl font-black text-slate-900">{formatCurrency(booking.total_paise)}</span>
        </div>

        {/* Actions */}
        <div className="pt-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            {booking.status === 'CONFIRMED' && (
              <p className="text-xs text-slate-500">
                Cancellation policy: 100% refund &ge; 60m before start, 50% inside 60m.
              </p>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {(booking.status === 'PENDING_PAYMENT' || booking.status === 'CONFIRMED') && (
              <Button
                variant="danger"
                size="sm"
                onClick={handleCancel}
                loading={cancelling}
              >
                Cancel Booking
              </Button>
            )}

            {booking.status === 'PENDING_PAYMENT' && (
              <Button
                variant="primary"
                onClick={handlePayNow}
                loading={paying}
              >
                Pay Now with Razorpay
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};
