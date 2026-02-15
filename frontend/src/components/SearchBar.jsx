import { ArrowRight } from "lucide-react";

export default function SearchBar({ query, setQuery, onSearch, loading = false }) {
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
        disabled={loading}
      />
      <button className="search-btn" onClick={onSearch} disabled={loading}>
        {loading ? <ArrowRight size={28} color="#9ca3af"/> : <ArrowRight size={28} />}
      </button>
    </div>
  );
}
