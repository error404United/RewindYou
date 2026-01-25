import { useState } from "react";
import { Eye, EyeOff, User, Lock } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function LoginForm({ switchToSignup }) {
  const [showPassword, setShowPassword] = useState(false);
  const navigate = useNavigate();

  const handleLogin = () => {
    // later: call backend
    navigate("/home");
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
        <User size={18} />
        <input type="text" placeholder="Username" />
      </div>

      <div className="input-group">
        <Lock size={18} />
        <input
          type={showPassword ? "text" : "password"}
          placeholder="Password"
          onKeyDown={handleKeyDown}
        />
        <button
          className="eye-btn"
          onClick={() => setShowPassword(!showPassword)}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>

      <button className="primary-btn" onClick={handleLogin}>
        Login
      </button>

      <p className="switch-text">
        Don't have an account?{" "}
        <span onClick={() => navigate("/signup")}>Sign up</span>
      </p>
    </div>
  );
}
