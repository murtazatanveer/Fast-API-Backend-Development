import { useState, useEffect, useRef } from "react";
import { fetchApi } from "../../Utils/apiClient";

const LogoutMenu = ({ onLogoutSuccess }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const menuRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = async (endpoint) => {
    setLoading(true);
    try {
      // true = include credentials (cookie) to delete the refresh token
      await fetchApi(endpoint, { method: "POST" }, true);
    } catch (error) {
      console.error("Logout failed", error);
    } finally {
      // Always clear local storage and redirect on success OR failure
      localStorage.removeItem("accessToken");
      if (onLogoutSuccess) onLogoutSuccess();
      window.location.href = "/login";
    }
  };

  return (
    <div className="relative" ref={menuRef}>
      {/* Trigger Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={loading}
        className="flex items-center gap-2 bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 px-5 py-2.5 rounded-xl font-semibold transition-all duration-200"
      >
        {loading ? "Logging out..." : "Logout"}
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-60 bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden z-50 animate-fade-in">
          <div className="py-1">
            {/* Option 1: Current Device */}
            <button
              onClick={() => handleLogout("/auth/logout")}
              className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-gray-50 flex items-center gap-3 transition-colors"
            >
              <svg
                className="w-4 h-4 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              Logout from this device
            </button>

            {/* Option 2: Other Devices */}
            <button
              onClick={() => handleLogout("/auth/logout-all")}
              className="w-full text-left px-4 py-3 text-sm text-gray-700 hover:bg-blue-50 flex items-center gap-3 transition-colors border-t border-gray-50"
            >
              <svg
                className="w-4 h-4 text-blue-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                />
              </svg>
              Logout from other devices
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default LogoutMenu;
