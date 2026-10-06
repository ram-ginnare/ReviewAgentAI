import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { CustomerPage } from './pages/CustomerPage'
import { LoginPage } from './pages/LoginPage'
import { AccountPage } from './pages/AccountPage'
import { OwnerDashboardPage } from './pages/OwnerDashboardPage'
import { getAuthToken, getStoredUser } from './lib/auth'
import { AdminBillingPage } from './pages/AdminBillingPage'
import { AdminDashboardPage } from './pages/AdminDashboardPage'
import { AdminBusinessFormPage } from './pages/AdminBusinessFormPage'

function ProtectedOwner() {
  const location = useLocation()
  return getAuthToken() ? <OwnerDashboardPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedAdmin() {
  const location = useLocation()
  const user = getStoredUser()
  return getAuthToken() && user?.role === 'ADMIN' ? <AdminDashboardPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedAdminForm() {
  const location = useLocation()
  const user = getStoredUser()
  return getAuthToken() && user?.role === 'ADMIN' ? <AdminBusinessFormPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedAdminBilling() {
  const location = useLocation()
  const user = getStoredUser()
  return getAuthToken() && user?.role === 'ADMIN' ? <AdminBillingPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

function ProtectedAccount() {
  const location = useLocation()
  return getAuthToken() ? <AccountPage /> : <Navigate to="/login" replace state={{ from: location.pathname }} />
}

export default function App() {
  return (
    <Routes>
      <Route path="/r/:slug" element={<CustomerPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/account" element={<ProtectedAccount />} />
      <Route path="/owner" element={<ProtectedOwner />} />
      <Route path="/admin" element={<ProtectedAdmin />} />
      <Route path="/admin/businesses/new" element={<ProtectedAdminForm />} />
      <Route path="/admin/businesses/:id" element={<ProtectedAdminForm />} />
      <Route path="/admin/billing" element={<ProtectedAdminBilling />} />
      <Route path="/" element={<Navigate to="/r/reviewagentai" replace />} />
      <Route path="*" element={<Navigate to="/r/reviewagentai" replace />} />
    </Routes>
  )
}
