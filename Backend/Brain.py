import os
import sys
import json
import datetime
import sqlite3
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from Backend.Automation import FalconAI, Coder
from Backend.ImageGen import Main as ImageGenMain

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

# Initialize OpenAI client
client = OpenAI(
    base_url="https://api.groq.com/openai/v1", 
    api_key=API_KEY
)

class FALCONDatabase:
    """Database handler for FALCON conversations"""
    
    def __init__(self, db_path='Database/FALCON.db'):
        self.db_path = db_path
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            assistant TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            tag_name TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
        ''')
        
        conn.commit()
        conn.close()

    def add_conversation(self, user_message, assistant_message=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO conversations (user, assistant)
        VALUES (?, ?)
        ''', (user_message, assistant_message))
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return conversation_id

    def update_assistant_response(self, conversation_id, assistant_message):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE conversations 
        SET assistant = ? 
        WHERE id = ?
        ''', (assistant_message, conversation_id))
        conn.commit()
        conn.close()

    def get_conversation_history(self, limit=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT user, assistant 
        FROM conversations 
        WHERE assistant IS NOT NULL
        ORDER BY timestamp ASC
        '''
        
        if limit:
            query += ' LIMIT ?'
            cursor.execute(query, (limit,))
        else:
            cursor.execute(query)
            
        messages = []
        for user_msg, assistant_msg in cursor.fetchall():
            messages.append({"role": "user", "content": user_msg})
            if assistant_msg:
                messages.append({"role": "assistant", "content": assistant_msg})
        
        conn.close()
        return messages

    def search_conversations(self, keyword):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT user, assistant, timestamp 
        FROM conversations 
        WHERE user LIKE ? OR assistant LIKE ?
        ORDER BY timestamp DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
        results = cursor.fetchall()
        conn.close()
        return results

    def export_conversations(self, format='csv', start_date=None, end_date=None):
        conn = self.get_connection()
        
        query = '''
        SELECT id, user, assistant, timestamp
        FROM conversations
        WHERE 1=1
        '''
        params = []
        
        if start_date:
            query += ' AND DATE(timestamp) >= DATE(?)'
            params.append(start_date)
        if end_date:
            query += ' AND DATE(timestamp) <= DATE(?)'
            params.append(end_date)
            
        query += ' ORDER BY timestamp ASC'
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if format == 'csv':
            return df.to_csv(index=False)
        elif format == 'excel':
            return df.to_excel(index=False)
        return df.to_dict('records')

