import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Loader2, CheckCircle, XCircle, Globe, Folder, Cpu, Menu, X, Clock, Sparkles, Wifi, WifiOff } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import './App.css';
import './SystemInfo.css';

// Use 127.0.0.1 instead of localhost to avoid DNS issues
const API_BASE = 'http://127.0.0.1:8000';

// Create axios instance with proper configuration
const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // Reduced from 30s to 10s
  headers: {
    'Content-Type': 'application/json',
  }
});

function App() {
  const [command, setCommand] = useState('');
  const [conversation, setConversation] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [connectionError, setConnectionError] = useState(false);
  const textareaRef = useRef(null);
  const conversationEndRef = useRef(null);

  const scrollToBottom = () => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  // Test backend connection on component mount
  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    try {
      await api.get('/health');
      setConnectionError(false);
    } catch (error) {
      console.error('Backend connection failed:', error);
      setConnectionError(true);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!command.trim() || loading) return;

    const userCommand = command;
    setCommand('');

    const userMessage = {
      type: 'user',
      content: userCommand,
      timestamp: new Date()
    };

    setConversation(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      console.log('Sending command:', userCommand);

      const response = await api.post('/api/v1/agent/query', {
        command: userCommand
      });

      console.log('Received response:', response.data);

      const assistantMessage = {
        type: 'assistant',
        content: response.data,
        timestamp: new Date()
      };

      setConversation(prev => [...prev, assistantMessage]);
      setConnectionError(false);

    } catch (error) {
      console.error('API Error:', error);

      let errorMessage = 'Unknown error occurred';

      if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNREFUSED') {
        errorMessage = 'Cannot connect to DeskMate backend. Make sure the server is running on http://localhost:8000';
        setConnectionError(true);
      } else if (error.response) {
        // Server responded with error status
        errorMessage = error.response.data?.detail || `Server error: ${error.response.status}`;
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Check if backend is running.';
        setConnectionError(true);
      } else {
        errorMessage = error.message;
      }

      const errorMsg = {
        type: 'error',
        content: errorMessage,
        timestamp: new Date()
      };
      setConversation(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setConversation([]);
  };

  const handleSuggestionClick = (suggestion) => {
    setCommand(suggestion);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderStepResult = (step, stepIdx) => {
    const result = step.result;

    if (!result.success) {
      return (
        <div key={stepIdx} className="step-result">
          <div className="step-status error">
            <XCircle size={16} />
            <span>{step.action} failed</span>
          </div>
          <div className="step-output error">
            {result.error || 'Unknown error occurred'}
          </div>
        </div>
      );
    }

    const output = result.output || {};

    // Handle different action types with friendly messages
    switch (step.action) {
      case 'open_url':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Website opened</span>
            </div>
            <div className="step-output friendly">
              ✅ {output.friendly_message || `Opened ${output.url}`}
            </div>
          </div>
        );

      case 'open_app':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Application launched</span>
            </div>
            <div className="step-output friendly">
              ✅ {output.friendly_message || `Launched ${output.app_name}`}
            </div>
          </div>
        );

      case 'open_explorer':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>File Explorer opened</span>
            </div>
            <div className="step-output friendly">
              ✅ {output.friendly_message || 'File Explorer opened'}
            </div>
          </div>
        );

      case 'answer_question':
        return (
          <div key={stepIdx} className="step-result">
            <div className="message-content markdown-content">
              <ReactMarkdown>{output.answer || 'No response generated'}</ReactMarkdown>
            </div>
          </div>
        );

      case 'generate_email':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Email draft created</span>
            </div>
            <div className="email-draft">
              <div className="email-header">
                <strong>Subject:</strong> {output.subject || 'No Subject'}
              </div>
              <div className="email-header">
                <strong>To:</strong> {output.recipient || 'No Recipient'}
              </div>
              <div className="email-body">
                <ReactMarkdown>{output.email_draft || output.body || 'No content'}</ReactMarkdown>
              </div>
            </div>
          </div>
        );

      case 'read_file':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>File read</span>
            </div>
            {output.content ? (
              <div className="step-output">
                <strong>Content:</strong>
                <div className="file-content">
                  {output.content}
                </div>
              </div>
            ) : (
              <div className="step-output error">
                {output.error || 'No content found'}
              </div>
            )}
          </div>
        );

      case 'run_shell':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Command executed</span>
            </div>
            {output.friendly_message && (
              <div className="step-output friendly">
                {output.friendly_message}
              </div>
            )}
            {output.output && (
              <div className="step-output">
                <strong>Output:</strong>
                <pre>{output.output}</pre>
              </div>
            )}
            {output.error && (
              <div className="step-output error">
                <strong>Error:</strong>
                <pre>{output.error}</pre>
              </div>
            )}
          </div>
        );

      case 'create_file':
      case 'create_folder':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>{step.action === 'create_file' ? 'File created' : 'Folder created'}</span>
            </div>
            <div className="step-output friendly">
              {output.friendly_message || output.output || 'Created successfully'}
            </div>
          </div>
        );

      case 'get_system_info':
        const sysInfo = output.output;
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>System Information</span>
            </div>
            <div className="system-info-modern">
              {/* OS Info Card */}
              <div className="info-card os-card">
                <div className="card-icon">💻</div>
                <div className="card-content">
                  <h4>{sysInfo.system}</h4>
                  <p className="card-subtitle">{sysInfo.architecture}</p>
                  <div className="card-detail">
                    <span className="detail-label">Processor:</span>
                    <span className="detail-value">{sysInfo.machine}</span>
                  </div>
                  <div className="card-detail">
                    <span className="detail-label">Python:</span>
                    <span className="detail-value">{sysInfo.python_version}</span>
                  </div>
                </div>
              </div>

              {/* CPU Card */}
              {sysInfo.cpu && (
                <div className="info-card cpu-card">
                  <div className="card-icon">⚙️</div>
                  <div className="card-content">
                    <h4>CPU</h4>
                    <p className="card-subtitle">{sysInfo.processor}</p>
                    <div className="card-detail">
                      <span className="detail-label">Cores:</span>
                      <span className="detail-value">{sysInfo.cpu.cores} Physical / {sysInfo.cpu.logical_cores} Logical</span>
                    </div>
                    <div className="card-detail">
                      <span className="detail-label">Frequency:</span>
                      <span className="detail-value">{sysInfo.cpu.frequency_mhz} MHz</span>
                    </div>
                    <div className="usage-bar-container">
                      <div className="usage-label">
                        <span>Usage</span>
                        <span className="usage-percent">{sysInfo.cpu.usage_percent}%</span>
                      </div>
                      <div className="usage-bar">
                        <div
                          className="usage-fill cpu-fill"
                          style={{ width: `${sysInfo.cpu.usage_percent}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* RAM Card */}
              {sysInfo.ram && (
                <div className="info-card ram-card">
                  <div className="card-icon">🧠</div>
                  <div className="card-content">
                    <h4>Memory (RAM)</h4>
                    <p className="card-subtitle">{sysInfo.ram.total_gb} GB Total</p>
                    <div className="card-detail">
                      <span className="detail-label">Used:</span>
                      <span className="detail-value">{sysInfo.ram.used_gb} GB</span>
                    </div>
                    <div className="card-detail">
                      <span className="detail-label">Available:</span>
                      <span className="detail-value">{sysInfo.ram.available_gb} GB</span>
                    </div>
                    <div className="usage-bar-container">
                      <div className="usage-label">
                        <span>Usage</span>
                        <span className="usage-percent">{sysInfo.ram.percent}%</span>
                      </div>
                      <div className="usage-bar">
                        <div
                          className="usage-fill ram-fill"
                          style={{ width: `${sysInfo.ram.percent}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Storage Card */}
              {sysInfo.storage && (
                <div className="info-card storage-card">
                  <div className="card-icon">💾</div>
                  <div className="card-content">
                    <h4>Storage ({sysInfo.storage.drive})</h4>
                    <p className="card-subtitle">{sysInfo.storage.total_gb} GB Total</p>
                    <div className="card-detail">
                      <span className="detail-label">Used:</span>
                      <span className="detail-value">{sysInfo.storage.used_gb} GB</span>
                    </div>
                    <div className="card-detail">
                      <span className="detail-label">Free:</span>
                      <span className="detail-value">{sysInfo.storage.free_gb} GB</span>
                    </div>
                    <div className="usage-bar-container">
                      <div className="usage-label">
                        <span>Usage</span>
                        <span className="usage-percent">{sysInfo.storage.percent}%</span>
                      </div>
                      <div className="usage-bar">
                        <div
                          className="usage-fill storage-fill"
                          style={{ width: `${sysInfo.storage.percent}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Fallback message if psutil not available */}
              {sysInfo.note && (
                <div className="info-note">
                  ℹ️ {sysInfo.note}
                </div>
              )}
            </div>
          </div>
        );

      case 'get_time':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Current Time</span>
            </div>
            <div className="step-output friendly">
              {output.friendly_message || output.output}
            </div>
          </div>
        );

      case 'open_terminal':
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>Terminal opened</span>
            </div>
            <div className="step-output friendly">
              {output.friendly_message || 'Terminal launched'}
            </div>
          </div>
        );

      default:
        // For any unknown action, try to show friendly_message first
        return (
          <div key={stepIdx} className="step-result">
            <div className="step-status success">
              <CheckCircle size={16} />
              <span>{step.action}</span>
            </div>
            <div className="step-output friendly">
              {output.friendly_message || output.message || output.output || JSON.stringify(output, null, 2)}
            </div>
          </div>
        );
    }
  };

  const renderMessage = (msg, idx) => {
    if (msg.type === 'user') {
      return (
        <motion.div
          key={idx}
          className="message user-message"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <div className="message-content">{msg.content}</div>
        </motion.div>
      );
    } else if (msg.type === 'assistant') {
      const result = msg.content;

      return (
        <motion.div
          key={idx}
          className="message assistant-message"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          {/* Show intent information */}
          {result.intent && (
            <div className="intent-info">
              <small>Intent: <strong>{result.intent.intent}</strong></small>
              {result.intent.confirmation_required && (
                <span className="confirmation-badge">⚠️ Requires confirmation</span>
              )}
            </div>
          )}

          {/* Show step results */}
          {result.results && result.results.length > 0 ? (
            <div className="steps-container">
              {result.results.map((step, stepIdx) => renderStepResult(step, stepIdx))}
            </div>
          ) : (
            <div className="message-content">
              {result.success ? 'Command processed successfully' : 'Command failed'}
            </div>
          )}
        </motion.div>
      );
    } else {
      return (
        <motion.div
          key={idx}
          className="message error-message"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <XCircle size={16} />
          <span>{msg.content}</span>
        </motion.div>
      );
    }
  };



  return (
    <div className="app">
      {/* Connection Status */}
      {connectionError && (
        <div className="connection-banner error">
          ⚠️ Cannot connect to DeskMate backend. Make sure the server is running on http://localhost:8000
        </div>
      )}

      {/* Sidebar Toggle */}
      <motion.button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </motion.button>

      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              className="sidebar-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSidebarOpen(false)}
            />
            <motion.div
              className="sidebar"
              initial={{ x: -320 }}
              animate={{ x: 0 }}
              exit={{ x: -320 }}
              transition={{ type: 'tween', duration: 0.2 }}
            >
              <div className="sidebar-header">
                <h2>History</h2>
                <button onClick={handleClear} className="clear-history-btn">
                  Clear
                </button>
              </div>
              <div className="sidebar-content">
                {conversation.length === 0 ? (
                  <div className="empty-history">
                    <Clock size={40} />
                    <p>No history yet</p>
                  </div>
                ) : (
                  <div className="history-list">
                    {conversation.filter(m => m.type === 'user').map((msg, idx) => (
                      <div key={idx} className="history-item">
                        <div className="history-command">{msg.content}</div>
                        <div className="history-time">{formatTime(msg.timestamp)}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <div className="main-content">
        {conversation.length === 0 ? (
          <>
            <motion.div
              className="header"
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="logo">
                <Sparkles size={40} />
              </div>
              <h1>DeskMate AI</h1>
              <p>Your intelligent desktop assistant</p>
              {connectionError && (
                <div className="connection-hint">
                  ⚠️ Backend not connected. Start the server with: <code>uvicorn app.main:app --reload</code>
                </div>
              )}
            </motion.div>

            <motion.div
              className="suggestions-container"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.1, duration: 0.3 }}
            >
              <div className="suggestions">
                {[
                  { icon: Globe, title: 'Open Website', command: 'Open youtube.com', color: '#ef4444' },
                  { icon: Cpu, title: 'Launch App', command: 'Open notepad', color: '#3b82f6' },
                  { icon: Folder, title: 'File Explorer', command: 'Open file explorer', color: '#10b981' },
                  { icon: Send, title: 'Draft Email', command: 'Draft email about meeting', color: '#8b5cf6' },
                  { icon: Folder, title: 'List Files', command: 'Run dir command', color: '#f59e0b' },
                  { icon: Sparkles, title: 'Get Help', command: 'What can you do', color: '#06b6d4' }
                ].map((suggestion, idx) => (
                  <motion.div
                    key={idx}
                    className="suggestion-card"
                    onClick={() => handleSuggestionClick(suggestion.command)}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + idx * 0.05 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="suggestion-icon" style={{ backgroundColor: suggestion.color }}>
                      <suggestion.icon size={20} />
                    </div>
                    <h4>{suggestion.title}</h4>
                    <p>{suggestion.command}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </>
        ) : (
          <div className="conversation-area">
            <div className="conversation-messages">
              {conversation.map((msg, idx) => renderMessage(msg, idx))}
              {loading && (
                <motion.div
                  className="message assistant-message loading-message"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <Loader2 size={16} className="spinner" />
                  <span>Thinking...</span>
                </motion.div>
              )}
              <div ref={conversationEndRef} />
            </div>
          </div>
        )}

        <motion.div
          className="input-container"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.3 }}
        >
          <form onSubmit={handleSubmit} className="input-area">
            <div className="input-wrapper">
              <textarea
                ref={textareaRef}
                value={command}
                onChange={(e) => setCommand(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask DeskMate to open websites, launch apps, draft emails, or run commands..."
                disabled={loading}
                rows={1}
              />
            </div>
            <motion.button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !command.trim()}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              {loading ? <Loader2 size={20} className="spinner" /> : <Send size={20} />}
            </motion.button>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
export default App;