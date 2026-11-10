export const OTP_LENGTH = 6;
export const OTP_DURATION_SECONDS = 110;
export const OTP_MAX_ATTEMPTS = 3;
export const OTP_INVALID_MESSAGE = "Invalid or expired OTP";

export const createEmptyOtpDigits = () => Array(OTP_LENGTH).fill("");

export const formatOtpTime = (seconds) => {
  const safeSeconds = Math.max(0, seconds);
  const minutes = Math.floor(safeSeconds / 60);
  const remainingSeconds = safeSeconds % 60;

  return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
};
