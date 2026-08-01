import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../utils/api";
import AdminAvatar from "../components/AdminAvatar";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (event) => {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      const response = await api.post("/auth/login", { username, password });
      sessionStorage.setItem("token", response.data.token);
      sessionStorage.setItem("visibleEmployeeCount", "20");
      navigate("/dashboard");
    } catch (requestError) {
      const status = requestError.response?.status;

      if (status === 401) {
        setError("Invalid username or password.");
      } else if (status === 429) {
        setError("Too many attempts. Please wait a minute.");
      } else if (!requestError.response) {
        setError(
          "The server is starting or temporarily unavailable. Please try again shortly."
        );
      } else {
        setError("Unable to sign in. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-[100dvh] flex items-center justify-center bg-gradient-to-r from-blue-500 to-blue-700 px-4 py-8">
      <form onSubmit={handleLogin} className="w-full max-w-sm rounded-2xl bg-white p-6 text-center shadow-2xl sm:p-8">
        <AdminAvatar large />
         <div className="mb-6">
        <h1 className="text-xl font-semibold mb-6">Insider Sentinel</h1>
        <p className="mt-1 text-sm font-medium text-gray-500">
            Administrator Portal
          </p>
         </div>
        <input placeholder="Username" className="w-full p-3 mb-4 border rounded-full" value={username} autoComplete="username" minLength="3" maxLength="50" required onChange={(event) => setUsername(event.target.value)} />
        <input type={showPassword ? "text" : "password"} placeholder="Password" className="w-full p-3 mb-2 border rounded-full" value={password} autoComplete="current-password" minLength="8" maxLength="128" required onChange={(event) => setPassword(event.target.value)} />
        <div className="flex items-center justify-center gap-2 text-sm mb-4">
          <input id="show-password" type="checkbox" checked={showPassword} onChange={() => setShowPassword(!showPassword)} />
          <label htmlFor="show-password">Show password</label>
        </div>
        {error && <p role="alert" className="mb-3 text-sm text-red-600">{error}</p>}
        <button type="submit" disabled={isSubmitting} className="w-full bg-black text-white py-3 rounded-full disabled:opacity-60">
          {isSubmitting ? "Signing in…" : "Login"}
        </button>
        <p className="mt-4 text-xs text-gray-400">
          Authorized administrators only
        </p>
      </form>
    </div>
  );
}
