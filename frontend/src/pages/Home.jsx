import { useState } from "react";
import SearchBar from "../components/SearchBar";
import "../styles/globalstyles.css";
import { search } from "../apiClient";

export default function Home() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await search(query.trim());
      setResults(data.results || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      {results.length === 0 ? (
        <div className="search-wrapper">
          <h1 className="search-title">RewindYou</h1>
          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
            loading={loading}
          />
          {error && <p className="error-text">{error}</p>}
          {loading && (
            <div className="spinner"></div>
          )}
        </div>
      ) : (
        <div className="result-wrapper">
          <button className="back-btn" onClick={() => setResults([])}>
            ← New search
          </button>

          <div className="query-bubble">{query}</div>

          <div className="sources-box">
            {results.map((item) => (
              <div key={item.page_id} className="source-row">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                >
                  {item.title || "Untitled"}
                </a>
                <span className="source-date">{item.created_at || ""}</span>
              </div>
            ))}
          </div>
          <div className="answer">
            {results.map((item) => (
              <p key={`${item.page_id}-summary`}>{item.summary}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
