import { Routes, Route, Navigate } from "react-router-dom";
import Home from "./pages/Home";
import Auth from "./pages/Auth";
import TimelinePage from "./pages/TimelinePage";
import Layout from "./components/Layout";
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
      <Route element={<PrivateRoute element={<Layout />} />}>
        <Route path="/home" element={<Home />} />
        <Route path="/timeline" element={<TimelinePage />} />
      </Route>
    </Routes>
  );
}

export default App;
