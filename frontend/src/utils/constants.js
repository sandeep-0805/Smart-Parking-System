export const VEHICLE_TYPES = [
  { value: 'CAR', label: 'Car / Sedan' },
  { value: 'SUV', label: 'SUV' },
  { value: 'MOTORCYCLE', label: 'Motorcycle / Scooter' },
  { value: 'EV', label: 'Electric Vehicle (EV)' },
  { value: 'TRUCK', label: 'Truck / Large' },
];

export const FACILITY_OPTIONS = [
  { id: 'ev_charging', label: 'EV Charging' },
  { id: 'covered', label: 'Covered Parking' },
  { id: 'cctv', label: 'CCTV Monitored' },
  { id: 'disabled_access', label: 'Disabled Access' },
  { id: 'valet', label: 'Valet Service' },
];

export const BOOKING_STATUS_COLORS = {
  PENDING_PAYMENT: 'bg-amber-100 text-amber-800 border-amber-300',
  CONFIRMED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  CANCELLED: 'bg-rose-100 text-rose-800 border-rose-300',
  EXPIRED: 'bg-slate-100 text-slate-800 border-slate-300',
  COMPLETED: 'bg-blue-100 text-blue-800 border-blue-300',
  REFUNDED: 'bg-purple-100 text-purple-800 border-purple-300',
};
