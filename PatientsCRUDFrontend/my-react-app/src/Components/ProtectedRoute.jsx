import { Navigate, Outlet } from "react-router-dom";
import AuthLoadingScreen from "./AuthLoadingScreen";
import { useAuthContext } from "../Hooks/useAuthContext";

const ProtectedRoute = () => {
  const { accessToken, isInitializing } = useAuthContext();

  if (isInitializing) {
    return <AuthLoadingScreen />;
  }

  if (!accessToken) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};

export default ProtectedRoute;
