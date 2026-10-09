import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Mail, Lock, User, AlertCircle, Loader2, CheckCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export default function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [validationError, setValidationError] = useState('');
  const { register, isLoading, error, clearError } = useAuthStore();
  const navigate = useNavigate();

  const passwordChecks = [
    { label: 'At least 8 characters', valid: password.length >= 8 },
    { label: 'Contains uppercase', valid: /[A-Z]/.test(password) },
    { label: 'Contains number', valid: /\d/.test(password) },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    setValidationError('');

    if (password !== confirmPassword) {
      setValidationError('Passwords do not match');
      return;
    }

    if (password.length < 8) {
      setValidationError('Password must be at least 8 characters');
      return;
    }

    try {
      await register(email, password, fullName);
      navigate('/dashboard');
    } catch {
      // Error handled by store
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/10 via-slate-950 to-cyan-500/10" />
        <div className="relative flex flex-col justify-center px-16">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-3 mb-8">
              <img src="/logo.svg" alt="BARAKA TRADING BOT" className="w-12 h-12" />
              <div>
                <h1 className="text-2xl font-bold text-white">BARAKA TRADING BOT</h1>
                <p className="text-xs text-slate-500 uppercase tracking-widest">Smarter Tools. Better Trading Decisions.</p>
              </div>
            </div>
            <h2 className="text-4xl font-bold text-white leading-tight">
              Start Your Trading<br />Journey
            </h2>
            <p className="mt-4 text-lg text-slate-400 max-w-md">
              Create an account and begin paper trading with AI-powered signals and professional risk management.
            </p>
            <div className="mt-8 space-y-3">
              {['Free paper trading with $10,000 virtual balance', 'AI-powered market analysis', 'Professional risk management tools'].map((item) => (
                <div key={item} className="flex items-center gap-3 text-sm text-slate-400">
                  <CheckCircle className="h-4 w-4 text-emerald-400" />
                  {item}
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md"
        >
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <img src="/logo.svg" alt="BARAKA TRADING BOT" className="w-10 h-10" />
            <span className="text-xl font-bold text-white">BARAKA TRADING BOT</span>
          </div>

          <h2 className="text-2xl font-bold text-white">Create account</h2>
          <p className="mt-1 text-sm text-slate-400">Start paper trading in minutes</p>

          {(error || validationError) && (
            <div className="mt-4 flex items-center gap-2 rounded-lg bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-400">
              <AlertCircle className="h-4 w-4 flex-shrink-0" />
              {error || validationError}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                  placeholder="John Doe"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                  placeholder="you@example.com"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                  placeholder="Create a password"
                  required
                />
              </div>
              {password && (
                <div className="mt-2 space-y-1">
                  {passwordChecks.map((check) => (
                    <div key={check.label} className="flex items-center gap-2 text-xs">
                      <CheckCircle className={`h-3 w-3 ${check.valid ? 'text-emerald-400' : 'text-slate-600'}`} />
                      <span className={check.valid ? 'text-emerald-400' : 'text-slate-500'}>{check.label}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-lg border border-slate-700 bg-slate-900/50 pl-10 pr-4 py-2.5 text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 transition-colors"
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-emerald-500 py-2.5 font-semibold text-white hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            Already have an account?{' '}
            <Link to="/login" className="text-emerald-400 hover:text-emerald-300 font-medium">
              Sign in
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
