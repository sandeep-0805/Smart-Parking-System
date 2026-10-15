import React, { useState, useRef, useEffect } from 'react';
import { FiMessageSquare, FiX, FiSend, FiMinimize2, FiMaximize2, FiCalendar, FiMapPin } from 'react-icons/fi';
import { sendChatMessage } from '../../api/chat';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "👋 Hi! I'm your AI Parking Assistant. Ask me to find parking near Hitech City, Gachibowli, or book slots in English, Hindi, or Hinglish!",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (customText = null) => {
    const textToSend = customText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = { id: Date.now().toString(), sender: 'user', text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    if (!customText) setInput('');
    setLoading(true);

    try {
      const resp = await sendChatMessage(textToSend, sessionId);
      if (resp.session_id) {
        setSessionId(resp.session_id);
      }

      const botMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: resp.reply,
        options: resp.options || [],
        action_type: resp.action_type,
        booking_id: resp.booking_id,
        requires_login: resp.requires_login,
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          text: "Sorry, I had trouble processing that request. Please try our search page.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Toggle Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-blue-600 hover:bg-blue-700 text-white rounded-full p-3.5 shadow-xl transition-transform hover:scale-105 flex items-center justify-center focus:outline-none"
          title="Open AI Parking Assistant"
        >
          <FiMessageSquare className="w-6 h-6" />
        </button>
      )}

      {/* Slide-out / Floating Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 w-96 max-w-[calc(100vw-2rem)] h-[540px] max-h-[calc(100vh-5rem)] bg-white rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-200">
          {/* Header */}
          <div className="bg-blue-600 text-white px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-7 h-7 rounded-full bg-blue-500/80 flex items-center justify-center text-xs font-bold">
                AI
              </div>
              <div>
                <h3 className="font-bold text-sm leading-tight">AI Parking Assistant</h3>
                <span className="text-[10px] text-blue-100 flex items-center">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse"></span>
                  Llama 3.2 3B active
                </span>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-blue-100 hover:text-white p-1 rounded-md"
            >
              <FiX className="w-5 h-5" />
            </button>
          </div>

          {/* Messages Stream */}
          <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50 text-sm">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-3.5 py-2.5 shadow-2xs leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-blue-600 text-white rounded-tr-xs'
                      : 'bg-white text-slate-800 border border-slate-200/80 rounded-tl-xs'
                  }`}
                >
                  <p className="whitespace-pre-line">{m.text}</p>
                </div>

                {/* Option Cards */}
                {m.options && m.options.length > 0 && (
                  <div className="mt-2 w-full space-y-2">
                    {m.options.map((opt) => (
                      <div
                        key={opt.option_index}
                        className="bg-white border border-slate-200 rounded-xl p-3 shadow-xs hover:border-blue-400 transition-colors"
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="inline-block text-[10px] font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-1.5 py-0.5 rounded">
                              Option #{opt.option_index}
                            </span>
                            <h4 className="font-semibold text-slate-900 text-xs mt-0.5">
                              {opt.location_name}
                            </h4>
                            <p className="text-[11px] text-slate-500 truncate max-w-[180px]">
                              {opt.address}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="font-bold text-slate-900 text-xs">
                              {opt.price_formatted}
                            </span>
                            <p className="text-[10px] text-slate-400">
                              {Math.round(opt.distance_m)}m away
                            </p>
                          </div>
                        </div>

                        {/* Reason tags */}
                        {opt.reason_tags?.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {opt.reason_tags.slice(0, 2).map((t, i) => (
                              <span
                                key={i}
                                className="text-[9px] bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded"
                              >
                                {t}
                              </span>
                            ))}
                          </div>
                        )}

                        <button
                          onClick={() => handleSend(`Book option ${opt.option_index}`)}
                          className="mt-2.5 w-full bg-blue-50 hover:bg-blue-100 text-blue-700 font-medium text-xs py-1.5 rounded-lg transition-colors"
                        >
                          Select Option #{opt.option_index}
                        </button>
                      </div>
                    ))}
                  </div>
                )}

                {/* Booking Payment Link */}
                {m.action_type === 'payment_ready' && m.booking_id && (
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      navigate(`/bookings/${m.booking_id}`);
                    }}
                    className="mt-2 text-xs font-semibold bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg shadow-sm transition-colors"
                  >
                    Proceed to Payment for Booking #{m.booking_id} →
                  </button>
                )}

                {/* Login Prompt */}
                {m.requires_login && (
                  <button
                    onClick={() => {
                      setIsOpen(false);
                      navigate('/login');
                    }}
                    className="mt-2 text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-lg shadow-sm"
                  >
                    Log In to Reserve
                  </button>
                )}
              </div>
            ))}

            {loading && (
              <div className="flex items-center space-x-1.5 text-slate-400 text-xs">
                <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"></div>
                <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:0.2s]"></div>
                <div className="w-2 h-2 rounded-full bg-slate-400 animate-bounce [animation-delay:0.4s]"></div>
                <span className="text-[11px] ml-1">Extracting intent...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Quick suggestions */}
          <div className="px-3 py-1.5 bg-white border-t border-slate-100 flex items-center space-x-1.5 overflow-x-auto text-[11px]">
            <button
              onClick={() => handleSend('Parking near Hitech City tomorrow at 10 AM')}
              className="whitespace-nowrap bg-slate-100 hover:bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full"
            >
              Hitech City 10 AM
            </button>
            <button
              onClick={() => handleSend('Gachibowli with EV charging')}
              className="whitespace-nowrap bg-slate-100 hover:bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full"
            >
              Gachibowli EV
            </button>
            <button
              onClick={() => handleSend('Book the first one')}
              className="whitespace-nowrap bg-slate-100 hover:bg-slate-200 text-slate-600 px-2 py-0.5 rounded-full"
            >
              Book #1
            </button>
          </div>

          {/* Input Box */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="p-2.5 bg-white border-t border-slate-200 flex items-center space-x-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask for parking in any language..."
              className="flex-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white p-2 rounded-lg transition-colors focus:outline-none"
            >
              <FiSend className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}
    </>
  );
};
