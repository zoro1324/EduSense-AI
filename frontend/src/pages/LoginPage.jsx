import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button, Input } from '../components/ui/UIPrimitives';

export const LoginPage = () => {
  const navigate = useNavigate();
  const { login, authLoading } = useAuth();
  const [email, setEmail] = useState('admin@edusense.ai');
  const [password, setPassword] = useState('demo123');
  const [show, setShow] = useState(false);
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    const result = await login(email, password);
    if (result.ok) {
      navigate('/dashboard');
      return;
    }
    setError(result.error || 'Invalid credentials.');
  };

  return (
    <div className="min-h-screen bg-bg grid-pattern flex items-center justify-center px-4">
      <div className="w-full max-w-md bg-card/95 border border-border rounded-2xl shadow-hover p-6">
        <div className="text-center mb-6">
          <div className="text-4xl mb-2">🧠👁️</div>
          <h1 className="text-2xl font-semibold text-text">EduSense AI</h1>
          <p className="text-muted text-sm">AI Driven School Management</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="text-sm text-muted">Email</label>
            <Input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="admin@edusense.ai" type="email" />
          </div>
          <div>
            <label className="text-sm text-muted">Password</label>
            <div className="relative">
              <Input value={password} onChange={(e) => setPassword(e.target.value)} type={show ? 'text' : 'password'} placeholder="••••••••" className="pr-16" />
              <button type="button" onClick={() => setShow((v) => !v)} className="absolute right-3 top-2 text-xs text-muted hover:text-text">
                {show ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          <Button type="submit" className="w-full" loading={authLoading}>Login</Button>
          <div className="text-right text-xs text-indigo-300 hover:text-indigo-200 cursor-pointer">Forgot password?</div>
          {error ? <p className="text-sm text-danger">{error}</p> : null}
        </form>
      </div>
    </div>
  );
};
