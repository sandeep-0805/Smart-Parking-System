import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { createBooking, createPaymentOrder, verifyPayment } from '../../api/bookings';
import { formatCurrency, formatDateTime } from '../../utils/formatters';
import { Countdown } from '../common/Countdown';
import { Button } from '../common/Button';
import toast from 'react-hot-toast';
import { FiCheckCircle, FiShield, FiClock } from 'react-icons/fi';

export const BookingModal = ({ isOpen, onClose, slot, location, quote }) => {
  const [loading, setLoading] = useState(false);
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  if (!isOpen || !slot || !location) return null;

  const handleProceedToPay = async () => {
    if (!isAuthenticated) {
      toast.error('Please log in to book a slot.');
      navigate('/login');
      return;
    }

    setLoading(true);
    try {
      // 1. Transactional reservation
      const booking = await createBooking(
        {
          quote_id: slot.quote_id,
          source: 'MANUAL',
        },
        `idemp_${slot.quote_id}_${Date.now()}`
      );

      // If location is pay-at-venue, it confirms immediately!
      if (location.pay_at_venue || booking.status === 'CONFIRMED') {
        toast.success('Booking confirmed! You can pay at the venue.');
        navigate(`/bookings/${booking.id}`);
        onClose();
        return;
      }

      // 2. Otherwise initiate Razorpay order
      const order = await createPaymentOrder(booking.id);

      // 3. Open Razorpay Checkout modal
      const options = {
        key: order.key_id,
        amount: order.amount_paise,
        currency: order.currency,
        name: 'SmartParking',
        description: `Reservation for Slot ${slot.slot_code} at ${location.name}`,
        order_id: order.razorpay_order_id,
        handler: async function (response) {
          try {
            await verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            toast.success('Payment verified! Booking confirmed.');
            navigate(`/bookings/${booking.id}`);
            onClose();
          } catch (verErr) {
            toast.error('Payment verification failed.');
          }
        },
        prefill: {
          name: user?.full_name,
          email: user?.email,
          contact: user?.phone || '',
        },
        theme: {
          color: '#2563eb',
        },
      };

      if (window.Razorpay) {
        const rzp = new window.Razorpay(options);
        rzp.on('payment.failed', function (failResp) {
          toast.error(failResp.error?.description || 'Payment was cancelled or failed.');
        });
        rzp.open();
      } else {
        // Fallback demo mock verification if razorpay script isn't loaded (e.g. offline testing)
        toast('Testing mode: Simulating payment verification...');
        await verifyPayment({
          razorpay_order_id: order.razorpay_order_id,
          razorpay_payment_id: `pay_mock_${Date.now()}`,
          razorpay_signature: 'sig_mock_verified',
        });
        toast.success('Mock payment confirmed!');
        navigate(`/bookings/${booking.id}`);
        onClose();
      }
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Could not reserve slot. It may have just been booked.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-200 animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="bg-slate-50 border-b border-slate-200/80 px-6 py-4 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-slate-900 text-base">Confirm Reservation</h3>
            <p className="text-xs text-slate-500 mt-0.5">{location.name}</p>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-lg font-bold p-1"
          >
            &times;
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Slot & Price Banner */}
          <div className="bg-blue-50 border border-blue-200/80 rounded-xl p-4 flex items-center justify-between">
            <div>
              <span className="text-[11px] uppercase font-bold text-blue-700 tracking-wider">
                Slot Code
              </span>
              <div className="font-mono text-2xl font-black text-blue-900 mt-0.5">
                {slot.slot_code}
              </div>
              <span className="text-xs text-blue-600 font-medium">{slot.vehicle_type}</span>
            </div>
            <div className="text-right">
              <span className="text-[11px] uppercase font-bold text-slate-500 tracking-wider">
                Total Price
              </span>
              <div className="text-2xl font-black text-slate-900 mt-0.5">
                {formatCurrency(slot.total_price_paise)}
              </div>
              <span className="text-[11px] text-slate-500">Taxes included</span>
            </div>
          </div>

          {/* Quote validity countdown */}
          <div className="flex items-center justify-between text-xs py-2 px-3 bg-amber-50/80 border border-amber-200/80 rounded-lg">
            <span className="text-amber-800 font-medium">Guaranteed price window</span>
            <Countdown initialSeconds={600} onExpire={onClose} label="Quote expires" />
          </div>

          {/* Reason badges */}
          {slot.reason_tags?.length > 0 && (
            <div>
              <span className="text-xs font-semibold text-slate-600 block mb-1.5">
                AI Match Highlights:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {slot.reason_tags.map((tag, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center text-xs bg-slate-100 text-slate-700 px-2.5 py-1 rounded-md font-medium"
                  >
                    <FiCheckCircle className="text-emerald-500 mr-1.5 text-xs" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Security guarantee */}
          <div className="text-xs text-slate-500 flex items-start space-x-2 pt-2 border-t border-slate-100">
            <FiShield className="text-blue-600 w-4 h-4 mt-0.5 shrink-0" />
            <span>
              Zero double-bookings guarantee. Your 15-minute time block is row-locked in MySQL.
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-slate-50 border-t border-slate-200/80 px-6 py-4 flex items-center justify-end space-x-3">
          <Button variant="outline" onClick={onClose} disabled={loading}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleProceedToPay}
            loading={loading}
            className="px-6"
          >
            {location.pay_at_venue ? 'Confirm (Pay at Venue)' : 'Proceed to Checkout'}
          </Button>
        </div>
      </div>
    </div>
  );
};
