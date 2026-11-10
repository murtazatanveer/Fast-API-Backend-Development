import { AuthAlert } from "../Components/AuthAlert";
import { AuthHeader } from "../Components/AuthHeader";
import { AuthLayout } from "../Components/AuthLayout";
import OtpInput from "./components/OtpInput";
import OtpResend from "./components/OtpResend";
import OtpTimer from "./components/OtpTimer";
import { useOtpFlow } from "./hooks/useOtpFlow";

const OtpPage = ({
  username,
  password,
  maskedEmail,
  onVerified,
  onAttemptsExhausted,
  onBackToLogin,
}) => {
  const {
    digits,
    displayEmail,
    remainingSeconds,
    remainingAttempts,
    verifying,
    resending,
    error,
    success,
    canResend,
    isExpired,
    handleDigitsChange,
    handleResend,
  } = useOtpFlow({
    username,
    password,
    maskedEmail,
    onVerified,
    onAttemptsExhausted,
  });

  return (
    <AuthLayout>
      <AuthHeader
        title="Verify your login"
        subtitle="Enter the six-digit code sent to your email address."
        icon={
          <svg
            className="h-8 w-8"
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
        }
      />

      <AuthAlert type="error" message={error} />
      <AuthAlert type="success" message={success} />

      <div className="space-y-5">
        <div className="rounded-2xl border border-blue-100 bg-blue-50/60 px-4 py-3 text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-500">
            Code sent to
          </p>
          <p className="mt-1 text-sm font-semibold text-gray-900">
            {displayEmail}
          </p>
        </div>

        <OtpInput
          value={digits}
          onChange={handleDigitsChange}
          disabled={isExpired || verifying}
        />

        <OtpTimer remainingSeconds={remainingSeconds} />

        <div className="flex items-center justify-between rounded-xl bg-gray-50 px-4 py-3 text-sm">
          <span className="font-medium text-gray-600">
            Remaining verification attempts
          </span>
          <span
            className={`font-bold ${
              remainingAttempts <= 1 ? "text-red-600" : "text-blue-600"
            }`}
          >
            {remainingAttempts}
          </span>
        </div>

        {verifying && (
          <p className="text-center text-sm font-medium text-blue-600">
            Verifying your code...
          </p>
        )}

        <OtpResend
          disabled={!canResend}
          loading={resending}
          onResend={handleResend}
        />

        <button
          type="button"
          onClick={onBackToLogin}
          className="w-full text-center text-sm font-semibold text-gray-500 transition-colors hover:text-gray-800"
        >
          Back to login
        </button>
      </div>
    </AuthLayout>
  );
};

export default OtpPage;
