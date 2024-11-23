import React from "react";

const ResultsList = ({ results }) => {
    console.log('RK', results);
  if (results.length === 0) return <div style={{marginTop: '40px'}}>No results found.</div>;

  const renderField = (field, highlight) => {
    if (highlight && highlight[field]) {
      // If highlight exists, render the highlighted snippet
      return <span dangerouslySetInnerHTML={{ __html: highlight[field][0] }} />;
    }
    return <span>{field}</span>;
  };

  if (results.length === 0) return <div style={{marginTop: '40px'}}>No results found.</div>;
  return (
    <div className="results-list">
      {results.map((result, index) => (
        <div key={index} className="result-item">
            <div dangerouslySetInnerHTML={{ __html: result.highlight.lyrics[0] }}></div>
          <h3>
            Title:{" "}
            {renderField(
              result.title,
              result.highlight ? result.highlight.title : null
            )}
          </h3>
          <p>
            Artist:{" "}
            {renderField(
              result.artist,
              result.highlight ? result.highlight.artist : null
            )}
          </p>
          <p>
            Lyrics:{" "}
            {renderField(
              result.lyrics,
              result.highlight ? result.highlight.lyrics : null
            )}
          </p>
        </div>
      ))}
    </div>
  );
};

export default ResultsList;
