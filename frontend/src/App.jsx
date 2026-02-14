import { Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import TimelinePage from "./pages/TimelinePage";
import { getStoredTokens } from "./apiClient";

function App() {
  const PrivateRoute = ({ element }) => {
    const tokens = getStoredTokens();
    if (!tokens?.accessToken) {
      return <Navigate to="/login" replace />;
    }
    return element;
  };

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" />} />
      <Route path="/login" element={<Auth mode="login" />} />
      <Route path="/signup" element={<Auth mode="signup" />} />
      <Route path="/home" element={<PrivateRoute element={<Home />} />} />
      <Route path="/timeline" element={<PrivateRoute element={<TimelinePage />}/>} />
    </Routes>
  );
}

export default App;
