import { useEffect, useMemo, useState, useSyncExternalStore } from "react";
import { refreshAccessToken } from "../Utils/apiClient";
import { AuthContext } from "../Utils/authContext";
import {
  clearAccessToken,
  getAccessToken,
  setAccessToken,
  subscribeToAccessToken,
} from "../Utils/authTokenStore";

export const AuthProvider = ({ children }) => {
  const accessToken = useSyncExternalStore(
    subscribeToAccessToken,
    getAccessToken,
    getAccessToken,
  );
  const [isInitializing, setIsInitializing] = useState(true);

  useEffect(() => {
    let isActive = true;

    const initializeAuth = async () => {
      try {
        await refreshAccessToken();
      } catch {
        clearAccessToken();
      } finally {
        if (isActive) {
          setIsInitializing(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isActive = false;
    };
  }, []);

  const value = useMemo(
    () => ({
      accessToken,
      isInitializing,
      setAccessToken,
      clearAccessToken,
    }),
    [accessToken, isInitializing],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
