🦅 FALCON AI Assistant
A powerful Voice-Controlled AI Assistant built using Python, designed by Utkarsh Rishi.

🤖 “Automate tasks. Speak. Listen. Create. All in one — with FALCON.”

🎯 Features
✅ Real-time voice control (Speech-to-Text & Text-to-Speech)
✅ Execute system commands (open/close apps, search web, automate actions)
✅ AI-generated content: blogs, articles, code snippets
✅ Stunning AI image generation from text prompts
✅ Chat memory & conversation history stored in a database
✅ Export history in CSV or Excel format

📸 Sneak Peek
🧠 "Hello FALCON, open Chrome and play some music."

🎥 YouTube demo coming soon: Subscribe here

🛠️ Installation
📁 Clone the repo:
git clone https://github.com/yourusername/FALCON-AI-Assistant.git
cd FALCON-AI-Assistant

📦 Install requirements:
pip install -r requirements.txt

🔐 Setup .env file:
Create a .env in the root directory with your API keys:

.env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

🧠 Project Structure
📦 FALCON-AI-Assistant
├── Backend/
│   ├── Automation.py       # Task execution engine (Groq + safety layer)
│   ├── Brain.py            # Core AI assistant with memory/tools
│   ├── ImageGen.py         # AI-based image generation
│   ├── STT.py              # Voice input using speech recognition
│   ├── TTS.py              # Text-to-Speech using OpenAI.fm
├── Database/               # Stores content, images, chat DB
├── web/                    # Eel UI frontend (index.html required)
├── Falcon.py               # Main launcher for FALCON app
├── .env                    # Environment configuration
├── requirements.txt        # All Python dependencies

🚀 Running the Assistant
Launch FALCON from terminal:
python Falcon.py
🔗 Opens a local GUI in your browser: http://localhost:8000

🔊 Sample Commands
You can speak or type commands like:

"Open Google Chrome"
"Search YouTube for lo-fi music"
"Generate an image of a cyberpunk city"
"Write an article about future of AI"
"Close all browser windows"

📁 Chat History Export
Export chat logs as .csv or .xlsx:
assistant.export_chat_history('csv')
assistant.export_chat_history('excel')

📜 License
This project is licensed under the MIT License.
Feel free to use, remix, or build your own assistant from it!

🙌 Made with ❤️ by Utkarsh Rishi
🔔 Don’t forget to ⭐ star the repo & subscribe on YouTube
