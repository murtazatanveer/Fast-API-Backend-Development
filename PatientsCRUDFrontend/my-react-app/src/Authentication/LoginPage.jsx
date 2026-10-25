import { Link } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import { AuthLayout } from "./components/AuthLayout";
import { AuthHeader } from "./components/AuthHeader";
import { AuthAlert } from "./components/AuthAlert";
import { AuthInput } from "./components/AuthInput";
import { AuthButton } from "./components/AuthButton";

const LoginPage = () => {
  const { formData, loading, error, success, handleChange, handleSubmit } =
    useAuth("login");

  return (
    <AuthLayout>
      <AuthHeader
        title="Welcome Back"
        subtitle="Sign in to manage your patients."
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
              d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
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
          label="Password"
          type="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          placeholder="••••••••"
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
        <div className="flex justify-end mt-1.5">
          <a
            href="#"
            className="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors"
          >
            Forgot password?
          </a>
        </div>
        <AuthButton
          loading={loading}
          text="Sign In"
          loadingText="Signing in..."
        />
      </form>

      <p className="text-center text-sm text-gray-600 mt-8">
        Don't have an account?{" "}
        <Link
          to="/signup"
          className="font-semibold text-blue-600 hover:text-blue-800 transition-colors"
        >
          Create an account
        </Link>
      </p>
    </AuthLayout>
  );
};

export default LoginPage;
