import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/layout/ProtectedRoute';

// Public Pages
import { Home } from './pages/Home';
import { Search } from './pages/Search';
import { Login } from './pages/Login';
import { Register } from './pages/Register';

// Protected User Pages
import { MyBookings } from './pages/MyBookings';
import { BookingDetails } from './pages/BookingDetails';
import { Profile } from './pages/Profile';
import { AutoBooking } from './pages/AutoBooking';

// Operator Pages
import { OperatorDashboard } from './pages/operator/OperatorDashboard';
import { ManageLocations } from './pages/operator/ManageLocations';
import { ManageSlots } from './pages/operator/ManageSlots';
import { OperatorBookings } from './pages/operator/OperatorBookings';

// Admin Pages
import { AdminPanel } from './pages/admin/AdminPanel';

export const App = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        {/* Public Routes */}
        <Route index element={<Home />} />
        <Route path="search" element={<Search />} />
        <Route path="login" element={<Login />} />
        <Route path="register" element={<Register />} />

        {/* Protected Driver Routes */}
        <Route
          path="bookings"
          element={
            <ProtectedRoute>
              <MyBookings />
            </ProtectedRoute>
          }
        />
        <Route
          path="bookings/:id"
          element={
            <ProtectedRoute>
              <BookingDetails />
            </ProtectedRoute>
          }
        />
        <Route
          path="profile"
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          }
        />
        <Route
          path="auto-booking"
          element={
            <ProtectedRoute allowedRoles={['DRIVER', 'ADMIN']}>
              <AutoBooking />
            </ProtectedRoute>
          }
        />

        {/* Operator Portal Routes */}
        <Route
          path="operator"
          element={
            <ProtectedRoute allowedRoles={['OPERATOR', 'ADMIN']}>
              <OperatorDashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="operator/locations"
          element={
            <ProtectedRoute allowedRoles={['OPERATOR', 'ADMIN']}>
              <ManageLocations />
            </ProtectedRoute>
          }
        />
        <Route
          path="operator/locations/:id/slots"
          element={
            <ProtectedRoute allowedRoles={['OPERATOR', 'ADMIN']}>
              <ManageSlots />
            </ProtectedRoute>
          }
        />
        <Route
          path="operator/bookings"
          element={
            <ProtectedRoute allowedRoles={['OPERATOR', 'ADMIN']}>
              <OperatorBookings />
            </ProtectedRoute>
          }
        />

        {/* Admin Console Route */}
        <Route
          path="admin"
          element={
            <ProtectedRoute allowedRoles={['ADMIN']}>
              <AdminPanel />
            </ProtectedRoute>
          }
        />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default App;
