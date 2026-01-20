import { useState } from "react";
import SearchBar from "../components/SearchBar";
import "../styles/globalstyles.css";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const handleSearch = () => {
    if (!query.trim()) return;

    const mockData = {
      question: query,
      answer:
        "Dynamic programming is a problem-solving technique where you break a big problem into smaller overlapping subproblems, solve each of them once, and store their results so you never recompute the same thing again. Instead of repeatedly recalculating answers like in naive recursion, you remember what you have already solved, which makes your solution much faster. The key idea is: if a problem can be built from the results of smaller versions of itself, and those smaller versions repeat, then dynamic programming helps you trade extra memory for huge gains in time.",
      sources: [
        {
          title: "geeksforgeeks.org",
          url: "https://www.geeksforgeeks.org/competitive-programming/dynamic-programming/",
          date: "Jan 4, 2026 · 10:38 AM",
        },
        {
          title: "w3schools.com",
          url: "https://www.w3schools.com/dsa/dsa_ref_dynamic_programming.php",
          date: "Dec 18, 2025 · 8:21 PM",
        },
      ],
    };

    setResult(mockData);
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
              </div>
            ))}
          </div>
          <p className="answer">{result.answer}</p>
        </div>
      )}
    </div>
  );
}
