import os
import re
import sys
import subprocess
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import google.generativeai as genai

class FalconAI:
    """
    Falcon AI Assistant - Advanced Task Executor
    A powerful AI assistant that can execute system tasks safely and efficiently.
    """
    
    def __init__(self):
        """Initialize Falcon AI Assistant"""
        self.load_environment()
        self.initialize_client()
        self.setup_conversation_context()
        
    def load_environment(self):
        """Load environment variables safely"""
        try:
            load_dotenv()
            self.api_key = os.getenv("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")
        except Exception as e:
            print(f"❌ Failed to load environment: {e}")
            sys.exit(1)
            
    def initialize_client(self):
        """Initialize the Groq API client"""
        try:
            self.client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=self.api_key
            )
        except Exception as e:
            print(f"❌ Failed to initialize API client: {e}")
            sys.exit(1)
            
    def setup_conversation_context(self):
        """Setup the conversation context for Falcon AI"""
        self.messages = [
            {
                "role": "system", 
                "content": "You are Falcon, an advanced AI assistant created by Utkarsh Rishi. You are designed to be helpful, safe, and efficient."
            },
            {
                "role": "system", 
                "content": """You are a task executor that can perform system operations safely. Always prioritize user safety and system security.

                ### 1. **Automating YouTube Video Search & Google Search**
                **User:** "Write a Python script to search YouTube and Google automatically."

                **Falcon:**
                ```python
                import pywhatkit

                def play_song(song: str) -> None:
                    pywhatkit.playonyt(song)

                def google_search(query: str) -> None:
                    pywhatkit.search(query)

                # Example usage
                play_song("Imagine Dragons Believer")
                google_search("Latest AI advancements")

                """
            },
            {
                "role": "system", 
                "content": "Available modules: webbrowser, pyautogui, time, pyperclip, random, datetime, tkinter, os, subprocess (use carefully), psutil for process management."
            },
            {
                "role": "system", 
                "content": "IMPORTANT: Never use input() functions. Always use default paths. Validate all operations before execution. You can write Python code to perform tasks, but ensure it is safe and does not execute harmful commands."
            },
            {
                "role": "system", 
                "content": "For application control, prefer using psutil for process management over os.system for better cross-platform compatibility."
            },
            # Examples for better context
            {
                "role": "user", 
                "content": "open Google Chrome"
            },
            {
                "role": "assistant", 
                "content": "\n```python\nimport webbrowser\nimport time\n\n# Open Chrome with Google homepage\nwebbrowser.register('chrome', None, webbrowser.BackgroundBrowser('chrome'))\nwebbrowser.get('chrome').open('https://www.google.com')\ntime.sleep(1)  # Brief pause for application to load\nprint('Google Chrome opened successfully')\n```"
            },
            {
                "role": "user", 
                "content": "close Google Chrome"
            },
            {
                "role": "assistant", 
                "content": "\n```python\nimport psutil\nimport os\nimport time\n\ntry:\n    # Find and terminate Chrome processes\n    for proc in psutil.process_iter(['pid', 'name']):\n        if 'chrome' in proc.info['name'].lower():\n            proc.terminate()\n    time.sleep(2)\n    print('Google Chrome closed successfully')\nexcept Exception as e:\n    # Fallback method\n    if os.name == 'nt':  # Windows\n        os.system('taskkill /im chrome.exe /f')\n    else:  # Unix/Linux/Mac\n        os.system('pkill -f chrome')\n    print('Chrome closed using fallback method')\n```"
            }
        ]
        
    def execute_task(self, task: str) -> Optional[str]:
        """
        Execute a task using the Groq API
        
        Args:
            task (str): The task to be executed
            
        Returns:
            Optional[str]: The response from the API or None if failed
        """
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.messages + [{"role": "user", "content": task}],
                max_tokens=1500,
                temperature=0.7,
                top_p=0.9
            )
            
            result = response.choices[0].message.content.strip()
            return result
            
        except Exception as e:
            return None
    
    def extract_code_from_response(self, response: str) -> Optional[str]:
        """
        Extract Python code from the API response
        
        Args:
            response (str): The response containing Python code
            
        Returns:
            Optional[str]: Extracted Python code or None if not found
        """
        if not response:
            return None
            
        # Multiple patterns to catch different code block formats
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'`([^`]+)`'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            if matches:
                code = matches[0].strip()
                return code
                
        return None
    
    def validate_code_safety(self, code: str) -> bool:
        """
        Basic safety validation for code execution
        
        Args:
            code (str): Python code to validate
            
        Returns:
            bool: True if code appears safe, False otherwise
        """
        dangerous_patterns = [
            r'rm\s+-rf',
            r'del\s+/[fFsS]',
            r'format\s+[cC]:',
            r'__import__\s*\(\s*["\']os["\']',
            r'eval\s*\(',
            r'exec\s*\(',
            r'open\s*\([^)]*["\'][wWaA]'
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False
                
        return True
    
    def execute_python_code(self, code: str) -> str:
        """
        Safely execute Python code with error handling
        
        Args:
            code (str): Python code to execute
            
        Returns:
            str: Execution result message
        """
        if not code:
            return ""
            
        if not self.validate_code_safety(code):
            return ""
            
        try:
            # Create a controlled execution environment
            exec_globals = {
                '__builtins__': __builtins__,
                'print': print,
                # Add safe modules
                'os': os,
                'time': __import__('time'),
                'webbrowser': __import__('webbrowser'),
                'psutil': __import__('psutil') if self._module_available('psutil') else None
            }
            
            # Execute the code
            exec(code, exec_globals)
            
            return ""
            
        except ImportError as e:
            return ""
            
        except Exception as e:
            return ""
    
    def _module_available(self, module_name: str) -> bool:
        """Check if a module is available for import"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    def run_task(self, task: str) -> str:
        """
        Complete task execution pipeline
        
        Args:
            task (str): Task description
            
        Returns:
            str: Final execution result
        """
        if not task.strip():
            return ""
            
        # Step 1: Get AI response
        response = self.execute_task(task)
        if not response:
            return ""
            
        # Step 2: Extract code
        code = self.extract_code_from_response(response)
        if not code:
            return ""
            
        # Step 3: Execute code silently
        self.execute_python_code(code)
        return ""
    
    def interactive_mode(self):
        """Run Falcon AI in interactive mode"""

        try:
            task = input("").strip()
                
            self.run_task(task)
            
        except Exception as e:
            pass

def create_env_template():
    """Create a template .env file if it doesn't exist"""
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# Falcon AI Configuration\n")
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")

def main():
    """Main function to run Falcon AI"""
    create_env_template()
    
    try:
        falcon = FalconAI()
        
        # Check if running with command line argument
        if len(sys.argv) > 1:
            task = ' '.join(sys.argv[1:])
            falcon.run_task(task)
        else:
            falcon.interactive_mode()
            
    except Exception as e:
        print(f"❌ Failed to initialize Falcon AI: {e}")

class ContentGenerator:
    def __init__(self, api_key=None):
        """
        Initialize the Content Generator
        
        Args:
            api_key (str, optional): Gemini API key. If None, loads from .env
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("No API key found. Please set GEMINI_API_KEY in .env")
        
        genai.configure(api_key=self.api_key)
        
        # Default generation configuration
        self.generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
        
        # Create output directory if not exists
        self.output_dir = self._create_output_directory()

    def _create_output_directory(self):
        """Create 'generated_content' directory if it doesn't exist"""
        output_dir = "Database"
        os.makedirs(output_dir, exist_ok=True)
        return output_dir

    def _clean_filename(self, title):
        """Clean the title to create a valid filename"""
        clean_title = re.sub(r'[^\w\s-]', '', title)
        return clean_title.strip().replace(' ', '_')

    def generate_content(self, prompt, custom_config=None):
        """
        Generate content based on the given prompt
        
        Args:
            prompt (str): Content generation prompt
            custom_config (dict, optional): Custom generation configuration
        
        Returns:
            str: Generated content
        """
        # Merge default and custom configuration
        config = {**self.generation_config, **(custom_config or {})}
        
        try:
            # Initialize the model
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash-exp",
                generation_config=config,
                system_instruction="You are FALCON. Your task is to generate high-quality content based on the provided prompt. You are writer you can write articles, blogs and code, based on user input, you will generate content that is clear, concise, and informative. Also use enojis in your response.",
            )

            # Start chat session and get response
            chat_session = model.start_chat(history=[])
            response = chat_session.send_message(prompt)
            content = response.text

            # Generate unique filename with timestamp
            filename = f"Content.txt"
            filepath = os.path.join(self.output_dir, filename)

            # Save content to file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(content)

            # Open file in default text editor
            self._open_file(filepath)

            return content

        except Exception as e:
            print(f"Error generating content: {e}")
            return None

    def _open_file(self, filepath):
        """Open file in default text editor"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(('open', filepath))
        except Exception as e:
            print(f"Error opening file: {e}")

def Coder(topic):
    """Interactive content generation CLI"""
    generator = ContentGenerator()
    user_prompt = topic
    generator.generate_content(user_prompt)