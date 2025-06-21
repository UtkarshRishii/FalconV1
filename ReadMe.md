🚀 Quick Start

Prerequisites
Python 3.12.5
Internet connection for AI services
Microphone for voice commands (optional)
Installation
Clone the repository

git clone https://github.com/UtkarshRishii/FalconV1.git
cd FALCON-AI-Assistant

Install dependencies
pip install -r requirements.txt
Setup environment variables
Create a .env file in the root directory:
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

Launch FALCON

python Falcon.py
🌐 Opens automatically at: http://localhost:8000

🏗️ Project Structure
📦 FALCON-AI-Assistant/
├── 🔧 Backend/
│   ├── Automation.py      # Task execution engine (Groq + safety layer)
│   ├── Brain.py          # Core AI assistant with memory/tools
│   ├── ImageGen.py       # AI-based image generation
│   ├── STT.py           # Speech-to-Text processing
│   └── TTS.py           # Text-to-Speech synthesis
├── 🗄️ Database/          # Content storage & chat history
├── 🌐 web/              # Eel-based frontend interface
├── 🚀 Falcon.py         # Main application launcher
├── ⚙️ .env              # Environment configuration
└── 📋 requirements.txt   # Python dependencies
🎤 Voice Commands
FALCON responds to natural language commands:

Command Type	Examples
System Control	"Open Google Chrome", "Close all browser windows"
Web Navigation	"Search YouTube for lo-fi music", "Open Gmail"
Content Creation	"Write an article about AI", "Generate a Python script"
Image Generation	"Create an image of a cyberpunk city", "Generate a sunset landscape"

🤝 Contributing
We welcome contributions! Here's how you can help:

Made with ❤️ by Utkarsh Rishi
⭐ Don't forget to star the repo if you found it helpful! ⭐