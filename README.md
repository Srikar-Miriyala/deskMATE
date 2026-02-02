# DeskMate 🤖

DeskMate is a powerful, local-first desktop agent capable of multitasking, file management, and system automation. It combines a modern React-based UI with a robust Python backend to assist you with your daily tasks.

## ✨ Features

- **🤖 Conversational AI**: Chat naturally with DeskMate about any topic.
- **📂 File Management**: Read, summarize, and search for files.
- **🆕 File Creation**: Create new files and folders directly from chat.
- **📧 Email Drafting**: Generate professional emails instantly.
- **💻 System Control**: Open apps, websites, and the terminal.
- **📺 Media Control**: Play YouTube videos and search for content.
- **🔒 Local & Safe**: Runs locally with safety checks for all commands.
- **🎨 Modern UI**: Beautiful glass-morphism design with dark mode.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js & npm
- Google Gemini API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/deskMATE.git
   cd deskMATE
   ```

2. **Backend Setup**
   ```bash
   pip install -r requirements.txt
   ```
   Create a `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Frontend Setup**
   ```bash
   cd frontend-desktop
   npm install
   ```

### Running the App

1. **Start the Backend**
   ```bash
   python run.py
   ```

2. **Start the Frontend** (in a new terminal)
   ```bash
   cd frontend-desktop
   npm run electron:dev
   ```

## 💡 Usage Examples

- **"Open YouTube and play RRR glimpse"**
- **"Create folder ProjectX"**
- **"Summarize report.pdf"**
- **"Open terminal"**
- **"Draft an email to boss about the delay"**

## 🛠️ Tech Stack

- **Backend**: FastAPI, Google Gemini, Python
- **Frontend**: React, Electron, Tailwind CSS (optional)
- **Design**: Glassmorphism, CSS Animations

## 📄 License

MIT License
