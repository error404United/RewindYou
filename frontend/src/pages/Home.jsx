import { useState, useEffect } from "react";
import SearchBar from "../components/SearchBar";
import "../styles/globalstyles.css";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pages, setPages] = useState([]);
  const [jwtToken, setJwtToken] = useState("");

  // Load JWT token from localStorage on component mount
  useEffect(() => {
    const token = localStorage.getItem("jwtToken");
    if (token) {
      setJwtToken(token);
      fetchPages(token);
    }
  }, []);

  // Fetch list of saved pages
  const fetchPages = async (token) => {
    if (!token) {
      console.warn("No JWT token found");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/pages`, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch pages: ${response.status}`);
      }

      const data = await response.json();
      setPages(data.pages || []);
    } catch (error) {
      console.error("Error fetching pages:", error);
    } finally {
      setLoading(false);
    }
  };

  // Perform semantic search
  const handleSearch = async () => {
    if (!query.trim() || !jwtToken) {
      alert("Please enter a search query and ensure you're logged in");
      return;
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/api/search?q=${encodeURIComponent(query)}`, {
        headers: {
          "Authorization": `Bearer ${jwtToken}`,
          "Content-Type": "application/json"
        }
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Format results for display
      const formattedResult = {
        question: query,
        answer: `Found ${data.count} results for your query`,
        sources: (data.results || []).map(result => ({
          title: result.title,
          url: result.url,
          date: new Date(result.createdAt).toLocaleString(),
          summary: result.summary
        }))
      };

      setResult(formattedResult);
    } catch (error) {
      console.error("Search error:", error);
      alert("Search failed: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <div className="profile">
        <img
          src="https://cataas.com/cat?width=60&height=60"
          alt="User profile"
        />
      </div>

      {!result ? (
        <div className="search-wrapper">
          <h1 className="search-title">RewindYou</h1>
          <SearchBar
            query={query}
            setQuery={setQuery}
            onSearch={handleSearch}
          />
          
          {/* Display saved pages if no search result */}
          {pages.length > 0 && !query && (
            <div className="saved-pages">
              <h3>Your Saved Pages</h3>
              <div className="pages-list">
                {pages.map(page => (
                  <div key={page.id} className="page-card">
                    <h4>{page.title}</h4>
                    <p className="summary">{page.summary}</p>
                    <div className="page-meta">
                      <span className="date">{new Date(page.createdAt).toLocaleDateString()}</span>
                      <a href={page.url} target="_blank" rel="noopener noreferrer" className="page-url">
                        Visit
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="result-wrapper">
          <button className="back-btn" onClick={() => setResult(null)}>
            ← New search
          </button>

          <div className="query-bubble">{result.question}</div>

          <div className="sources-box">
            {result.sources.map((src, idx) => (
              <div key={idx} className="source-row">
                <a
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="source-link"
                >
                  {src.title}
                </a>
                <span className="source-date">{src.date}</span>
                <p className="source-summary">{src.summary}</p>
              </div>
            ))}
          </div>
          <p className="answer">{result.answer}</p>
        </div>
      )}

      {loading && <div className="loading">Loading...</div>}
    </div>
  );
}
