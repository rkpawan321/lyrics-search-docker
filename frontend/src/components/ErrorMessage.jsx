import React from "react";

const ErrorMessage = ({ error }) => {
  if (!error) return null;

  return <div className="error-message">Error: {error}</div>;
};

export default ErrorMessage;
