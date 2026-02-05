import React, { useState } from 'react';
import { FiSend, FiDownload } from 'react-icons/fi'; // Install react-icons if needed

const ChatBox = ({ sessionId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  // --- 1. CHAT LOGIC ---
  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Send to your backend
      const response = await fetch("https://documentor-backend-8evm.onrender.com/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          question: userMessage.text,
          chat_history: messages // Send previous history for context
        }),
      });

      if (!response.ok) throw new Error("Failed to get answer");

      // Handle Streaming Response (Simplified for now, just text)
      // Note: If you implemented streaming in backend, you might need a reader here.
      // For this MVP, let's assume standard text response or handle stream basic way:
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let botText = "";
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        botText += chunk;
        // Live update the last message
        setMessages((prev) => {
           const lastMsg = prev[prev.length - 1];
           if (lastMsg.sender === 'model') {
             return [...prev.slice(0, -1), { sender: 'model', text: botText }];
           } else {
             return [...prev, { sender: 'model', text: botText }];
           }
        });
      }

    } catch (error) {
      console.error("Chat Error:", error);
      setMessages((prev) => [...prev, { sender: 'model', text: "Error: Could not reach the AI." }]);
    } finally {
      setIsLoading(false);
    }
  };

  // --- 2. DOWNLOAD SUMMARY LOGIC (Your New Code) ---
  const handleDownloadSummary = async () => {
    if (messages.length === 0) {
      alert("No conversation to summarize yet!");
      return;
    }

    setIsDownloading(true);

    try {
      const payload = {
        chat_history: messages.map(msg => ({
          sender: msg.sender === "user" ? "user" : "model",
          text: msg.text
        }))
      };

      const response = await fetch("https://documentor-backend-8evm.onrender.com/export/pdf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error("Failed to generate PDF");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `DocuMentor_Summary_${new Date().toISOString().slice(0,10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      console.log("PDF Downloaded successfully!");

    } catch (error) {
      console.error("Download Error:", error);
      alert("Failed to download summary. Please try again.");
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 w-full max-w-4xl mx-auto border-x border-gray-800">
      
      {/* --- HEADER WITH DOWNLOAD BUTTON --- */}
      <div className="bg-gray-800 p-4 shadow-md flex justify-between items-center">
        <div className="text-gray-300 text-sm">Session: <span className="font-mono text-purple-400">{sessionId.slice(0,8)}...</span></div>
        
        <button 
          onClick={handleDownloadSummary}
          disabled={messages.length === 0 || isDownloading}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all
            ${messages.length === 0 
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
              : 'bg-green-600 hover:bg-green-700 text-white shadow-lg shadow-green-900/20'}`}
        >
          {isDownloading ? (
            <span className="animate-pulse">Generating PDF...</span>
          ) : (
            <>
              <FiDownload /> Download Summary
            </>
          )}
        </button>
      </div>

      {/* --- MESSAGES AREA --- */}
      <div className="flex-grow overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <p>Ask a question about your document to get started!</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-2xl ${
              msg.sender === 'user' 
                ? 'bg-purple-600 text-white rounded-br-none' 
                : 'bg-gray-800 text-gray-200 rounded-bl-none border border-gray-700'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-800 text-gray-400 p-3 rounded-2xl rounded-bl-none border border-gray-700 text-sm animate-pulse">
              Thinking...
            </div>
          </div>
        )}
      </div>

      {/* --- INPUT AREA --- */}
      <div className="p-4 bg-gray-800 border-t border-gray-700">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask something about your doc..."
            className="flex-grow bg-gray-900 text-white border border-gray-600 rounded-lg px-4 py-2 focus:outline-none focus:border-purple-500 transition-colors"
          />
          <button 
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            className="bg-purple-600 hover:bg-purple-700 text-white p-3 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <FiSend size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;