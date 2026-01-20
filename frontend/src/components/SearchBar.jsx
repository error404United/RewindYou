import { ArrowRight } from "lucide-react";

export default function SearchBar({ query, setQuery, onSearch }) {
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      onSearch();
    }
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search your past learning..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button className="search-btn" onClick={onSearch}>
        <ArrowRight size={20} />
      </button>
    </div>
  );
}
