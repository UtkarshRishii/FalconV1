<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FALCON AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            padding: 60px 0;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-bottom: 40px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .header h1 {
            font-size: 4rem;
            font-weight: 800;
            color: white;
            margin-bottom: 20px;
            text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }

        .header .subtitle {
            font-size: 1.5rem;
            color: rgba(255, 255, 255, 0.9);
            margin-bottom: 30px;
            font-weight: 300;
        }

        .header .tagline {
            font-size: 1.8rem;
            color: #FFD700;
            font-weight: 600;
            margin-bottom: 40px;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .badges {
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        .badge {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }

        .badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }

        .nav-links {
            display: flex;
            justify-content: center;
            gap: 20px;
            flex-wrap: wrap;
        }

        .nav-link {
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 12px 25px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-2px);
        }

        .section {
            background: white;
            margin: 30px 0;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .section h2 {
            font-size: 2.5rem;
            margin-bottom: 25px;
            color: #2c3e50;
            position: relative;
            padding-bottom: 15px;
        }

        .section h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 4px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 2px;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        .feature-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            transition: all 0.3s ease;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        }

        .feature-card h3 {
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3rem;
        }

        .feature-card p {
            color: #6c757d;
            line-height: 1.6;
        }

        .demo-box {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

        .demo-line {
            margin: 10px 0;
            padding: 5px 0;
        }

        .demo-line.user {
            color: #3498db;
        }

        .demo-line.system {
            color: #e74c3c;
        }

        .demo-line.success {
            color: #2ecc71;
        }

        .installation-steps {
            counter-reset: step-counter;
        }

        .install-step {
            counter-increment: step-counter;
            background: #f8f9fa;
            margin: 20px 0;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #667eea;
            position: relative;
        }

        .install-step::before {
            content: counter(step-counter);
            position: absolute;
            left: -15px;
            top: 15px;
            background: #667eea;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }

        .install-step h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .code-block {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 15px 0;
            overflow-x: auto;
        }

        .project-tree {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }

        .commands-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            border-radius: 10px;
            overflow: hidden;
        }

        .commands-table th,
        .commands-table td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }

        .commands-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
        }

        .commands-table tr:hover {
            background: #f8f9fa;
        }

        .footer {
            text-align: center;
            padding: 50px 0;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-top: 40px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .footer h3 {
            color: white;
            font-size: 1.5rem;
            margin-bottom: 20px;
        }

        .footer p {
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
        }

        .star-button {
            display: inline-block;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            color: #2c3e50;
            padding: 15px 30px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: 700;
            margin: 20px 10px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(255, 215, 0, 0.4);
        }

        .star-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6);
        }

        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            
            .header .subtitle {
                font-size: 1.2rem;
            }
            
            .header .tagline {
                font-size: 1.4rem;
            }
            
            .section {
                padding: 25px;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header Section -->
        <div class="header">
            <h1>🦅 FALCON AI Assistant</h1>
            <p class="subtitle">A powerful Voice-Controlled AI Assistant built with Python</p>
            <p class="tagline">🤖 "Automate tasks. Speak. Listen. Create. All in one — with FALCON."</p>
            
            <div class="badges">
                <a href="#" class="badge">FALCON AI</a>
                <a href="#" class="badge">Python 3.8+</a>
                <a href="#" class="badge">MIT License</a>
            </div>
            
            <div class="nav-links">
                <a href="#" class="nav-link">📺 YouTube Demo</a>
                <a href="#" class="nav-link">🐛 Report Bug</a>
                <a href="#" class="nav-link">💡 Request Feature</a>
            </div>
        </div>

        <!-- Features Section -->
        <div class="section">
            <h2>🎯 Features</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <h3>🎤 Real-time Voice Control</h3>
                    <p>Advanced Speech-to-Text & Text-to-Speech capabilities for seamless interaction</p>
                </div>
                <div class="feature-card">
                    <h3>⚡ System Command Execution</h3>
                    <p>Open/close apps, search web, and automate system actions with voice commands</p>
                </div>
                <div class="feature-card">
                    <h3>🧠 AI Content Generation</h3>
                    <p>Create blogs, articles, and code snippets using advanced AI models</p>
                </div>
                <div class="feature-card">
                    <h3>🎨 AI Image Generation</h3>
                    <p>Generate stunning visuals from text prompts with state-of-the-art AI</p>
                </div>
                <div class="feature-card">
                    <h3>💾 Smart Memory System</h3>
                    <p>Chat history & conversation context stored intelligently in database</p>
                </div>
                <div class="feature-card">
                    <h3>📊 Data Export</h3>
                    <p>Export conversation history in CSV or Excel format for analysis</p>
                </div>
            </div>
        </div>

        <!-- Demo Section -->
        <div class="section">
            <h2>📸 Demo</h2>
            <div class="demo-box">
                <div class="demo-line user">🧠 "Hello FALCON, open Chrome and play some music."</div>
                <div class="demo-line system">🎵 Opening Google Chrome...</div>
                <div class="demo-line system">🎶 Searching for music on YouTube...</div>
                <div class="demo-line success">✅ Task completed successfully!</div>
            </div>
            <p style="text-align: center; margin-top: 20px; font-style: italic;">
                🎥 <strong>YouTube demo coming soon!</strong> <a href="#" style="color: #667eea;">Subscribe here</a> to be notified
            </p>
        </div>

        <!-- Installation Section -->
        <div class="section">
            <h2>🚀 Quick Start</h2>
            
            <h3>Prerequisites</h3>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li>Python 3.8 or higher</li>
                <li>Internet connection for AI services</li>
                <li>Microphone for voice commands (optional)</li>
            </ul>

            <div class="installation-steps">
                <div class="install-step">
                    <h3>Clone the repository</h3>
                    <div class="code-block">
git clone https://github.com/yourusername/FALCON-AI-Assistant.git
cd FALCON-AI-Assistant
                    </div>
                </div>

                <div class="install-step">
                    <h3>Install dependencies</h3>
                    <div class="code-block">
pip install -r requirements.txt
                    </div>
                </div>

                <div class="install-step">
                    <h3>Setup environment variables</h3>
                    <p>Create a <code>.env</code> file in the root directory:</p>
                    <div class="code-block">
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
                    </div>
                </div>

                <div class="install-step">
                    <h3>Launch FALCON</h3>
                    <div class="code-block">
python Falcon.py
                    </div>
                    <p>🌐 Opens automatically at: <strong>http://localhost:8000</strong></p>
                </div>
            </div>
        </div>

        <!-- Project Structure -->
        <div class="section">
            <h2>🏗️ Project Structure</h2>
            <div class="project-tree">
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
            </div>
        </div>

        <!-- Voice Commands -->
        <div class="section">
            <h2>🎤 Voice Commands</h2>
            <p>FALCON responds to natural language commands:</p>
            
            <table class="commands-table">
                <thead>
                    <tr>
                        <th>Command Type</th>
                        <th>Examples</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>System Control</strong></td>
                        <td><em>"Open Google Chrome"</em>, <em>"Close all browser windows"</em></td>
                    </tr>
                    <tr>
                        <td><strong>Web Navigation</strong></td>
                        <td><em>"Search YouTube for lo-fi music"</em>, <em>"Open Gmail"</em></td>
                    </tr>
                    <tr>
                        <td><strong>Content Creation</strong></td>
                        <td><em>"Write an article about AI"</em>, <em>"Generate a Python script"</em></td>
                    </tr>
                    <tr>
                        <td><strong>Image Generation</strong></td>
                        <td><em>"Create an image of a cyberpunk city"</em>, <em>"Generate a sunset landscape"</em></td>
                    </tr>
                    <tr>
                        <td><strong>File Management</strong></td>
                        <td><em>"Save this conversation"</em>, <em>"Export chat history"</em></td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Data Export -->
        <div class="section">
            <h2>📊 Data Export</h2>
            <p>Export your conversation history programmatically:</p>
            <div class="code-block">
# Export as CSV
assistant.export_chat_history('csv')

# Export as Excel
assistant.export_chat_history('excel')
            </div>
        </div>

        <!-- Configuration -->
        <div class="section">
            <h2>🔧 Configuration</h2>
            <h3>API Keys Required</h3>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li><strong>GROQ API</strong>: For natural language processing</li>
                <li><strong>GEMINI API</strong>: For advanced AI capabilities</li>
            </ul>
            
            <h3>Optional Settings</h3>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li>Voice recognition sensitivity</li>
                <li>Response speed preferences</li>
                <li>Default export formats</li>
            </ul>
        </div>

        <!-- Contributing -->
        <div class="section">
            <h2>🤝 Contributing</h2>
            <p>We welcome contributions! Here's how you can help:</p>
            <ol style="margin: 20px 0; padding-left: 20px;">
                <li>🍴 Fork the repository</li>
                <li>🌟 Create a feature branch (<code>git checkout -b feature/AmazingFeature</code>)</li>
                <li>💾 Commit your changes (<code>git commit -m 'Add some AmazingFeature'</code>)</li>
                <li>📤 Push to the branch (<code>git push origin feature/AmazingFeature</code>)</li>
                <li>🔄 Open a Pull Request</li>
            </ol>
        </div>

        <!-- License -->
        <div class="section">
            <h2>📝 License</h2>
            <p>This project is licensed under the MIT License - see the <a href="LICENSE" style="color: #667eea;">LICENSE</a> file for details.</p>
        </div>

        <!-- Support -->
        <div class="section">
            <h2>📞 Support</h2>
            <ul style="margin: 20px 0; padding-left: 20px;">
                <li>🐛 <strong>Found a bug?</strong> <a href="#" style="color: #667eea;">Open an issue</a></li>
                <li>💡 <strong>Have a suggestion?</strong> <a href="#" style="color: #667eea;">Request a feature</a></li>
                <li>📺 <strong>Stay updated</strong>: <a href="#" style="color: #667eea;">Subscribe on YouTube</a></li>
            </ul>
        </div>

        <!-- Footer -->
        <div class="footer">
            <h3>Made with ❤️ by Utkarsh Rishi</h3>
            <p>⭐ Don't forget to star the repo if you found it helpful! ⭐</p>
            <a href="#" class="star-button">⭐ Star this Repository</a>
            <a href="#" class="star-button">📺 Subscribe on YouTube</a>
        </div>
    </div>
</body>
</html>
