import LoginForm from "../components/LoginForm";
import SignupForm from "../components/SignupForm";
import "../styles/auth.css";

export default function Auth({ mode }) {
  return (
    <div className="auth-container">
      {mode === "login" ? <LoginForm /> : <SignupForm />}
    </div>
  );
}
