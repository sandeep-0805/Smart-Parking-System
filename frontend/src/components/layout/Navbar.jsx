import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { FiMenu, FiX, FiUser, FiLogOut, FiCalendar, FiSearch, FiSliders, FiShield, FiBriefcase } from 'react-icons/fi';
import { Button } from '../common/Button';

export const Navbar = () => {
  const { user, isAuthenticated, isOperator, isAdmin, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [profileDropdown, setProfileDropdown] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white border-b border-slate-200/80 sticky top-0 z-40 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-xl shadow-xs">
                P
              </div>
              <span className="font-extrabold text-xl tracking-tight text-slate-900">
                Smart<span className="text-blue-600">Parking</span>
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:ml-8 md:flex md:space-x-4">
              <Link
                to="/search"
                className="inline-flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
              >
                <FiSearch className="mr-1.5" /> Find Parking
              </Link>
              {isAuthenticated && (
                <>
                  <Link
                    to="/bookings"
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
                  >
                    <FiCalendar className="mr-1.5" /> My Bookings
                  </Link>
                  <Link
                    to="/auto-booking"
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-slate-600 hover:text-blue-600 transition-colors"
                  >
                    <FiSliders className="mr-1.5" /> Auto-Booking
                  </Link>
                </>
              )}
              {isOperator && (
                <Link
                  to="/operator"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors"
                >
                  <FiBriefcase className="mr-1.5" /> Operator Portal
                </Link>
              )}
              {isAdmin && (
                <Link
                  to="/admin"
                  className="inline-flex items-center px-3 py-2 text-sm font-medium text-purple-600 hover:text-purple-700 transition-colors"
                >
                  <FiShield className="mr-1.5" /> Admin Panel
                </Link>
              )}
            </div>
          </div>

          {/* User Profile / Auth buttons */}
          <div className="hidden md:flex md:items-center md:space-x-3">
            {isAuthenticated ? (
              <div className="relative">
                <button
                  onClick={() => setProfileDropdown(!profileDropdown)}
                  className="flex items-center space-x-2 text-sm text-slate-700 hover:text-slate-900 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg focus:outline-none"
                >
                  <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs">
                    {user?.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="font-medium">{user?.full_name}</span>
                  <span className="text-[11px] bg-slate-200 text-slate-700 px-1.5 py-0.5 rounded font-mono">
                    {user?.role}
                  </span>
                </button>

                {profileDropdown && (
                  <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-lg shadow-lg py-1 bg-white ring-1 ring-black ring-opacity-5 divide-y divide-slate-100 z-50">
                    <div className="px-4 py-2 text-xs text-slate-500">
                      Signed in as <strong className="text-slate-800">{user?.email}</strong>
                    </div>
                    <div className="py-1">
                      <Link
                        to="/profile"
                        onClick={() => setProfileDropdown(false)}
                        className="flex items-center px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
                      >
                        <FiUser className="mr-2" /> My Profile
                      </Link>
                    </div>
                    <div className="py-1">
                      <button
                        onClick={handleLogout}
                        className="w-full text-left flex items-center px-4 py-2 text-sm text-rose-600 hover:bg-rose-50"
                      >
                        <FiLogOut className="mr-2" /> Sign Out
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link to="/login">
                  <Button variant="outline" size="sm">Log In</Button>
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm">Sign Up</Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger button */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-md text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-none"
            >
              {isOpen ? <FiX className="h-6 w-6" /> : <FiMenu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-2 pb-4 space-y-1">
          <Link
            to="/search"
            onClick={() => setIsOpen(false)}
            className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
          >
            Find Parking
          </Link>
          {isAuthenticated ? (
            <>
              <Link
                to="/bookings"
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
              >
                My Bookings
              </Link>
              <Link
                to="/auto-booking"
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
              >
                Auto-Booking Rules
              </Link>
              {isOperator && (
                <Link
                  to="/operator"
                  onClick={() => setIsOpen(false)}
                  className="block px-3 py-2 rounded-md text-base font-medium text-emerald-600 hover:bg-emerald-50"
                >
                  Operator Dashboard
                </Link>
              )}
              {isAdmin && (
                <Link
                  to="/admin"
                  onClick={() => setIsOpen(false)}
                  className="block px-3 py-2 rounded-md text-base font-medium text-purple-600 hover:bg-purple-50"
                >
                  Admin Panel
                </Link>
              )}
              <Link
                to="/profile"
                onClick={() => setIsOpen(false)}
                className="block px-3 py-2 rounded-md text-base font-medium text-slate-700 hover:bg-slate-100"
              >
                Profile & Preferences
              </Link>
              <button
                onClick={() => {
                  setIsOpen(false);
                  handleLogout();
                }}
                className="w-full text-left block px-3 py-2 rounded-md text-base font-medium text-rose-600 hover:bg-rose-50"
              >
                Sign Out
              </button>
            </>
          ) : (
            <div className="pt-2 flex flex-col space-y-2">
              <Link to="/login" onClick={() => setIsOpen(false)}>
                <Button variant="outline" className="w-full">Log In</Button>
              </Link>
              <Link to="/register" onClick={() => setIsOpen(false)}>
                <Button variant="primary" className="w-full">Sign Up</Button>
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
};
