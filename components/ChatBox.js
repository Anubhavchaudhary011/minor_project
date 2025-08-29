import React, { useState } from 'react';

function ChatBox({ onSubmit }) {
  const [text, setText] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (text.trim()) {
      onSubmit(text);
      setText("");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type your thoughts..."
        style={{ padding: "10px", width: "300px" }}
      />
      <button type="submit" style={{ marginLeft: "10px" }}>Analyze</button>
    </form>
  );
}

export default ChatBox;
