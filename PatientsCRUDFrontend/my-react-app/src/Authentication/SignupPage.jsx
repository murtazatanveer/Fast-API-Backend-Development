import { Link } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { AuthLayout } from "./components/AuthLayout";
import { AuthHeader } from "./components/AuthHeader";
import { AuthAlert } from "./components/AuthAlert";
import { AuthInput } from "./components/AuthInput";
import { AuthButton } from "./components/AuthButton";

const SignupPage = () => {
  const { formData, loading, error, success, handleChange, handleSubmit } =
    useAuth("signup");

  return (
    <AuthLayout>
      <AuthHeader
        title="Create an account"
        subtitle="Join us and start managing your patients effortlessly."
        icon={
          <svg
            className="w-8 h-8"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
            />
          </svg>
        }
      />

      <AuthAlert type="error" message={error} />
      <AuthAlert type="success" message={success} />

      <form onSubmit={handleSubmit} className="space-y-5">
        <AuthInput
          label="Username"
          name="username"
          value={formData.username}
          onChange={handleChange}
          placeholder="johndoe"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          }
        />
        <AuthInput
          label="Email Address"
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          placeholder="john@example.com"
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
          }
        />
        <AuthInput
          label="Password"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="••••••••"
          minLength={6}
          icon={
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          }
        />
        <AuthButton
          loading={loading}
          text="Create Account"
          loadingText="Creating account..."
        />
      </form>

      <p className="text-center text-sm text-gray-600 mt-8">
        Already have an account?{" "}
        <Link
          to="/login"
          className="font-semibold text-blue-600 hover:text-blue-800 transition-colors"
        >
          Sign in
        </Link>
      </p>
    </AuthLayout>
  );
};

export default SignupPage;
