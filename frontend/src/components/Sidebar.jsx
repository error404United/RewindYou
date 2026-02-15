import {
  Search,
  Clock,
  RotateCcw,
  User,
  LibraryBig,
  House,
  LogOut,
} from "lucide-react";
import { useState, useEffect, useRef } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { getCurrentUser, logout } from "../apiClient";
import "../styles/sidebar.css";

export default function Sidebar() {
  const [user, setUser] = useState(null);
  const [isOpen, setIsOpen] = useState(false);
  const popupRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const data = await getCurrentUser();
        setUser(data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchUser();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupRef.current && !popupRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      navigate("/login");
    } catch (err) {
      console.error("Logout failed:", err);
    }
  };

  return (
    <div className="sidebar">
      <div className="sidebar-top">
        <div className="logo">
          <span>RewindYou</span>
        </div>

        <nav className="nav">
          <NavLink to="/home" className="nav-item">
            <House size={18} />
            <span>Home</span>
          </NavLink>

          <NavLink to="/timeline" className="nav-item">
            <LibraryBig size={18} />
            <span>Timeline</span>
          </NavLink>
        </nav>
      </div>

      <div className="sidebar-bottom">
        <div className="profile" onClick={() => setIsOpen((prev) => !prev)}>
          <div className="profile-avatar">
            <User size={18} className="user-icon"/>
          </div>
          <span className="profile-name">
            {user ? user.username : "Loading..."}
          </span>
        </div>
        {isOpen && user && (
          <div className="profile-popup" ref={popupRef}>
            <div className="popup-user-info">
              <div>
                <User size={20} />
              </div>
              <div>
                <div className="popup-name">{user.username}</div>
                <div className="popup-email">{user.email}</div>
              </div>
            </div>

            <div className="popup-divider"></div>

            <div className="popup-logout" onClick={handleLogout}>
              <LogOut size={16} className="logout-icon"/>
              <span>Logout</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
