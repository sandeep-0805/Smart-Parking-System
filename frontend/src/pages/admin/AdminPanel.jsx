import React, { useState, useEffect } from 'react';
import {
  getAdminUsers,
  updateUserRole,
  updateUserStatus,
  getSystemConfig,
  updateSystemConfig,
  getAdminAuditLog,
  getAllLocationsAdmin,
} from '../../api/admin';
import { approveLocation } from '../../api/locations';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { formatDateTime } from '../../utils/formatters';
import toast from 'react-hot-toast';
import { FiUsers, FiMapPin, FiSliders, FiFileText, FiCheck, FiShield } from 'react-icons/fi';

export const AdminPanel = () => {
  const [tab, setTab] = useState('users'); // 'users', 'locations', 'config', 'audit'
  const [users, setUsers] = useState([]);
  const [locations, setLocations] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingConfig, setEditingConfig] = useState(null);
  const [configValueInput, setConfigValueInput] = useState('');
  const [savingConfig, setSavingConfig] = useState(false);

  const fetchTabData = async () => {
    setLoading(true);
    try {
      if (tab === 'users') {
        const data = await getAdminUsers();
        setUsers(data);
      } else if (tab === 'locations') {
        const data = await getAllLocationsAdmin();
        setLocations(data);
      } else if (tab === 'config') {
        const data = await getSystemConfig();
        setConfigs(data);
      } else if (tab === 'audit') {
        const data = await getAdminAuditLog();
        setAuditLogs(data);
      }
    } catch {
      toast.error('Failed to load admin data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTabData();
  }, [tab]);

  const handleRoleChange = async (userId, newRole) => {
    try {
      await updateUserRole(userId, newRole);
      toast.success('User role updated!');
      fetchTabData();
    } catch {
      toast.error('Failed to update role.');
    }
  };

  const handleStatusChange = async (userId, newStatus) => {
    try {
      await updateUserStatus(userId, newStatus);
      toast.success('User status updated!');
      fetchTabData();
    } catch {
      toast.error('Failed to update status.');
    }
  };

  const handleApproveLocation = async (locId) => {
    try {
      await approveLocation(locId);
      toast.success('Location approved!');
      fetchTabData();
    } catch {
      toast.error('Failed to approve location.');
    }
  };

  const handleEditConfig = (c) => {
    setEditingConfig(c);
    setConfigValueInput(
      typeof c.config_value === 'object'
        ? JSON.stringify(c.config_value, null, 2)
        : String(c.config_value)
    );
  };

  const handleSaveConfig = async () => {
    if (!editingConfig) return;
    setSavingConfig(true);
    try {
      let parsed;
      try {
        parsed = JSON.parse(configValueInput);
      } catch {
        parsed = configValueInput;
      }
      await updateSystemConfig(editingConfig.config_key, parsed);
      toast.success(`Config '${editingConfig.config_key}' updated successfully!`);
      setEditingConfig(null);
      fetchTabData();
    } catch {
      toast.error('Failed to update config.');
    } finally {
      setSavingConfig(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center">
            <FiShield className="mr-2 text-purple-600" /> Admin Console
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            User management, location approvals, audit trails, and system config
          </p>
        </div>

        {/* Tab switcher */}
        <div className="flex bg-slate-200/80 p-1 rounded-xl text-xs font-semibold self-start">
          <button
            onClick={() => setTab('users')}
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center ${
              tab === 'users' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiUsers className="mr-1.5" /> Users
          </button>
          <button
            onClick={() => setTab('locations')}
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center ${
              tab === 'locations' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiMapPin className="mr-1.5" /> Locations
          </button>
          <button
            onClick={() => setTab('config')}
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center ${
              tab === 'config' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiSliders className="mr-1.5" /> System Config
          </button>
          <button
            onClick={() => setTab('audit')}
            className={`px-3 py-1.5 rounded-lg transition-colors flex items-center ${
              tab === 'audit' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600'
            }`}
          >
            <FiFileText className="mr-1.5" /> Audit Log
          </button>
        </div>
      </div>

      {loading ? (
        <div className="py-20">
          <LoadingSpinner size="lg" />
        </div>
      ) : (
        <>
          {/* Tab 1: Users */}
          {tab === 'users' && (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-b border-slate-200 font-bold uppercase text-[10px] text-slate-400 tracking-wider">
                    <tr>
                      <th className="px-5 py-3">ID</th>
                      <th className="px-5 py-3">User</th>
                      <th className="px-5 py-3">Email</th>
                      <th className="px-5 py-3">Role</th>
                      <th className="px-5 py-3">Status</th>
                      <th className="px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {users.map((u) => (
                      <tr key={u.id} className="hover:bg-slate-50/50">
                        <td className="px-5 py-3 font-mono font-bold text-slate-500">#{u.id}</td>
                        <td className="px-5 py-3 font-semibold text-slate-900">{u.full_name}</td>
                        <td className="px-5 py-3">{u.email}</td>
                        <td className="px-5 py-3">
                          <select
                            value={u.role}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                            className="bg-slate-50 border border-slate-200 rounded px-2 py-1 text-xs font-semibold focus:outline-none"
                          >
                            <option value="DRIVER">DRIVER</option>
                            <option value="OPERATOR">OPERATOR</option>
                            <option value="ADMIN">ADMIN</option>
                          </select>
                        </td>
                        <td className="px-5 py-3">
                          <span
                            className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                              u.status === 'ACTIVE'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-rose-100 text-rose-800'
                            }`}
                          >
                            {u.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          <button
                            onClick={() =>
                              handleStatusChange(u.id, u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE')
                            }
                            className={`text-xs font-semibold px-2.5 py-1 rounded transition-colors ${
                              u.status === 'ACTIVE'
                                ? 'text-rose-600 hover:bg-rose-50'
                                : 'text-emerald-600 hover:bg-emerald-50'
                            }`}
                          >
                            {u.status === 'ACTIVE' ? 'Suspend' : 'Activate'}
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Tab 2: Locations Approval */}
          {tab === 'locations' && (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-b border-slate-200 font-bold uppercase text-[10px] text-slate-400 tracking-wider">
                    <tr>
                      <th className="px-5 py-3">ID</th>
                      <th className="px-5 py-3">Name</th>
                      <th className="px-5 py-3">Address</th>
                      <th className="px-5 py-3">Base Rate</th>
                      <th className="px-5 py-3">Status</th>
                      <th className="px-5 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {locations.map((loc) => (
                      <tr key={loc.id} className="hover:bg-slate-50/50">
                        <td className="px-5 py-3 font-mono font-bold text-slate-500">#{loc.id}</td>
                        <td className="px-5 py-3 font-bold text-slate-900">{loc.name}</td>
                        <td className="px-5 py-3 max-w-xs truncate">{loc.address}</td>
                        <td className="px-5 py-3">₹{loc.base_rate_paise / 100}/hr</td>
                        <td className="px-5 py-3">
                          <span
                            className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                              loc.status === 'APPROVED'
                                ? 'bg-emerald-100 text-emerald-800'
                                : 'bg-amber-100 text-amber-800'
                            }`}
                          >
                            {loc.status}
                          </span>
                        </td>
                        <td className="px-5 py-3">
                          {loc.status !== 'APPROVED' && (
                            <Button
                              size="sm"
                              variant="primary"
                              onClick={() => handleApproveLocation(loc.id)}
                            >
                              <FiCheck className="mr-1" /> Approve
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Tab 3: System Config */}
          {tab === 'config' && (
            <div className="space-y-4">
              {configs.map((c) => (
                <Card key={c.config_key} className="p-5">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="font-mono text-xs font-bold text-blue-600 block">
                        {c.config_key}
                      </span>
                      <p className="text-xs text-slate-500 mt-1">{c.description}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleEditConfig(c)}
                    >
                      Edit Config
                    </Button>
                  </div>
                  <div className="mt-3 bg-slate-50 p-3 rounded-lg font-mono text-xs text-slate-800 break-all">
                    {JSON.stringify(c.config_value, null, 2)}
                  </div>
                </Card>
              ))}

              {/* Edit Config Modal */}
              {editingConfig && (
                <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
                  <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-slate-200">
                    <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                      <div>
                        <span className="font-mono text-xs font-bold text-blue-600">
                          {editingConfig.config_key}
                        </span>
                        <h3 className="font-bold text-slate-900 text-base mt-0.5">
                          Edit System Setting
                        </h3>
                      </div>
                      <button
                        onClick={() => setEditingConfig(null)}
                        className="text-slate-400 hover:text-slate-600 text-lg font-bold"
                      >
                        &times;
                      </button>
                    </div>

                    <div className="py-4 space-y-3">
                      <p className="text-xs text-slate-500">{editingConfig.description}</p>
                      <label className="block text-xs font-semibold text-slate-700">
                        Configuration Value (JSON or Primitive)
                      </label>
                      <textarea
                        value={configValueInput}
                        onChange={(e) => setConfigValueInput(e.target.value)}
                        rows={6}
                        className="w-full font-mono text-xs p-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-blue-500"
                      />
                    </div>

                    <div className="flex justify-end space-x-3 pt-3 border-t border-slate-100">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingConfig(null)}
                        disabled={savingConfig}
                      >
                        Cancel
                      </Button>
                      <Button
                        variant="primary"
                        size="sm"
                        onClick={handleSaveConfig}
                        loading={savingConfig}
                      >
                        Save Configuration
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Tab 4: Audit Log */}
          {tab === 'audit' && (
            <Card className="overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-50 border-b border-slate-200 font-bold uppercase text-[10px] text-slate-400 tracking-wider">
                    <tr>
                      <th className="px-5 py-3">ID</th>
                      <th className="px-5 py-3">User ID</th>
                      <th className="px-5 py-3">Action</th>
                      <th className="px-5 py-3">Resource</th>
                      <th className="px-5 py-3">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {auditLogs.length > 0 ? (
                      auditLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-slate-50/50">
                          <td className="px-5 py-3 font-mono font-bold">#{log.id}</td>
                          <td className="px-5 py-3">User {log.user_id || 'System'}</td>
                          <td className="px-5 py-3 font-semibold text-slate-900">{log.action}</td>
                          <td className="px-5 py-3 font-mono text-[11px]">
                            {log.resource_type}:{log.resource_id}
                          </td>
                          <td className="px-5 py-3 text-slate-400">
                            {formatDateTime(log.created_at)}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="px-5 py-8 text-center text-slate-400">
                          No audit log entries found.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};
