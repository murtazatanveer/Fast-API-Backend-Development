import { useEffect, useRef, useState } from "react";
import { authRequest } from "../../Utils/authApi";
import {
  OTP_DURATION_SECONDS,
  OTP_INVALID_MESSAGE,
  OTP_MAX_ATTEMPTS,
  createEmptyOtpDigits,
} from "../utils/otpConfig";

export const useOtpFlow = ({
  username,
  password,
  maskedEmail,
  onVerified,
  onAttemptsExhausted,
}) => {
  const [digits, setDigits] = useState(createEmptyOtpDigits);
  const [remainingSeconds, setRemainingSeconds] = useState(
    OTP_DURATION_SECONDS,
  );
  const [remainingAttempts, setRemainingAttempts] = useState(OTP_MAX_ATTEMPTS);
  const [displayEmail, setDisplayEmail] = useState(maskedEmail);
  const [verifying, setVerifying] = useState(false);
  const [resending, setResending] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const submitInFlightRef = useRef(false);
  const lastSubmittedOtpRef = useRef("");
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;

    return () => {
      isMountedRef.current = false;
    };
  }, []);

  useEffect(() => {
    if (remainingSeconds <= 0) return undefined;

    const timer = setTimeout(() => {
      setRemainingSeconds((current) => Math.max(0, current - 1));
    }, 1000);

    return () => clearTimeout(timer);
  }, [remainingSeconds]);

  useEffect(() => {
    const otp = digits.join("");
    const isComplete = digits.every((digit) => digit !== "");

    if (
      !isComplete ||
      remainingSeconds <= 0 ||
      remainingAttempts <= 0 ||
      submitInFlightRef.current ||
      lastSubmittedOtpRef.current === otp
    ) {
      return;
    }

    submitInFlightRef.current = true;
    lastSubmittedOtpRef.current = otp;

    const verifyOtp = async () => {
      setVerifying(true);
      setError("");
      setSuccess("");

      try {
        const data = await authRequest(
          "verify-login",
          { username, otp },
          "OTP verification failed",
        );

        if (!isMountedRef.current) return;

        const accessToken = data?.data?.accessToken;

        if (!accessToken) {
          throw new Error("Invalid server response");
        }

        onVerified(accessToken);
      } catch (err) {
        if (!isMountedRef.current) return;

        setDigits(createEmptyOtpDigits());
        lastSubmittedOtpRef.current = "";

        if (err?.status === 401) {
          const nextAttempts = Math.max(0, remainingAttempts - 1);
          setRemainingAttempts(nextAttempts);

          if (nextAttempts === 0) {
            onAttemptsExhausted();
            return;
          }

          setError(err.message || OTP_INVALID_MESSAGE);
          return;
        }

        setError(
          err?.displayUi === true
            ? err.message
            : "Unable to verify OTP. Please try again.",
        );
      } finally {
        submitInFlightRef.current = false;

        if (isMountedRef.current) {
          setVerifying(false);
        }
      }
    };

    verifyOtp();
  }, [
    digits,
    onAttemptsExhausted,
    onVerified,
    remainingAttempts,
    remainingSeconds,
    username,
  ]);

  const handleDigitsChange = (nextDigits) => {
    setDigits(nextDigits);
    setError("");
    setSuccess("");
  };

  const handleResend = async () => {
    if (remainingSeconds > 0 || resending || verifying) return;

    setResending(true);
    setError("");
    setSuccess("");

    try {
      const data = await authRequest(
        "login",
        { username, password },
        "Resend OTP failed",
      );

      if (!isMountedRef.current) return;

      const nextEmail = data?.data?.email;

      if (nextEmail) {
        setDisplayEmail(nextEmail);
      }

      setDigits(createEmptyOtpDigits());
      lastSubmittedOtpRef.current = "";
      setRemainingAttempts(OTP_MAX_ATTEMPTS);
      setRemainingSeconds(OTP_DURATION_SECONDS);
      setSuccess(data?.message || "OTP Sent Successfully");
    } catch (err) {
      if (!isMountedRef.current) return;

      if (err?.status === 401) {
        onAttemptsExhausted();
        return;
      }

      setError(
        err?.displayUi === true
          ? err.message
          : "Unable to resend OTP. Please try again.",
      );
    } finally {
      if (isMountedRef.current) {
        setResending(false);
      }
    }
  };

  return {
    digits,
    displayEmail,
    remainingSeconds,
    remainingAttempts,
    verifying,
    resending,
    error,
    success,
    canResend: remainingSeconds <= 0 && !resending && !verifying,
    isExpired: remainingSeconds <= 0,
    handleDigitsChange,
    handleResend,
  };
};
