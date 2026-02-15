import { Search, Clock, RotateCcw, User, LibraryBig, House } from "lucide-react";
import { NavLink } from "react-router-dom";
import "../styles/sidebar.css";

export default function Sidebar() {
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
        <div className="profile">
          <div className="profile-avatar">
            <User size={18} />
          </div>
          <span className="profile-name">Jeslia Rose</span>
        </div>
      </div>
    </div>
  );
}
