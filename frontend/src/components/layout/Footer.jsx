import React from 'react';

export const Footer = () => {
  return (
    <footer className="bg-white border-t border-slate-200 mt-auto py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-4">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-slate-800">SmartParking Platform</span>
          <span>•</span>
          <span>AI advises, backend decides</span>
        </div>
        <div className="flex space-x-6 text-slate-400">
          <span>Razorpay Test Mode</span>
          <span>•</span>
          <span>Leaflet + OSM</span>
          <span>•</span>
          <span>MySQL 8.4 LTS</span>
        </div>
      </div>
    </footer>
  );
};