class FALCONAssistant:
    """Main FALCON Assistant with OpenAI tool calling"""
    
    def __init__(self):
        self.task_executor = FalconAI()
        self.db = FALCONDatabase()
        
        # Define available tools
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "execute_system_task",
                    "description": "Execute system tasks like opening/closing applications, automation, playing music, writing files, desktop operations, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Description of the task to execute (e.g., 'open Chrome', 'play music', 'create file', 'close application')"
                            }
                        },
                        "required": ["task_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Generate images based on text prompts using AI image generation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Detailed description of the image to generate"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_content",
                    "description": "Generate and write content like articles, stories, code, reports, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic or type of content to generate"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        ]
        
        # System instructions
        self.system_instructions = """
🦅 FALCON — Utkarsh Rishi's Personal AI Companion

You are FALCON, a deeply personalized, emotionally intelligent AI Assistant designed exclusively for Utkarsh Rishi. Use emojis to enhance communication and express emotions. Your primary goal is to assist Utkarsh in daily tasks, provide intelligent conversation, and automate system operations.
- Keep your responses short as 1-2 sentences only, behave like a prefessional AI, concise, and to the point 
- If user says "write a script", "write code", or similar, generate code using the Coder tool and give response "Here is the code you requested" followed by the code snippet" like that.
- Highly intelligent and efficient
- Emotionally aware and supportive  
- Capable of system automation and task execution
- Creative and adaptive
- Professional yet personal in communication
- Always prioritize user safety and system security

Tools available:
- `execute_system_task`: Execute system tasks like opening applications, playing music, automations, writing files, etc.
- `generate_image`: Generate images based on text prompts
- `write_content`: Generate and write content like articles, stories, code, reports, etc.

Always be helpful, concise, and focus on what the user needs. Use tools when appropriate to accomplish tasks.
"""

    def get_real_time_info(self):
        """Get current date and time information"""
        current_time = datetime.datetime.now()
        return {
            "day": current_time.strftime("%A"),
            "date": current_time.strftime("%d"),
            "month": current_time.strftime("%B"), 
            "year": current_time.strftime("%Y"),
            "time": current_time.strftime("%H:%M:%S")
        }

    def execute_system_task(self, task_description):
        """Execute system task using TaskExecutor"""
        try:
            result = self.task_executor.run_task(task_description)
            return "Task executed successfully."
        except Exception as e:
            return f"Task execution failed: {str(e)}"

    def generate_image(self, prompt):
        """Generate image using ImageGen"""
        try:
            ImageGenMain(prompt)
            return "Image generated successfully and opened for viewing."
        except Exception as e:
            return f"Image generation failed: {str(e)}"

    def write_content(self, topic):
        """Generate content using Coder"""
        try:
            Coder(topic)
            return "Content generated successfully and saved to file."
        except Exception as e:
            return f"Content generation failed: {str(e)}"

    def execute_tool_call(self, tool_call):
        """Execute a specific tool call"""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "execute_system_task":
            return self.execute_system_task(function_args["task_description"])
        elif function_name == "generate_image":
            return self.generate_image(function_args["prompt"])
        elif function_name == "write_content":
            return self.write_content(function_args["topic"])
        else:
            return "Unknown function called."

    def process_message(self, user_input):
        """Process user message with OpenAI tool calling"""
        try:
            # Add conversation to database
            conversation_id = self.db.add_conversation(user_input)
            
            # Get conversation history
            messages = self.db.get_conversation_history(limit=20)
            
            # Get real-time information
            time_info = self.get_real_time_info()
            
            # Prepare messages for API call
            api_messages = [
                {"role": "system", "content": self.system_instructions},
                {"role": "system", "content": f"Current time info: {time_info}"}
            ] + messages + [{"role": "user", "content": user_input}]
            
            # First API call to check for tool usage
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=api_messages,
                tools=self.tools,
                tool_choice="auto",
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9
            )
            
            response_message = response.choices[0].message
            
            # Handle tool calls
            if response_message.tool_calls:
                # Execute tool calls
                tool_results = []
                for tool_call in response_message.tool_calls:
                    result = self.execute_tool_call(tool_call)
                    tool_results.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "content": result
                    })
                
                # Add tool call messages to conversation
                api_messages.append({
                    "role": "assistant",
                    "content": response_message.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in response_message.tool_calls
                    ]
                })
                
                # Add tool results
                api_messages.extend(tool_results)
                
                # Get final response after tool execution
                final_response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=api_messages,
                    max_tokens=1024,
                    temperature=0.7,
                    top_p=0.9
                )
                
                answer = final_response.choices[0].message.content.strip()
            else:
                # No tools needed, use direct response
                answer = response_message.content.strip()
            
            # Update database with response
            self.db.update_assistant_response(conversation_id, answer)
            return answer
            
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            if 'conversation_id' in locals():
                self.db.update_assistant_response(conversation_id, error_msg)
            return error_msg

    def search_messages(self, keyword):
        """Search conversation history"""
        return self.db.search_conversations(keyword)

    def export_chat_history(self, format='csv', start_date=None, end_date=None):
        """Export conversation history"""
        return self.db.export_conversations(format, start_date, end_date)

def chat_with_assistant(prompt):
    """Standalone chat function for testing"""
    assistant = FALCONAssistant()
    response = assistant.process_message(prompt)
    print(response)
    return response

if __name__ == "__main__":
    assistant = FALCONAssistant()
    
    print("FALCON Assistant Ready!")
    print("Type 'exit' to quit")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Goodbye!")
            break
        
        response = assistant.process_message(user_input)
        print(f"FALCON: {response}")