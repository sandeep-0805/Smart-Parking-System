import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { SearchForm } from '../components/search/SearchForm';
import { FiCheckCircle, FiShield, FiCpu, FiClock, FiMapPin, FiCreditCard } from 'react-icons/fi';
import { Card } from '../components/common/Card';

export const Home = () => {
  const navigate = useNavigate();

  const handleHeroSearch = (searchParams) => {
    const query = new URLSearchParams();
    if (searchParams.place_name) query.set('place_name', searchParams.place_name);
    if (searchParams.lat) query.set('lat', searchParams.lat);
    if (searchParams.lng) query.set('lng', searchParams.lng);
    if (searchParams.date) query.set('date', searchParams.date);
    if (searchParams.start_time) query.set('start_time', searchParams.start_time);
    if (searchParams.duration_minutes) query.set('duration_minutes', searchParams.duration_minutes);
    if (searchParams.vehicle_type) query.set('vehicle_type', searchParams.vehicle_type);
    navigate(`/search?${query.toString()}`);
  };

  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-b from-blue-50/70 via-slate-50 to-white pt-12 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center space-x-2 bg-blue-100/80 text-blue-700 text-xs font-bold px-3.5 py-1.5 rounded-full uppercase tracking-wider">
            <span className="w-2 h-2 rounded-full bg-blue-600 animate-ping mr-1"></span>
            Deterministic Core • 5 AI Modules
          </div>
          <h1 className="text-4xl sm:text-5xl font-black text-slate-900 tracking-tight leading-tight">
            AI-Powered Smart Parking <br />
            <span className="text-blue-600">Find, Reserve & Pay Seamlessly</span>
          </h1>
          <p className="text-base sm:text-lg text-slate-600 max-w-2xl mx-auto">
            Zero double-bookings with database-guaranteed row locking. Explainable AI slot recommendations, demand-aware pricing, and automated booking rules.
          </p>

          {/* Search Card Overlay */}
          <div className="pt-6 max-w-4xl mx-auto text-left">
            <SearchForm onSearch={handleHeroSearch} />
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
            Engineered for Absolute Reliability
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            AI advises, backend decides. Every transaction is computed by deterministic MySQL code with strict ACID guarantees.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="p-6">
            <div className="w-12 h-12 rounded-xl bg-blue-100 text-blue-600 flex items-center justify-center text-2xl mb-4">
              <FiShield />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">Zero Double-Bookings</h3>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Unique 15-minute time block constraints in MySQL make overlapping reservations physically impossible at the database level.
            </p>
          </Card>

          <Card className="p-6">
            <div className="w-12 h-12 rounded-xl bg-emerald-100 text-emerald-600 flex items-center justify-center text-2xl mb-4">
              <FiCpu />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">5 Explainable AI Modules</h3>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Normalized candidate ranker with reason tags, Ollama LLM chat assistant, ML demand forecasts, dynamic pricing, and auto-booking.
            </p>
          </Card>

          <Card className="p-6">
            <div className="w-12 h-12 rounded-xl bg-purple-100 text-purple-600 flex items-center justify-center text-2xl mb-4">
              <FiCreditCard />
            </div>
            <h3 className="font-bold text-slate-900 text-lg">Secure Test Payments</h3>
            <p className="text-sm text-slate-600 mt-2 leading-relaxed">
              Razorpay integration with HMAC-SHA256 signature verification for callbacks and raw webhooks. Automated hold expiry and refund policies.
            </p>
          </Card>
        </div>
      </section>
    </div>
  );
};
