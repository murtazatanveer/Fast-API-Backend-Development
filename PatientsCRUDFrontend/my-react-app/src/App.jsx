import "./App.css";

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import SignupPage from "./Authentication/SignupPage";
import LoginPage from "./Authentication/LoginPage";
import DashboardPage from "./Dashboard/DashboardPage";
import ProtectedRoute from "./Components/ProtectedRoute";
import PublicRoute from "./Components/PublicRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        {/* Wrap Login and Signup in PublicRoute */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
        </Route>

        {/* Protected Routes Wrapper */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
