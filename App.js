import React, { useState } from 'react';
import ChatBox from './components/ChatBox';
import Result from './components/Result';

function App() {
  const [result, setResult] = useState(null);

  const analyzeText = async (text) => {
    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h2>Mental Health Sentiment Analyzer</h2>
      <ChatBox onSubmit={analyzeText} />
      {result && <Result data={result} />}
    </div>
  );
}

export default App;
