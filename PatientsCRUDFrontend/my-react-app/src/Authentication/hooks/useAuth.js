// Authentication/hooks/useAuth.js
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authRequest } from "../utils/authApi";

export const useAuth = (type = "login") => {
  const [formData, setFormData] = useState(
    type === "login"
      ? { username: "", password: "" }
      : { username: "", email: "", password: "" },
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      // 1. Call the API based on the page type
      const data =
        type === "login"
          ? await authRequest("login", formData, "Login failed")
          : await authRequest("signup", formData, "Signup failed");

      // 3. Store the Access Token in LocalStorage

      localStorage.setItem("accessToken", data.data.accessToken);

      // 4. Redirect to the protected page after a short delay

      navigate("/dashboard");
    } catch (err) {
      // 5. Handle the displayUi flag
      if (err.displayUi) {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return { formData, loading, error, success, handleChange, handleSubmit };
};
