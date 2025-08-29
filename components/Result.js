import React from 'react';

function Result({ data }) {
  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Result:</h3>
      {data.error ? (
        <p style={{ color: "red" }}>{data.error}</p>
      ) : (
        <p>Prediction: <b>{data.label}</b> (Confidence: {(data.score * 100).toFixed(2)}%)</p>
      )}
    </div>
  );
}

export default Result;
