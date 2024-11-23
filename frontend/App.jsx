import React, { useState, useEffect } from "react";
import axios from "axios";
import "./App.css";

const App = () => {
  const [query, setQuery] = useState("");
  const [searchLevel, setSearchLevel] = useState("level1");
  const [advancedSearch, setAdvancedSearch] = useState(false);
  const [semanticSearchDone, setSemanticSearchDone] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedLyrics, setSelectedLyrics] = useState("");
  const [noResults, setNoResults] = useState(false);

  useEffect(() => {
    setSemanticSearchDone(false);
    if (!query) {
      setNoResults(false)
    }
  }, [query]);

  const handleSearch = async () => {
    setLoading(true);
    try {
      let endpoint = "";
      let params = {};
      let method = "GET"; // Default method for lexical/fuzzy searches

      if (advancedSearch) {
        if (!semanticSearchDone) {
          console.log("Performing Semantic Search");
          endpoint = "/semantic-search/";
          method = "GET"; // Semantic search requires POST
          params = { q: query };
        } else {
          console.log("Performing Vector Search");
          endpoint = "/vector-search/";
          method = "POST"; // Vector search requires POST

          // Generate vector for the query
          console.log("Generating vector for query:", query);
          const vectorResponse = await axios.post(
            "http://127.0.0.1:8000/generate-vector/",
            { q: query }
          );
          console.log("Vector Response:", vectorResponse.data);
          params = { vector: vectorResponse.data?.vector };
        }
      } else {
        console.log("Performing Lexical or Fuzzy Search");
        endpoint =
          searchLevel === "level1" ? "/lexical-search/" : "/fuzzy-search/";
        params = { q: query }; // Pass query as a URL parameter for GET
      }

      console.log(`Calling ${method} endpoint: ${endpoint} with params:`, params);

      let response;
      if (method === "GET") {
        response = await axios.get(`http://127.0.0.1:8000${endpoint}`, {
          params,
        });
      } else {
        response = await axios.post(`http://127.0.0.1:8000${endpoint}`, params);
      }

      console.log("Search Results:", response.data.results);
      const resultArr = response.data.results
      if(resultArr.length === 0) {
        setNoResults(true);
      };
      setResults(response.data.results || []);

      if (advancedSearch && !semanticSearchDone) {
        setSemanticSearchDone(true);
      } else {
        setSemanticSearchDone(false);
      }
    } catch (error) {
      console.error("Error fetching search results:", error);
    }
    setLoading(false);
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSearch();
    }
  };

  const toggleAdvancedSearch = () => {
    setAdvancedSearch(!advancedSearch);
    setSemanticSearchDone(false);
  };

  const handleSearchLevelChange = (level) => {
    setSearchLevel(level);
  };

  const openModal = (lyrics) => {
    setSelectedLyrics(lyrics);
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedLyrics("");
  };

  return (
    <div className="app">
      <div className="search-container">
        <h1>
          {advancedSearch
            ? "What kind of song lyrics do you want?"
            : "What part of the lyrics do you remember?"}
        </h1>
        <input
          type="text"
          placeholder={
            advancedSearch
              ? "E.g., songs about love and heartbreak"
              : "E.g., part of the lyrics you remember"
          }
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        {advancedSearch && semanticSearchDone && (
          <p>Switching to Vector Search. Refine your query for precise matches.</p>
        )}
        <button onClick={handleSearch}>
          {advancedSearch
            ? semanticSearchDone
              ? "Vector Search"
              : "Semantic Search"
            : "Search"}
        </button>
        {!advancedSearch && (
          <div className="radio-buttons">
            <label className="radio-label">
              <input
                type="radio"
                name="searchLevel"
                checked={searchLevel === "level1"}
                onChange={() => handleSearchLevelChange("level1")}
              />
              Level 1
            </label>
            <label className="radio-label">
              <input
                type="radio"
                name="searchLevel"
                checked={searchLevel === "level2"}
                onChange={() => handleSearchLevelChange("level2")}
              />
              Level 2
            </label>
          </div>
        )}
        <div className="advanced-toggle">
          <label className="toggle-container">
            <input
              type="checkbox"
              checked={advancedSearch}
              onChange={toggleAdvancedSearch}
            />
            <span className="slider"></span>
            <span className="toggle-text">Advanced Search</span>
          </label>
        </div>
        {loading && <div className="spinner"></div>}
        <div className="results">
          {query && ((results.length === 0)) && !loading && noResults ? 'No results found !' : results.map((result, index) => (
            <div key={index} className="result-tile">
              <h3>{result.title}</h3>
              <h4>{result.artist}</h4>
              <div className="lyrics-container">
                {Array.isArray(result.highlight?.lyrics) ? (
                  <div
                    dangerouslySetInnerHTML={{
                      __html: result.highlight.lyrics.join(" "),
                    }}
                  />
                ) : (
                  <p>{result.lyrics || "No lyrics available"}</p>
                )}
              </div>
              <button
                className="view-lyrics-btn"
                onClick={() => openModal(result.lyrics || "No lyrics available")}
              >
                View Full Lyrics
              </button>
            </div>
          ))}
        </div>
      </div>

      {modalOpen && (
        <div className="lyrics-modal" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>
              &times;
            </button>
            <h2>Full Lyrics</h2>
            <div className="lyrics-line-by-line">
              {selectedLyrics.split("\n").map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
