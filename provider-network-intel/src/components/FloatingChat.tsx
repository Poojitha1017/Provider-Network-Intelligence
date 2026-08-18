import { useState, useRef, useEffect } from "react";
import { MessageSquare, X, Minus, Send, Bot, User, Sparkles, RefreshCw, ChevronRight } from "lucide-react";
import { sendChatQuery } from "../services/api";
import chatbotIcon from "../assets/chatbot.png";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  timestamp: string;
  suggestedActions?: string[];
}

const INITIAL_MESSAGES: Message[] = [
  {
    id: "welcome",
    role: "assistant",
    text: "Hello! I am your **Healthcare Intelligence Assistant**.\n\nI can analyze your network's **8,752 providers**, **3,052 decision scenarios**, shortage areas, and compute What-If simulations.\n\nHow can I help you today?",
    timestamp: "Just now",
    suggestedActions: [
      "Which areas have critical provider shortages?",
      "Simulate adding 2 cardiologists",
      "Show top recruitment recommendations",
    ],
  },
];

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const clearChat = () => {
    setMessages(INITIAL_MESSAGES);
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen, isMinimized]);


  const handleSend = async (queryText?: string) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.text }));
      const response = await sendChatQuery(textToSend, history);

      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        text: response.answer,
        timestamp: response.timestamp || new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        suggestedActions: response.suggested_actions,
      };

      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        text: `⚠️ **Connection Error**: ${err.message || "Failed to reach backend query engine. Please check connection."}`,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSummarize = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/chat/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const data = await res.json();
      const botMsg: Message = {
        id: Date.now().toString(),
        role: "assistant",
        text: data.summary || "Executive summary generated successfully.",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        suggestedActions: ["Simulate 2 Providers in Harrisville", "Open Network Map", "Export Report"],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "assistant",
          text: "⚠️ Failed to generate AI Executive Summary. Please ensure backend is running.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* 1. Chat Window */}
      {isOpen && (
        <div
          className={`mb-3 flex w-[380px] sm:w-[420px] flex-col rounded-2xl border border-slate-700/50 bg-slate-900 shadow-2xl transition-all duration-200 overflow-hidden ${
            isMinimized ? "h-14" : "h-[540px] max-h-[82vh]"
          }`}
          style={{ backdropFilter: "blur(12px)" }}
        >
          {/* Header */}
          <div className="flex h-14 shrink-0 items-center justify-between border-b border-slate-800 bg-gradient-to-r from-navy-900 to-navy-950 px-4">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-md overflow-hidden p-0.5">
                <img src={chatbotIcon} className="h-full w-full object-contain" alt="Assistant" />
              </div>
              <div>
                <h3 className="text-sm font-bold leading-tight text-white flex items-center gap-1.5">
                  Healthcare AI Assistant
                  <span className="flex h-2 w-2 rounded-full bg-emerald-400"></span>
                </h3>
                <p className="text-[11px] leading-tight text-slate-400">Healthcare Assistant</p>
              </div>
            </div>

            <div className="flex items-center gap-1">
              <button
                onClick={handleSummarize}
                title="Generate AI Executive Summary"
                className="rounded-md px-2 py-1 bg-brand-600/30 text-brand-300 hover:bg-brand-600 hover:text-white text-[11px] font-semibold border border-brand-500/40 flex items-center gap-1 transition-all"
              >
                <Sparkles className="h-3 w-3" />
                <span>Summarize</span>
              </button>
              <button
                onClick={clearChat}
                title="Clear conversation"
                className="rounded-md p-1.5 text-slate-400 hover:bg-navy-800 hover:text-slate-200"
              >
                <RefreshCw className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={() => setIsMinimized((v) => !v)}
                title={isMinimized ? "Expand" : "Minimize"}
                className="rounded-md p-1.5 text-slate-400 hover:bg-navy-800 hover:text-slate-200"
              >
                <Minus className="h-4 w-4" />
              </button>
              <button
                onClick={() => setIsOpen(false)}
                title="Close chat"
                className="rounded-md p-1.5 text-slate-400 hover:bg-navy-800 hover:text-rose-400"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Body */}
          {!isMinimized && (
            <>
              <div className="flex-1 overflow-y-auto p-4 space-y-3.5 bg-slate-900/90 text-sm">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-2.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    {msg.role === "assistant" && (
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white border border-slate-700/60 overflow-hidden p-0.5">
                        <img src={chatbotIcon} className="h-full w-full object-contain" alt="Assistant" />
                      </div>
                    )}

                    <div className={`max-w-[82%] space-y-1.5 ${msg.role === "user" ? "items-end" : "items-start"}`}>
                      <div
                        className={`rounded-2xl px-3.5 py-2.5 shadow-sm text-xs sm:text-sm leading-relaxed ${
                          msg.role === "user"
                            ? "bg-brand-600 text-white rounded-tr-none font-medium"
                            : "bg-navy-800/90 text-slate-200 border border-slate-700/60 rounded-tl-none"
                        }`}
                      >
                        <div className="whitespace-pre-line">
                          {msg.text.split("\n").map((line, idx) => {
                            if (line.startsWith("- ")) {
                              return (
                                <p key={idx} className="ml-2 flex items-start gap-1.5 my-0.5">
                                  <span className="text-brand-400 mt-1">•</span>
                                  <span>{line.slice(2)}</span>
                                </p>
                              );
                            }
                            return <p key={idx} className="my-0.5">{line}</p>;
                          })}
                        </div>
                      </div>

                      <div
                        className={`flex items-center gap-1 text-[10px] text-slate-500 ${
                          msg.role === "user" ? "justify-end" : "justify-start ml-1"
                        }`}
                      >
                        <span>{msg.timestamp}</span>
                      </div>

                      {/* Suggested actions chips */}
                      {msg.suggestedActions && msg.suggestedActions.length > 0 && (
                        <div className="flex flex-wrap gap-1.5 pt-1">
                          {msg.suggestedActions.map((action, i) => (
                            <button
                              key={i}
                              onClick={() => handleSend(action)}
                              className="inline-flex items-center gap-1 rounded-full border border-brand-500/30 bg-brand-500/10 px-2.5 py-1 text-[11px] font-medium text-brand-300 hover:bg-brand-500/20 hover:text-white transition-colors"
                            >
                              <span>{action}</span>
                              <ChevronRight className="h-3 w-3 opacity-60" />
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    {msg.role === "user" && (
                      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-navy-700 text-slate-300 border border-slate-600">
                        <User className="h-3.5 w-3.5" />
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex gap-2.5 items-start">
                    <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-white border border-slate-700/60 overflow-hidden p-0.5">
                      <img src={chatbotIcon} className="h-full w-full object-contain animate-spin" alt="Assistant" />
                    </div>
                    <div className="rounded-2xl rounded-tl-none bg-navy-800/90 border border-slate-700/60 px-4 py-2.5 text-xs text-slate-300 flex items-center gap-2">
                      <span className="inline-block h-2 w-2 rounded-full bg-brand-400 animate-bounce"></span>
                      <span className="inline-block h-2 w-2 rounded-full bg-brand-400 animate-bounce [animation-delay:0.2s]"></span>
                      <span className="inline-block h-2 w-2 rounded-full bg-brand-400 animate-bounce [animation-delay:0.4s]"></span>
                      <span className="ml-1 text-[11px] text-slate-400">Thinking...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Footer */}
              <div className="border-t border-slate-800 bg-navy-950 p-3">
                <div className="flex items-center gap-2 rounded-xl border border-slate-700/60 bg-slate-900/90 px-3 py-1.5 focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask AI about shortages, predictions..."
                    disabled={loading}
                    className="flex-1 bg-transparent text-xs sm:text-sm text-white placeholder:text-slate-500 focus:outline-none disabled:opacity-50"
                  />
                  <button
                    onClick={() => handleSend()}
                    disabled={!input.trim() || loading}
                    className="flex h-7 w-7 items-center justify-center rounded-lg bg-brand-600 text-white transition-opacity hover:bg-brand-500 disabled:opacity-40"
                  >
                    <Send className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* 2. Floating Action Button (Custom Floating AI Chatbot Badge) */}
      {!isOpen && (
        <button
          onClick={() => {
            setIsOpen(true);
            setIsMinimized(false);
          }}
          className="group relative flex h-14 w-14 items-center justify-center rounded-full bg-slate-900 border border-slate-700 shadow-2xl transition-all hover:scale-105 hover:shadow-brand-600/60 active:scale-95"
          aria-label="Open AI Assistant"
        >
          <img src={chatbotIcon} className="h-10 w-10 object-contain bg-white rounded-full p-1" alt="AI Chat" />
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500 border border-slate-900"></span>
          </span>
        </button>
      )}
    </div>
  );
}



