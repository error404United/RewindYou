import { useState } from "react";
import { Eye, EyeOff, Mail, Lock, User, Check, X } from "lucide-react";
import { Navigate, useNavigate } from "react-router-dom";

export default function SignupForm({ switchToLogin }) {
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const passwordsMatch =
    confirmPassword.length > 0 && password === confirmPassword;

  const showError =
    confirmPassword.length >= password.length && password !== confirmPassword;

  const navigate = useNavigate();

  const handleSignup = () => {
    if (!passwordsMatch) return;
    navigate("/Home");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && passwordsMatch) {
      handleSignup();
    }
  };

  return (
    <div className="auth-card">
      <h2>Create account</h2>
      <p className="auth-sub">Start building your memory</p>

      <div className="input-group">
        <User size={18} />
        <input type="text" placeholder="Username" />
      </div>

      <div className="input-group">
        <Mail size={18} />
        <input type="email" placeholder="Email" />
      </div>

      <div className="input-group">
        <Lock size={18} />
        <input
          type={showPassword ? "text" : "password"}
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="eye-btn"
          onClick={() => setShowPassword(!showPassword)}
        >
          {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>

      <div className="input-group">
        <Lock size={18} />
        <input
          type={showConfirmPassword ? "text" : "password"}
          placeholder="Confirm password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          className="eye-btn"
          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
        >
          {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>

      {showError && <p className="error-text"><X size={14} className="cross-icon"/>Passwords do not match</p>}

      {passwordsMatch && (
        <p className="success-text">
          <Check size={14} className="check-icon"/> Passwords match
        </p>
      )}

      <button
        className="primary-btn"
        disabled={!passwordsMatch}
        onClick={handleSignup}
      >
        Sign up
      </button>

      <p className="switch-text">
        Already have an account?{" "}
        <span onClick={() => navigate("/login")}>Login</span>
      </p>
    </div>
  );
}
