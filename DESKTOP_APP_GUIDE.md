# DeskMate Desktop App - User Guide

## 🎨 Modern Glass UI Desktop Application

Your DeskMate AI agent now has a beautiful desktop interface with glass morphism design!

## ✨ Features

### Visual Design
- **Glass Blur Effect**: Frosted glass cards with backdrop blur
- **Gradient Background**: Beautiful purple-to-indigo gradient
- **Smooth Animations**: Framer Motion powered transitions
- **Modern Icons**: Lucide React icon set
- **Responsive Layout**: Adapts to window resizing

### Functionality
- **System Control**: Open websites, applications, and file explorer
- **File Processing**: Read and summarize documents
- **Email Drafting**: Generate professional emails
- **Shell Commands**: Execute safe terminal commands
- **General Q&A**: Ask questions and get answers

## 🚀 Running the App

### Development Mode
```bash
cd frontend-desktop
npm run electron:dev
```

This will:
1. Start Vite dev server on port 5173
2. Launch Electron window automatically
3. Enable hot-reload for development

### Production Build
```bash
npm run electron:build
```

Creates a distributable desktop application.

## 💡 Usage Examples

### System Automation
- "Open youtube.com"
- "Launch chrome"
- "Open notepad"
- "Open file explorer"
- "Open my downloads folder"

### File Operations
- "Summarize report.pdf"
- "Read notes.txt"
- "Search for budget files"

### Communication
- "Draft an email about the project launch"
- "Write an email to the team"

### General
- "What can you do?"
- "Help"
- "What time is it?"

## ⌨️ Keyboard Shortcuts

- **Enter**: Send command
- **Shift + Enter**: New line in input
- **Ctrl/Cmd + A**: Select all text

## 🎯 UI Elements

### Suggestion Cards
Click on any suggestion card to auto-fill the command input with common tasks.

### Message Display
- **Green checkmark**: Successful execution
- **Red X**: Failed execution
- **Glass cards**: Each message in a beautiful frosted container
- **Intent badges**: Shows the detected intent (open_resource, general_qa, etc.)

### Input Area
- **Auto-resize textarea**: Grows with your text
- **Send button**: Disabled when empty or processing
- **Clear button**: Remove all messages

## 🔧 Technical Details

### Architecture
- **Frontend**: React + Vite
- **Desktop**: Electron (frameless transparent window)
- **Styling**: Custom CSS with glass morphism
- **Animations**: Framer Motion
- **API**: Axios connecting to FastAPI backend

### Window Features
- **Frameless**: No traditional title bar
- **Transparent**: See-through background
- **Vibrancy**: Native OS blur effects (macOS)
- **Resizable**: Min 800x600, default 1200x800

## 🐛 Troubleshooting

### Backend Not Running
Make sure the FastAPI backend is running:
```bash
cd ..
uvicorn app.main:app --reload
```

### Port Already in Use
If port 5173 is busy, Vite will automatically use the next available port.

### Window Not Appearing
Check the terminal for errors. The Electron window should open automatically after Vite starts.

## 📦 Building for Distribution

The app can be packaged for Windows, macOS, and Linux:

```bash
npm run electron:build
```

This creates installers in the `dist` folder.

## 🎨 Customization

### Colors
Edit `src/App.css` to change the color scheme:
- `--primary`: Main accent color
- `--glass-bg`: Glass card background
- `--text-primary`: Main text color

### Background
Change the gradient in `body` style:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Window Size
Edit `electron/main.js`:
```javascript
width: 1200,
height: 800,
```

Enjoy your beautiful new desktop interface! 🚀
