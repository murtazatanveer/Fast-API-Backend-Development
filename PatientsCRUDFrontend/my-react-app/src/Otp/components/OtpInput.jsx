import { useEffect, useRef } from "react";
import { OTP_LENGTH } from "../utils/otpConfig";

const OtpInput = ({ value, onChange, disabled }) => {
  const inputRefs = useRef([]);

  useEffect(() => {
    if (!disabled) {
      inputRefs.current[0]?.focus();
    }
  }, [disabled]);

  const focusInput = (index) => {
    const input = inputRefs.current[index];

    if (input) {
      input.focus();
      input.select();
    }
  };

  const fillDigits = (startIndex, rawValue) => {
    const digits = rawValue.replace(/\D/g, "");

    if (!digits) return;

    const nextValue = [...value];
    let currentIndex = startIndex;

    for (const digit of digits) {
      if (currentIndex >= OTP_LENGTH) break;

      nextValue[currentIndex] = digit;
      currentIndex += 1;
    }

    onChange(nextValue);
    focusInput(Math.min(currentIndex, OTP_LENGTH - 1));
  };

  const handleChange = (index, event) => {
    const rawValue = event.target.value.replace(/\D/g, "");

    if (!rawValue) {
      const nextValue = [...value];
      nextValue[index] = "";
      onChange(nextValue);
      return;
    }

    if (rawValue.length > 1) {
      fillDigits(index, rawValue);
      return;
    }

    const nextValue = [...value];
    nextValue[index] = rawValue;
    onChange(nextValue);

    if (index < OTP_LENGTH - 1) {
      focusInput(index + 1);
    }
  };

  const handleKeyDown = (index, event) => {
    if (event.key === "Backspace") {
      event.preventDefault();

      const nextValue = [...value];

      if (nextValue[index]) {
        nextValue[index] = "";
        onChange(nextValue);
        return;
      }

      if (index > 0) {
        nextValue[index - 1] = "";
        onChange(nextValue);
        focusInput(index - 1);
      }

      return;
    }

    if (event.key === "ArrowLeft" && index > 0) {
      event.preventDefault();
      focusInput(index - 1);
    }

    if (event.key === "ArrowRight" && index < OTP_LENGTH - 1) {
      event.preventDefault();
      focusInput(index + 1);
    }
  };

  const handlePaste = (event) => {
    event.preventDefault();
    fillDigits(0, event.clipboardData.getData("text"));
  };

  return (
    <div
      className="flex items-center justify-center gap-2 sm:gap-3"
      onPaste={handlePaste}
    >
      {value.map((digit, index) => (
        <input
          key={index}
          ref={(element) => {
            inputRefs.current[index] = element;
          }}
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={1}
          value={digit}
          onChange={(event) => handleChange(index, event)}
          onKeyDown={(event) => handleKeyDown(index, event)}
          disabled={disabled}
          autoComplete={index === 0 ? "one-time-code" : "off"}
          aria-label={`OTP digit ${index + 1}`}
          className={`h-14 w-12 sm:h-16 sm:w-14 rounded-xl border text-center text-2xl font-bold outline-none transition-all duration-200 ${
            digit
              ? "border-blue-500 bg-white text-gray-900"
              : "border-gray-200 bg-gray-50 text-gray-900"
          } ${
            disabled
              ? "cursor-not-allowed opacity-60"
              : "focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30"
          }`}
        />
      ))}
    </div>
  );
};

export default OtpInput;
