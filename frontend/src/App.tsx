import { Routes, Route } from 'react-router-dom'
import { lazy, Suspense } from 'react'
import Layout from './components/Layout'
import LoadingSpinner from './components/ui/LoadingSpinner'

// Lazy load pages for optimal bundle splitting
const Landing = lazy(() => import('./pages/Landing'))
const Login = lazy(() => import('./pages/Login'))
const Register = lazy(() => import('./pages/Register'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Trading = lazy(() => import('./pages/Trading'))
const Signals = lazy(() => import('./pages/Signals'))
const Portfolio = lazy(() => import('./pages/Portfolio'))
const Positions = lazy(() => import('./pages/Positions'))
const Orders = lazy(() => import('./pages/Orders'))
const Trades = lazy(() => import('./pages/Trades'))
const Analytics = lazy(() => import('./pages/Analytics'))
const Backtesting = lazy(() => import('./pages/Backtesting'))
const Risk = lazy(() => import('./pages/Risk'))
const Models = lazy(() => import('./pages/Models'))
const Strategies = lazy(() => import('./pages/Strategies'))
const Scanner = lazy(() => import('./pages/Scanner'))
const Alerts = lazy(() => import('./pages/Alerts'))
const Exchange = lazy(() => import('./pages/Exchange'))
const SystemHealth = lazy(() => import('./pages/SystemHealth'))
const Journal = lazy(() => import('./pages/Journal'))
const Settings = lazy(() => import('./pages/Settings'))
const Users = lazy(() => import('./pages/Users'))
const AuditLogs = lazy(() => import('./pages/AuditLogs'))
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'))

function App() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-950 flex items-center justify-center">
          <LoadingSpinner size="lg" />
        </div>
      }
    >
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Main app routes with layout */}
        <Route element={<Layout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/trading" element={<Trading />} />
          <Route path="/signals" element={<Signals />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/positions" element={<Positions />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/trades" element={<Trades />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/backtesting" element={<Backtesting />} />
          <Route path="/risk" element={<Risk />} />
          <Route path="/models" element={<Models />} />
          <Route path="/strategies" element={<Strategies />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/exchange" element={<Exchange />} />
          <Route path="/system" element={<SystemHealth />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/users" element={<Users />} />
          <Route path="/audit" element={<AuditLogs />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Landing />} />
      </Routes>
    </Suspense>
  )
}

export default App
