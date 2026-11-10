import { formatOtpTime } from "../utils/otpConfig";

const OtpTimer = ({ remainingSeconds }) => {
  const isExpired = remainingSeconds <= 0;

  return (
    <div
      className={`flex items-center justify-center gap-2 rounded-xl border px-4 py-2.5 text-sm font-semibold ${
        isExpired
          ? "border-red-200 bg-red-50 text-red-600"
          : "border-blue-100 bg-blue-50 text-blue-700"
      }`}
    >
      <svg
        className="h-4 w-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      {isExpired
        ? "OTP expired. Please resend a new code."
        : `Expires in ${formatOtpTime(remainingSeconds)}`}
    </div>
  );
};

export default OtpTimer;
