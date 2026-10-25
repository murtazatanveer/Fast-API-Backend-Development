// Authentication/components/AuthAlert.jsx
export const AuthAlert = ({ type, message }) => {
  if (!message) return null;
  const isError = type === "error";

  return (
    <div
      className={`mb-4 p-3 rounded-xl border text-sm flex items-center gap-2 animate-slide-down ${isError ? "bg-red-50 border-red-200 text-red-600" : "bg-green-50 border-green-200 text-green-600"}`}
    >
      <svg
        className="w-5 h-5 shrink-0"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        {isError ? (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        ) : (
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        )}
      </svg>
      {message}
    </div>
  );
};
