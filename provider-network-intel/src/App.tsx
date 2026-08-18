import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { SelectedAreaProvider } from "./context/SelectedAreaContext";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import InteractiveMap from "./pages/InteractiveMap";
import AreaInsights from "./pages/AreaInsights";
import Recommendations from "./pages/Recommendations";
import WhatIfSimulator from "./pages/WhatIfSimulator";

export default function App() {
  return (
    <AuthProvider>
      <SelectedAreaProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />

            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/map"
              element={
                <ProtectedRoute>
                  <InteractiveMap />
                </ProtectedRoute>
              }
            />
            <Route
              path="/area-insights"
              element={
                <ProtectedRoute>
                  <AreaInsights />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute>
                  <Recommendations />
                </ProtectedRoute>
              }
            />
            <Route
              path="/what-if"
              element={
                <ProtectedRoute>
                  <WhatIfSimulator />
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </BrowserRouter>
      </SelectedAreaProvider>
    </AuthProvider>
  );
}
