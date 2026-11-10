const OtpResend = ({ disabled, loading, onResend }) => (
  <div className="text-center">
    <p className="mb-3 text-xs text-gray-500">
      {disabled
        ? "You can request a new code when the timer ends."
        : "Didn't receive the code?"}
    </p>
    <button
      type="button"
      onClick={onResend}
      disabled={disabled || loading}
      className="inline-flex items-center justify-center gap-2 rounded-xl border border-blue-200 bg-white px-5 py-2.5 text-sm font-semibold text-blue-600 transition-colors hover:bg-blue-50 disabled:cursor-not-allowed disabled:opacity-50"
    >
      {loading && (
        <svg
          className="h-4 w-4 animate-spin"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {loading ? "Sending..." : "Resend OTP"}
    </button>
  </div>
);

export default OtpResend;
