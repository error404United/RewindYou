import { useState } from "react";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { login } from "../apiClient";

export default function LoginForm({ switchToSignup }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/home");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  return (
    <div className="auth-card">
      <h2>Welcome back!</h2>
      <p className="auth-sub">Login to your memory</p>

      <div className="input-group">
        <Mail size={18} />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <div className="input-group">
        <Lock size={18} />
        <input
          type={showPassword ? "text" : "password"}
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="eye-btn"
          onClick={() => setShowPassword(!showPassword)}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>

      {error && <p className="error-text">{error}</p>}

      <button className="primary-btn" onClick={handleLogin} disabled={loading}>
        {loading ? "Signing in..." : "Login"}
      </button>

      <p className="switch-text">
        Don't have an account?{" "}
        <span onClick={() => navigate("/signup")}>Sign up</span>
      </p>
    </div>
  );
}
