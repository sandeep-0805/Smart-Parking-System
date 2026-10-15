import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/common/Card';
import { Input } from '../components/common/Input';
import { Button } from '../components/common/Button';

export const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/search';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login({ email, password });
      navigate(from, { replace: true });
    } catch {
      // Error handled by AuthContext toast
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center px-4 py-12">
      <Card className="max-w-md w-full p-8 shadow-xl">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-black text-slate-900 tracking-tight">Sign In to SmartParking</h2>
          <p className="text-xs text-slate-500 mt-1">Access your bookings and AI parking assistant</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="driver@test.com"
            required
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="••••••••"
            required
          />

          <Button type="submit" variant="primary" loading={loading} className="w-full mt-2">
            Sign In
          </Button>
        </form>

        {/* Demo Credentials Helper */}
        <div className="mt-6 pt-5 border-t border-slate-100 text-xs text-slate-500">
          <p className="font-semibold text-slate-700 mb-1">Demo Credentials:</p>
          <div className="grid grid-cols-3 gap-1 font-mono text-[11px] bg-slate-50 p-2 rounded-lg">
            <button
              type="button"
              onClick={() => {
                setEmail('driver@test.com');
                setPassword('Test@1234');
              }}
              className="text-left hover:text-blue-600 font-semibold"
            >
              • Driver
            </button>
            <button
              type="button"
              onClick={() => {
                setEmail('operator@test.com');
                setPassword('Test@1234');
              }}
              className="text-left hover:text-blue-600 font-semibold"
            >
              • Operator
            </button>
            <button
              type="button"
              onClick={() => {
                setEmail('admin@test.com');
                setPassword('Test@1234');
              }}
              className="text-left hover:text-blue-600 font-semibold"
            >
              • Admin
            </button>
          </div>
        </div>

        <div className="mt-4 text-center text-xs text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-700">
            Sign up
          </Link>
        </div>
      </Card>
    </div>
  );
};
