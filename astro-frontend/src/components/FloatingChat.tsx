import React, { useState, useEffect } from 'react';

const FloatingChat = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('floatingChatHistory');
      return saved ? JSON.parse(saved) : [];
    }
    return [];
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  // Persist chat history in localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('floatingChatHistory', JSON.stringify(messages));
    }
  }, [messages]);

  // Optionally clear chat history when tab is closed
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const clearOnUnload = () => {
        localStorage.removeItem('floatingChatHistory');
      };
      window.addEventListener('beforeunload', clearOnUnload);
      return () => window.removeEventListener('beforeunload', clearOnUnload);
    }
  }, []);

  const toggleChat = () => setOpen(!open);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage.text })
      });

      const data = await res.json();
      // Compose bot message: summary + supporting verses (if any)
      let botText = data.answer || 'No answer returned.';
      if (Array.isArray(data.verses) && data.verses.length > 0) {
        botText += '\n\n'; // Add a blank line before the list
        botText += data.verses.map((v, idx) =>
          `${idx + 1}. [${v.surah}, Verse ${v.verse_number}]\n${v.content}`
        ).join('\n'); // Each item starts on a new line
      }
      setMessages((prev) => [...prev, { role: 'bot', text: botText }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'bot', text: '❌ Failed to fetch answer.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button
        className="chat-toggle"
        onClick={toggleChat}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 9999,
          background: '#0366d6',
          color: '#fff',
          borderRadius: '50%',
          width: '60px',
          height: '60px',
          border: 'none',
          fontSize: '24px',
          cursor: 'pointer',
        }}
      >
        💬
      </button>

      {open && (
        <div
          className="chat-box"
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            width: '300px',
            height: '400px',
            backgroundColor: '#fff',
            border: '1px solid #ccc',
            borderRadius: '8px',
            padding: '10px',
            overflowY: 'auto',
            zIndex: 9998,
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <div style={{ flexGrow: 1, overflowY: 'auto', marginBottom: '8px' }}>
            {messages.map((msg, idx) => (
              <div key={idx} style={{ margin: '4px 0', color: msg.role === 'user' ? '#0366d6' : '#24292e' }}>
                <strong>{msg.role === 'user' ? 'You' : 'Bot'}:</strong>{' '}
                {msg.text.split('\n').map((line, i) => (
                  <React.Fragment key={i}>
                    {line}
                    <br />
                  </React.Fragment>
                ))}
              </div>
            ))}
            {loading && <div><em>Typing...</em></div>}
          </div>

          <form onSubmit={handleAsk} style={{ display: 'flex' }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              style={{
                flexGrow: 1,
                padding: '6px',
                fontSize: '14px',
                borderRadius: '4px 0 0 4px',
                border: '1px solid #ccc',
              }}
            />
            <button
              type="submit"
              style={{
                padding: '6px 12px',
                fontSize: '14px',
                borderRadius: '0 4px 4px 0',
                border: '1px solid #ccc',
                backgroundColor: '#f0f0f0',
                cursor: 'pointer',
              }}
              disabled={loading}
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
};

export default FloatingChat;
