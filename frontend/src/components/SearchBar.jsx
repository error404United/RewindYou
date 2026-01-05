import { ArrowRight } from "lucide-react";

export default function SearchBar() {
  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search your past learning..."
      />
      <button className="search-btn">
        <ArrowRight size={40} />
      </button>
    </div>
  );
}
