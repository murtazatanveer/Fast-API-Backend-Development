import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { authRequest } from "../../Utils/authApi";

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
      if (type === "login") {
        return await authRequest("login", formData, "Login failed");
      }

      const data = await authRequest("signup", formData, "Signup failed");

      navigate("/login", {
        state: {
          successMessage: data?.message || "Account Created Successfully",
        },
      });

      return data;
    } catch (err) {
      if (err?.displayUi === true) {
        setError(err.message);
      } else {
        setError("Network error or Server Error. Please try again.");
      }

      return null;
    } finally {
      setLoading(false);
    }
  };

  return { formData, loading, error, success, handleChange, handleSubmit };
};
