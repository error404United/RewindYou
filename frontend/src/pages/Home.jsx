import { useState } from "react";
import SearchBar from "../components/SearchBar";
import "../styles/globalstyles.css";
import { Globe, TvMinimalPlay, FileText, ArrowLeft } from "lucide-react";
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

  const parseUTCDate = (timestamp) => {
    if (!timestamp) return null;
    return new Date(timestamp.includes("+") ? timestamp : timestamp + "Z");
  };

  const getIcon = (url) => {
    if (!url) return <Globe size={18} />;

    if (url.includes("youtube.com") || url.includes("youtu.be"))
      return <TvMinimalPlay size={18} />;

    if (url.endsWith(".pdf")) return <FileText size={18} />;

    return <Globe size={18} />;
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
          {loading && <div className="spinner"></div>}
        </div>
      ) : (
        <div className="result-wrapper">
          <div className="chat-feed">
            <div className="chat-row query-row">
              <button className="back-btn" onClick={() => setResults([])}>
                <ArrowLeft size={18} />  New search
              </button>
              <div className="query-bubble">{query}</div>
            </div>
            {results.map((item) => (
              <div key={item.page_id} className="chat-row results-row">
                <div className="result-bubble">
                  <div className="bubble-header">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="source-link"
                      >
                      {getIcon(item.url)} {item.title || "Untitled"}
                    </a>
                    {item.created_at && (
                      <span className="source-date">
                        {parseUTCDate(item.created_at).toLocaleDateString(
                          "en-IN",
                          {
                            timeZone: "Asia/Kolkata",
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          },
                        )}{" "}
                        •{" "}
                        {parseUTCDate(item.created_at)
                          .toLocaleTimeString("en-IN", {
                            timeZone: "Asia/Kolkata",
                            hour: "2-digit",
                            minute: "2-digit",
                            hour12: true,
                          })
                          .toLowerCase()}
                      </span>
                    )}
                  </div>
                  <p className="bubble-content">{item.summary}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
