import React, { useState } from "react";

const SearchBar = ({ onSearch }) => {
  const [query, setQuery] = useState("");
  const [searchType, setSearchType] = useState("lexical");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(query, searchType);
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter your search query..."
        />
        <select value={searchType} onChange={(e) => setSearchType(e.target.value)}>
          <option value="lexical">Lexical Search</option>
          <option value="fuzzy">Fuzzy Search</option>
          <option value="semantic">Semantic Search</option>
        </select>
        <button type="submit">Search</button>
      </form>
    </div>
  );
};

export default SearchBar;
