import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getSlots, createSlot, bulkCreateSlots, blockSlot, unblockSlot } from '../../api/slots';
import { getLocation } from '../../api/locations';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { VEHICLE_TYPES } from '../../utils/constants';
import toast from 'react-hot-toast';
import { FiPlus, FiArrowLeft, FiSlash, FiCheck, FiLayers } from 'react-icons/fi';

export const ManageSlots = () => {
  const { id: locationId } = useParams();
  const [location, setLocation] = useState(null);
  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);

  // Single Slot Modal
  const [singleModalOpen, setSingleModalOpen] = useState(false);
  const [slotCode, setSlotCode] = useState('');
  const [vehicleType, setVehicleType] = useState('CAR');

  // Bulk Modal
  const [bulkModalOpen, setBulkModalOpen] = useState(false);
  const [prefix, setPrefix] = useState('B');
  const [count, setCount] = useState(10);
  const [bulkVehicle, setBulkVehicle] = useState('CAR');

  const fetchData = async () => {
    try {
      setLoading(true);
      const [locData, slotsData] = await Promise.all([
        getLocation(locationId),
        getSlots(locationId),
      ]);
      setLocation(locData);
      setSlots(slotsData);
    } catch {
      toast.error('Failed to load slots.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [locationId]);

  const handleToggleBlock = async (slot) => {
    try {
      if (slot.status === 'ACTIVE') {
        await blockSlot(slot.id);
        toast.success(`Slot ${slot.code} blocked.`);
      } else {
        await unblockSlot(slot.id);
        toast.success(`Slot ${slot.code} activated.`);
      }
      fetchData();
    } catch {
      toast.error('Failed to update slot status.');
    }
  };

  const handleCreateSingle = async (e) => {
    e.preventDefault();
    try {
      await createSlot(locationId, {
        code: slotCode.toUpperCase(),
        vehicle_type: vehicleType,
      });
      toast.success(`Slot ${slotCode} created!`);
      setSingleModalOpen(false);
      setSlotCode('');
      fetchData();
    } catch {
      toast.error('Failed to create slot.');
    }
  };

  const handleCreateBulk = async (e) => {
    e.preventDefault();
    try {
      await bulkCreateSlots(locationId, {
        prefix: prefix.toUpperCase(),
        count: Number(count),
        vehicle_type: bulkVehicle,
      });
      toast.success(`Generated ${count} slots!`);
      setBulkModalOpen(false);
      fetchData();
    } catch {
      toast.error('Failed to bulk generate slots.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <Link
            to="/operator/locations"
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center mb-1"
          >
            <FiArrowLeft className="mr-1" /> Back to Locations
          </Link>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">
            Manage Slots — {location?.name}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Total Inventory: {slots.length} slots
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Button variant="outline" size="sm" onClick={() => setBulkModalOpen(true)}>
            <FiLayers className="mr-1.5" /> Bulk Generate
          </Button>
          <Button variant="primary" size="sm" onClick={() => setSingleModalOpen(true)}>
            <FiPlus className="mr-1.5" /> Add Single Slot
          </Button>
        </div>
      </div>

      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {slots.map((s) => (
            <Card
              key={s.id}
              className={`p-3.5 border text-center transition-all ${
                s.status === 'BLOCKED'
                  ? 'bg-rose-50/50 border-rose-200'
                  : 'bg-white border-slate-200/80 hover:border-blue-400'
              }`}
            >
              <div className="font-mono text-xl font-black text-slate-800">{s.code}</div>
              <span className="text-[11px] font-semibold text-slate-500 block mt-0.5">
                {s.vehicle_type}
              </span>

              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between">
                <span
                  className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    s.status === 'ACTIVE'
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-rose-100 text-rose-800'
                  }`}
                >
                  {s.status}
                </span>

                <button
                  onClick={() => handleToggleBlock(s)}
                  className={`p-1 rounded text-xs transition-colors ${
                    s.status === 'ACTIVE'
                      ? 'text-slate-400 hover:text-rose-600'
                      : 'text-rose-600 hover:text-emerald-600'
                  }`}
                  title={s.status === 'ACTIVE' ? 'Block Slot' : 'Activate Slot'}
                >
                  {s.status === 'ACTIVE' ? <FiSlash /> : <FiCheck />}
                </button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Single Slot Modal */}
      {singleModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-bold text-slate-900 text-base mb-4">Add Single Slot</h3>
            <form onSubmit={handleCreateSingle} className="space-y-4 text-xs">
              <Input
                label="Slot Code"
                value={slotCode}
                onChange={(e) => setSlotCode(e.target.value)}
                placeholder="e.g. A05, EV-01"
                required
              />
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Vehicle Type
                </label>
                <select
                  value={vehicleType}
                  onChange={(e) => setVehicleType(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                >
                  {VEHICLE_TYPES.map((v) => (
                    <option key={v.value} value={v.value}>
                      {v.label}
                    </option>
                  ))}
                </select>
              </div>
              <div className="pt-3 flex justify-end space-x-2 border-t border-slate-100">
                <Button variant="outline" size="sm" onClick={() => setSingleModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Add Slot
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Bulk Slot Modal */}
      {bulkModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-sm w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-bold text-slate-900 text-base mb-4">Bulk Generate Slots</h3>
            <form onSubmit={handleCreateBulk} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Prefix"
                  value={prefix}
                  onChange={(e) => setPrefix(e.target.value)}
                  placeholder="e.g. B"
                  required
                />
                <Input
                  label="Quantity (1-50)"
                  type="number"
                  min={1}
                  max={50}
                  value={count}
                  onChange={(e) => setCount(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Vehicle Type
                </label>
                <select
                  value={bulkVehicle}
                  onChange={(e) => setBulkVehicle(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-300 rounded-lg"
                >
                  {VEHICLE_TYPES.map((v) => (
                    <option key={v.value} value={v.value}>
                      {v.label}
                    </option>
                  ))}
                </select>
              </div>
              <p className="text-[11px] text-slate-400">
                Will create slots {prefix}01 through {prefix}{count < 10 ? `0${count}` : count}.
              </p>
              <div className="pt-3 flex justify-end space-x-2 border-t border-slate-100">
                <Button variant="outline" size="sm" onClick={() => setBulkModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" size="sm">
                  Generate Slots
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
