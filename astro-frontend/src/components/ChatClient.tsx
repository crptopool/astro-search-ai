import { useState } from 'react';

export default function ChatClient() {
  const [messages, setMessages] = useState<{ role: 'user' | 'bot'; text: string }[]>([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    const newMessages = [...messages, { role: 'user', text: question }];
    setMessages(newMessages);
    setQuestion('');
    setLoading(true);

    try {
      const res = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question })
      });
      const data = await res.json();
      setMessages([...newMessages, { role: 'bot', text: data.answer }]);
    } catch (error) {
      setMessages([...newMessages, { role: 'bot', text: '⚠️ Error contacting the server.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <form onSubmit={handleAsk} className="chat-form">
        <input
          type="text"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>Ask</button>
      </form>

      <div id="chat-box">
        {messages.map((msg, index) => (
          <div key={index} className={msg.role}>{msg.text}</div>
        ))}
      </div>

      <style jsx>{`
        .chat-container {
          max-width: 800px;
          margin: 2rem auto;
          padding: 1rem;
          border: 1px solid #ccc;
        }
        .chat-form {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        input {
          flex: 1;
          padding: 0.5rem;
          font-size: 1rem;
        }
        button {
          padding: 0.5rem 1rem;
          font-size: 1rem;
        }
        .user {
          color: #0366d6;
          margin: 0.5rem 0;
        }
        .bot {
          color: #24292e;
          margin: 0.5rem 0;
        }
      `}</style>
    </div>
  );
}
