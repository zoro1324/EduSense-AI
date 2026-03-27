import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ToastProvider } from './components/ui/ToastContext';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { AcademicPlannerPage } from './pages/AcademicPlannerPage';
import { LiveAttendancePage } from './pages/LiveAttendancePage';
import { AttendanceRecordsPage } from './pages/AttendanceRecordsPage';
import { EngagementMonitorPage } from './pages/EngagementMonitorPage';
import { SafetyMonitorPage } from './pages/SafetyMonitorPage';
import { StudentRegistryPage } from './pages/StudentRegistryPage';
import { StudentProfilePage } from './pages/StudentProfilePage';
import { DataUploadPage } from './pages/DataUploadPage';
import { LeaveManagementPage } from './pages/LeaveManagementPage';
import { MarksResultsPage } from './pages/MarksResultsPage';
import { NotificationsPage } from './pages/NotificationsPage';
import { ReportsPage } from './pages/ReportsPage';
import { SettingsPage } from './pages/SettingsPage';
import { NotFoundPage } from './pages/NotFoundPage';

function App() {
  return (
    <Router>
      <AuthProvider>
        <ToastProvider>
          <Routes>
            <Route path="/" element={<LoginPage />} />
            <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
            <Route path="/academic" element={<ProtectedRoute><AcademicPlannerPage /></ProtectedRoute>} />
            <Route path="/attendance/live" element={<ProtectedRoute><LiveAttendancePage /></ProtectedRoute>} />
            <Route path="/attendance/records" element={<ProtectedRoute><AttendanceRecordsPage /></ProtectedRoute>} />
            <Route path="/engagement" element={<ProtectedRoute><EngagementMonitorPage /></ProtectedRoute>} />
            <Route path="/safety" element={<ProtectedRoute><SafetyMonitorPage /></ProtectedRoute>} />
            <Route path="/students" element={<ProtectedRoute><StudentRegistryPage /></ProtectedRoute>} />
            <Route path="/students/:id" element={<ProtectedRoute><StudentProfilePage /></ProtectedRoute>} />
            <Route path="/upload" element={<ProtectedRoute><DataUploadPage /></ProtectedRoute>} />
            <Route path="/leave" element={<ProtectedRoute><LeaveManagementPage /></ProtectedRoute>} />
            <Route path="/marks" element={<ProtectedRoute><MarksResultsPage /></ProtectedRoute>} />
            <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
            <Route path="/reports" element={<ProtectedRoute><ReportsPage /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute adminOnly><SettingsPage /></ProtectedRoute>} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </ToastProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
