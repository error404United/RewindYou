import SearchBar from "../components/SearchBar";
import "../styles/globalstyles.css";

export default function Home() {
  return (
    <div className="home-container">
      <div className="profile">
        <img
          src="https://cataas.com/cat?width=200&height=200"
          alt="User profile"
        />
      </div>

      <div className="search-wrapper">
        <h1>RewindYou</h1>
        <SearchBar />
      </div>
    </div>
  );
}
