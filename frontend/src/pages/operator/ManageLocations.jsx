import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getLocations, createLocation, updateLocation, deleteLocation } from '../../api/locations';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { formatCurrency } from '../../utils/formatters';
import { FACILITY_OPTIONS } from '../../utils/constants';
import toast from 'react-hot-toast';
import { FiPlus, FiEdit2, FiTrash2, FiMapPin, FiLayers } from 'react-icons/fi';

export const ManageLocations = () => {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // Form fields
  const [name, setName] = useState('');
  const [address, setAddress] = useState('');
  const [lat, setLat] = useState('17.4435');
  const [lng, setLng] = useState('78.3772');
  const [baseRate, setBaseRate] = useState('25');
  const [minRate, setMinRate] = useState('15');
  const [maxRate, setMaxRate] = useState('60');
  const [payAtVenue, setPayAtVenue] = useState(false);
  const [facilities, setFacilities] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      const data = await getLocations();
      setLocations(data);
    } catch {
      toast.error('Failed to load locations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, []);

  const openCreateModal = () => {
    setEditingId(null);
    setName('');
    setAddress('');
    setLat('17.4435');
    setLng('78.3772');
    setBaseRate('25');
    setMinRate('15');
    setMaxRate('60');
    setPayAtVenue(false);
    setFacilities([]);
    setModalOpen(true);
  };

  const openEditModal = (loc) => {
    setEditingId(loc.id);
    setName(loc.name);
    setAddress(loc.address);
    setLat(loc.lat.toString());
    setLng(loc.lng.toString());
    setBaseRate((loc.base_rate_paise / 100).toString());
    setMinRate((loc.min_rate_paise / 100).toString());
    setMaxRate((loc.max_rate_paise / 100).toString());
    setPayAtVenue(loc.pay_at_venue);
    setFacilities(loc.facilities || []);
    setModalOpen(true);
  };

  const handleFacilityToggle = (facId) => {
    setFacilities((prev) =>
      prev.includes(facId) ? prev.filter((f) => f !== facId) : [...prev, facId]
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    const payload = {
      name,
      address,
      lat: Number(lat),
      lng: Number(lng),
      base_rate_paise: Number(baseRate) * 100,
      min_rate_paise: Number(minRate) * 100,
      max_rate_paise: Number(maxRate) * 100,
      pay_at_venue: payAtVenue,
      facilities,
    };

    try {
      if (editingId) {
        await updateLocation(editingId, payload);
        toast.success('Location updated!');
      } else {
        await createLocation(payload);
        toast.success('Location created and submitted for approval!');
      }
      setModalOpen(false);
      fetchLocations();
    } catch (err) {
      toast.error('Failed to save location.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this parking location?')) return;
    try {
      await deleteLocation(id);
      toast.success('Location deleted.');
      fetchLocations();
    } catch {
      toast.error('Failed to delete location.');
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight">Manage Locations</h1>
          <p className="text-xs text-slate-500 mt-0.5">Define parking facilities, dynamic pricing boundaries, and hours</p>
        </div>
        <Button variant="primary" size="sm" onClick={openCreateModal}>
          <FiPlus className="mr-1.5" /> Add New Location
        </Button>
      </div>

      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {locations.map((loc) => (
            <Card key={loc.id} className="p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-start justify-between">
                  <h3 className="font-bold text-slate-900 text-base">{loc.name}</h3>
                  <span
                    className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      loc.status === 'APPROVED'
                        ? 'bg-emerald-50 text-emerald-700'
                        : 'bg-amber-50 text-amber-700'
                    }`}
                  >
                    {loc.status}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-1 flex items-center">
                  <FiMapPin className="mr-1 text-slate-400" /> {loc.address}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Base Rate</span>
                    <strong className="text-slate-800">{formatCurrency(loc.base_rate_paise)}/h</strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Min / Max</span>
                    <strong className="text-slate-800">
                      ₹{loc.min_rate_paise / 100} - ₹{loc.max_rate_paise / 100}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-bold">Total Slots</span>
                    <strong className="text-slate-800">{loc.total_slots}</strong>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between">
                <Link
                  to={`/operator/locations/${loc.id}/slots`}
                  className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-700"
                >
                  <FiLayers className="mr-1" /> Slots ({loc.total_slots})
                </Link>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => openEditModal(loc)}
                    className="p-1.5 text-slate-500 hover:text-blue-600 rounded"
                  >
                    <FiEdit2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(loc.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-600 rounded"
                  >
                    <FiTrash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="font-bold text-slate-900 text-lg mb-4">
              {editingId ? 'Edit Parking Location' : 'New Parking Location'}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <Input
                label="Location Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Hitech Cyber Towers Plaza"
                required
              />
              <Input
                label="Address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="Full street address..."
                required
              />
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Latitude"
                  type="number"
                  step="any"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  required
                />
                <Input
                  label="Longitude"
                  type="number"
                  step="any"
                  value={lng}
                  onChange={(e) => setLng(e.target.value)}
                  required
                />
              </div>

              <div className="grid grid-cols-3 gap-3">
                <Input
                  label="Base Rate (₹/h)"
                  type="number"
                  value={baseRate}
                  onChange={(e) => setBaseRate(e.target.value)}
                  required
                />
                <Input
                  label="Min Rate (₹/h)"
                  type="number"
                  value={minRate}
                  onChange={(e) => setMinRate(e.target.value)}
                  required
                />
                <Input
                  label="Max Rate (₹/h)"
                  type="number"
                  value={maxRate}
                  onChange={(e) => setMaxRate(e.target.value)}
                  required
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1.5">
                  Available Facilities
                </label>
                <div className="flex flex-wrap gap-2">
                  {FACILITY_OPTIONS.map((fac) => (
                    <label
                      key={fac.id}
                      className={`cursor-pointer inline-flex items-center text-xs px-2.5 py-1 rounded-md border ${
                        facilities.includes(fac.id)
                          ? 'bg-blue-50 text-blue-700 border-blue-300 font-bold'
                          : 'bg-slate-50 text-slate-600 border-slate-200'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={facilities.includes(fac.id)}
                        onChange={() => handleFacilityToggle(fac.id)}
                        className="hidden"
                      />
                      {fac.label}
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-2 pt-2">
                <input
                  type="checkbox"
                  id="pay_at_venue_check"
                  checked={payAtVenue}
                  onChange={(e) => setPayAtVenue(e.target.checked)}
                  className="rounded text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="pay_at_venue_check" className="text-xs font-semibold text-slate-700">
                  Allow Pay at Venue (FR-B8: confirms instantly without online payment)
                </label>
              </div>

              <div className="pt-4 flex justify-end space-x-3 border-t border-slate-100">
                <Button variant="outline" onClick={() => setModalOpen(false)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" loading={submitting}>
                  Save Location
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
