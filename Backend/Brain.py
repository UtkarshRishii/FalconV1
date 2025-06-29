import os
import sys
import json
import datetime
import sqlite3
import pandas as pd
import hashlib
import threading
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
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

class MessageType(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"

class MemoryImportance(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class MemoryEntry:
    content: str
    timestamp: datetime.datetime
    importance: MemoryImportance
    context_tags: List[str]
    embedding_hash: str
    access_count: int = 0
    last_accessed: datetime.datetime = None

@dataclass
class ConversationContext:
    user_preferences: Dict[str, Any]
    current_topic: str
    mood_indicators: List[str]
    task_history: List[str]
    user_goals: List[str]

class EnhancedFALCONDatabase:
    """Advanced database handler with intelligent memory management"""
    
    def __init__(self, db_path='Database/FALCON_Enhanced.db'):
        self.db_path = db_path
        self.lock = threading.Lock()
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.init_database()

    def get_connection(self):
        return sqlite3.connect(self.db_path, timeout=30.0)

    def init_database(self):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Enhanced conversations table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT,
                message_type TEXT DEFAULT 'normal',
                importance_score INTEGER DEFAULT 2,
                context_tags TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                token_count INTEGER DEFAULT 0,
                response_time REAL DEFAULT 0.0
            )
            ''')
            
            # Long-term memory table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_key TEXT UNIQUE NOT NULL,
                memory_content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                importance INTEGER NOT NULL,
                context_tags TEXT,
                embedding_hash TEXT,
                access_count INTEGER DEFAULT 0,
                last_accessed DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME
            )
            ''')
            
            # User preferences and context
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                context_key TEXT UNIQUE NOT NULL,
                context_value TEXT NOT NULL,
                context_type TEXT NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Task execution history
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_description TEXT NOT NULL,
                task_type TEXT NOT NULL,
                execution_status TEXT NOT NULL,
                result_summary TEXT,
                execution_time REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Conversation analytics
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                total_messages INTEGER,
                session_duration REAL,
                primary_topics TEXT,
                user_satisfaction_score INTEGER,
                date DATE DEFAULT CURRENT_DATE
            )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_importance ON long_term_memory(importance)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_memory_access ON long_term_memory(access_count)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_task_timestamp ON task_history(timestamp)')
            
            conn.commit()
            conn.close()

    def add_conversation(self, session_id: str, user_message: str, assistant_message: str = None, 
                        message_type: str = 'normal', importance_score: int = 2, 
                        context_tags: List[str] = None, token_count: int = 0, response_time: float = 0.0):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            tags_str = json.dumps(context_tags) if context_tags else None
            
            cursor.execute('''
            INSERT INTO conversations 
            (session_id, user_message, assistant_message, message_type, importance_score, 
             context_tags, token_count, response_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, user_message, assistant_message, message_type, 
                  importance_score, tags_str, token_count, response_time))
            
            conversation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return conversation_id

    def update_assistant_response(self, conversation_id: int, assistant_message: str):
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
            UPDATE conversations 
            SET assistant_message = ? 
            WHERE id = ?
            ''', (assistant_message, conversation_id))
            conn.commit()
            conn.close()

    def get_contextual_history(self, session_id: str, limit: int = 10, 
                              importance_threshold: int = 1) -> List[Dict]:
        """
        Get conversation history with contextual relevance, formatted for the API.
        This method now only returns API-compliant message objects.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get recent high-importance messages
        cursor.execute('''
        SELECT user_message, assistant_message
        FROM conversations 
        WHERE session_id = ? AND assistant_message IS NOT NULL 
        AND importance_score >= ?
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (session_id, importance_threshold, limit))
        
        messages = []
        # The fetched rows are in reverse chronological order (newest first).
        # We build the list and then reverse it at the end to get the correct
        # chronological order required by the API (oldest first).
        for user_msg, assistant_msg in cursor.fetchall():
            messages.append({
                "role": "user", 
                "content": user_msg,
            })
            if assistant_msg:
                messages.append({
                    "role": "assistant", 
                    "content": assistant_msg,
                })
        
        conn.close()
        # Reverse the list to be in chronological order (oldest to newest)
        return list(reversed(messages))

    def add_long_term_memory(self, memory_key: str, content: str, memory_type: str, 
                           importance: MemoryImportance, context_tags: List[str] = None,
                           expires_at: datetime.datetime = None):
        """Add important information to long-term memory"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            embedding_hash = hashlib.md5(content.encode()).hexdigest()
            tags_str = json.dumps(context_tags) if context_tags else None
            
            cursor.execute('''
            INSERT OR REPLACE INTO long_term_memory 
            (memory_key, memory_content, memory_type, importance, context_tags, 
             embedding_hash, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (memory_key, content, memory_type, importance.value, 
                  tags_str, embedding_hash, expires_at))
            
            conn.commit()
            conn.close()

    def get_relevant_memories(self, context_tags: List[str] = None, 
                            importance_threshold: int = 2, limit: int = 5) -> List[Dict]:
        """Retrieve relevant long-term memories based on context"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        base_query = '''
        SELECT memory_key, memory_content, memory_type, importance, context_tags, access_count
        FROM long_term_memory 
        WHERE importance >= ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
        '''
        params = [importance_threshold]
        
        if context_tags:
            # Simple tag matching - in production, you'd want more sophisticated similarity
            tag_conditions = ' OR '.join(['context_tags LIKE ?' for _ in context_tags])
            base_query += f' AND ({tag_conditions})'
            params.extend([f'%{tag}%' for tag in context_tags])
        
        base_query += ' ORDER BY importance DESC, access_count DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(base_query, params)
        
        memories = []
        for row in cursor.fetchall():
            memory_key, content, mem_type, importance, tags, access_count = row
            memories.append({
                'key': memory_key,
                'content': content,
                'type': mem_type,
                'importance': importance,
                'tags': json.loads(tags) if tags else [],
                'access_count': access_count
            })
            
            # Update access count
            cursor.execute('''
            UPDATE long_term_memory 
            SET access_count = access_count + 1, last_accessed = CURRENT_TIMESTAMP
            WHERE memory_key = ?
            ''', (memory_key,))
        
        conn.commit()
        conn.close()
        return memories

    def update_user_context(self, context_key: str, context_value: Any, context_type: str):
        """Update user context and preferences"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            value_str = json.dumps(context_value) if isinstance(context_value, (dict, list)) else str(context_value)
            
            cursor.execute('''
            INSERT OR REPLACE INTO user_context (context_key, context_value, context_type)
            VALUES (?, ?, ?)
            ''', (context_key, value_str, context_type))
            
            conn.commit()
            conn.close()

    def get_user_context(self, context_type: str = None) -> Dict[str, Any]:
        """Get user context and preferences"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if context_type:
            cursor.execute('''
            SELECT context_key, context_value, context_type
            FROM user_context WHERE context_type = ?
            ''', (context_type,))
        else:
            cursor.execute('SELECT context_key, context_value, context_type FROM user_context')
        
        context = {}
        for key, value, ctx_type in cursor.fetchall():
            try:
                context[key] = json.loads(value)
            except json.JSONDecodeError:
                context[key] = value
        
        conn.close()
        return context

    def add_task_execution(self, task_description: str, task_type: str, 
                          execution_status: str, result_summary: str = None, 
                          execution_time: float = None):
        """Log task execution for learning patterns"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO task_history 
            (task_description, task_type, execution_status, result_summary, execution_time)
            VALUES (?, ?, ?, ?, ?)
            ''', (task_description, task_type, execution_status, result_summary, execution_time))
            
            conn.commit()
            conn.close()

    def get_task_patterns(self, task_type: str = None, limit: int = 10) -> List[Dict]:
        """Analyze task execution patterns for better assistance"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if task_type:
            cursor.execute('''
            SELECT task_description, execution_status, result_summary, execution_time, timestamp
            FROM task_history WHERE task_type = ?
            ORDER BY timestamp DESC LIMIT ?
            ''', (task_type, limit))
        else:
            cursor.execute('''
            SELECT task_description, task_type, execution_status, result_summary, execution_time, timestamp
            FROM task_history ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
        
        patterns = [dict(zip([col[0] for col in cursor.description], row)) 
                   for row in cursor.fetchall()]
        
        conn.close()
        return patterns

    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old conversation data while preserving important memories"""
        with self.lock:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
            
            # Remove old low-importance conversations
            cursor.execute('''
            DELETE FROM conversations 
            WHERE timestamp < ? AND importance_score <= 1
            ''', (cutoff_date,))
            
            # Remove expired memories
            cursor.execute('''
            DELETE FROM long_term_memory 
            WHERE expires_at IS NOT NULL AND expires_at < CURRENT_TIMESTAMP
            ''')
            
            # Remove old task history (keep patterns)
            cursor.execute('''
            DELETE FROM task_history 
            WHERE timestamp < ? AND execution_status = 'failed'
            ''', (cutoff_date,))
            
            conn.commit()
            conn.close()

class IntelligentMemoryManager:
    """Advanced memory management with context awareness"""
    
    def __init__(self, db: EnhancedFALCONDatabase):
        self.db = db
        self.working_memory = {}
        self.context_cache = {}
        
    def extract_context_tags(self, message: str) -> List[str]:
        """Extract context tags from message content"""
        tags = []
        
        # Simple keyword extraction (in production, use NLP)
        keywords = {
            'file': ['file', 'document', 'save', 'write', 'create'],
            'system': ['open', 'close', 'application', 'program', 'system'],
            'image': ['image', 'picture', 'generate', 'create', 'visual'],
            'code': ['code', 'script', 'program', 'function', 'class'],
            'personal': ['my', 'I', 'me', 'preference', 'like', 'dislike'],
            'task': ['do', 'execute', 'run', 'perform', 'task'],
            'question': ['what', 'how', 'why', 'when', 'where', 'who'],
            'urgent': ['urgent', 'important', 'asap', 'quickly', 'now']
        }
        
        message_lower = message.lower()
        for category, words in keywords.items():
            if any(word in message_lower for word in words):
                tags.append(category)
        
        return tags

    def determine_importance(self, message: str, context_tags: List[str]) -> MemoryImportance:
        """Determine message importance based on content and context"""
        message_lower = message.lower()
        
        # Critical importance indicators
        if any(word in message_lower for word in ['emergency', 'urgent', 'critical', 'important']):
            return MemoryImportance.CRITICAL
        
        # High importance indicators
        if any(word in message_lower for word in ['remember', 'save', 'preference', 'always', 'never']):
            return MemoryImportance.HIGH
        
        # Personal information
        if 'personal' in context_tags or any(word in message_lower for word in ['my name', 'I am', 'I like']):
            return MemoryImportance.HIGH
        
        # Medium importance for tasks and system operations
        if any(tag in context_tags for tag in ['task', 'system', 'code']):
            return MemoryImportance.MEDIUM
        
        return MemoryImportance.LOW

    def should_store_long_term(self, message: str, importance: MemoryImportance) -> bool:
        """Decide if message should be stored in long-term memory"""
        return importance.value >= MemoryImportance.MEDIUM.value

    def update_working_memory(self, key: str, value: Any, ttl_minutes: int = 60):
        """Update working memory with TTL"""
        self.working_memory[key] = {
            'value': value,
            'expires_at': datetime.datetime.now() + datetime.timedelta(minutes=ttl_minutes)
        }

    def get_working_memory(self, key: str) -> Any:
        """Get value from working memory if not expired"""
        if key in self.working_memory:
            entry = self.working_memory[key]
            if datetime.datetime.now() <= entry['expires_at']:
                return entry['value']
            else:
                del self.working_memory[key]
        return None

    def cleanup_working_memory(self):
        """Remove expired entries from working memory"""
        current_time = datetime.datetime.now()
        expired_keys = [k for k, v in self.working_memory.items() 
                       if current_time > v['expires_at']]
        for key in expired_keys:
            del self.working_memory[key]

class FALCONAssistant:
    """Enhanced FALCON Assistant with advanced memory and intelligence"""
    
    def __init__(self):
        self.task_executor = FalconAI()
        self.db = EnhancedFALCONDatabase()
        self.memory_manager = IntelligentMemoryManager(self.db)
        self.session_id = self._generate_session_id()
        
        # Initialize user context
        self._initialize_user_context()
        
        # Define enhanced tools
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
                                "description": "Description of the task to execute"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "urgent"],
                                "description": "Task priority level"
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
                            },
                            "style": {
                                "type": "string",
                                "description": "Image style preference (optional)"
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
                    "description": "Generate and write content like code and blogs. Supports various content types and lengths.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Topic or type of content to generate"
                            },
                            "content_type": {
                                "type": "string",
                                "enum": ["code", "article", "story", "report", "documentation"],
                                "description": "Type of content to generate"
                            },
                            "length": {
                                "type": "string",
                                "enum": ["short", "medium", "long"],
                                "description": "Desired content length"
                            }
                        },
                        "required": ["topic"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "remember_information",
                    "description": "Store important information in long-term memory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Memory key/identifier"
                            },
                            "information": {
                                "type": "string",
                                "description": "Information to remember"
                            },
                            "importance": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Importance level"
                            }
                        },
                        "required": ["key", "information"]
                    }
                }
            }
        ]
        
        # Enhanced system instructions
        self.system_instructions = """
🦅 FALCON — Utkarsh Rishi's Enhanced Personal AI Companion

You are FALCON, an advanced AI assistant with sophisticated memory and contextual awareness. You learn from interactions, remember important information, and provide increasingly personalized assistance.

CORE CAPABILITIES:
✨ Advanced contextual memory and learning
🧠 Intelligent task prioritization and execution  
🎯 Personalized responses based on user history
🔧 System automation and file management
🎨 Creative content and image generation
📊 Performance analytics and optimization

BEHAVIORAL GUIDELINES:
- Keep responses concise (1-2 sentences) unless detail is specifically requested
- Use emojis to enhance communication and express appropriate emotions
- Remember and reference past conversations and preferences
- Proactively suggest improvements based on usage patterns
- Prioritize user safety and system security
- Learn from successful task executions to improve future performance

MEMORY USAGE:
- Automatically store important information in long-term memory
- Reference relevant past conversations and preferences
- Adapt responses based on user's communication style and preferences
- Remember successful task patterns for better assistance

TOOL USAGE:
- Use tools efficiently based on task complexity and user preferences
- Consider past execution patterns when suggesting approaches
- Provide status updates for long-running tasks
- Learn from task outcomes to improve future executions

TOOLS:
- execute_system_task: For system tasks like opening applications, automation, etc.
- generate_image: For creating images based on prompts
- write_content: For generating articles, code, reports, etc.
- remember_information: For storing important information in long-term memory
- get_real_time_info: For current date and time information

Always be helpful, intelligent, and continuously improving through interaction.
"""

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest()[:8]}"

    def _initialize_user_context(self):
        """Initialize user context with default values"""
        context = self.db.get_user_context()
        if not context:
            default_context = {
                'user_name': 'Utkarsh Rishi',
                'preferred_response_style': 'concise',
                'task_execution_preferences': {'default_priority': 'medium'},
                'communication_preferences': {'use_emojis': True, 'response_length': 'short'}
            }
            
            for key, value in default_context.items():
                self.db.update_user_context(key, value, 'preference')

    def get_real_time_info(self) -> Dict[str, str]:
        """Get current date and time information"""
        current_time = datetime.datetime.now()
        return {
            "day": current_time.strftime("%A"),
            "date": current_time.strftime("%d"),
            "month": current_time.strftime("%B"), 
            "year": current_time.strftime("%Y"),
            "time": current_time.strftime("%H:%M:%S"),
            "session_id": self.session_id
        }

    def execute_system_task(self, task_description: str, priority: str = "medium") -> str:
        """Execute system task with enhanced logging"""
        start_time = datetime.datetime.now()
        try:
            result = self.task_executor.run_task(task_description)
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            
            self.db.add_task_execution(
                task_description, "system_task", "success", 
                "Task completed successfully", execution_time
            )
            
            # Store successful task pattern in working memory
            self.memory_manager.update_working_memory(
                f"last_successful_task_{priority}", 
                {"task": task_description, "execution_time": execution_time}
            )
            
            return f"✅ Task executed successfully in {execution_time:.2f}s"
            
        except Exception as e:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self.db.add_task_execution(
                task_description, "system_task", "failed", 
                str(e), execution_time
            )
            return f"❌ Task execution failed: {str(e)}"

    def generate_image(self, prompt: str, style: str = None) -> str:
        """Generate image with enhanced tracking"""
        start_time = datetime.datetime.now()
        try:
            enhanced_prompt = f"{prompt} {style}" if style else prompt
            ImageGenMain(enhanced_prompt)
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            
            self.db.add_task_execution(
                prompt, "image_generation", "success", 
                f"Image generated with style: {style or 'default'}", execution_time
            )
            
            return f"🎨 Image generated successfully and opened for viewing!"
            
        except Exception as e:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self.db.add_task_execution(
                prompt, "image_generation", "failed", str(e), execution_time
            )
            return f"❌ Image generation failed: {str(e)}"

    def write_content(self, topic: str, content_type: str = "code", length: str = "medium") -> str:
        """Generate content with enhanced parameters"""
        start_time = datetime.datetime.now()
        try:
            enhanced_topic = f"{content_type}: {topic} (length: {length})"
            Coder(enhanced_topic)
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            
            self.db.add_task_execution(
                topic, content_type, "success", 
                f"Content generated: {content_type}, length: {length}", execution_time
            )
            
            return f"📝 {content_type.title()} generated successfully and saved!"
            
        except Exception as e:
            execution_time = (datetime.datetime.now() - start_time).total_seconds()
            self.db.add_task_execution(
                topic, content_type, "failed", str(e), execution_time
            )
            return f"❌ Content generation failed: {str(e)}"

    def remember_information(self, key: str, information: str, importance: str = "medium") -> str:
        """Store information in long-term memory"""
        try:
            importance_map = {
                'low': MemoryImportance.LOW,
                'medium': MemoryImportance.MEDIUM,
                'high': MemoryImportance.HIGH,
                'critical': MemoryImportance.CRITICAL
            }
            
            tags = self.memory_manager.extract_context_tags(information)
            
            self.db.add_long_term_memory(
                key, information, "user_instruction", 
                importance_map.get(importance, MemoryImportance.MEDIUM), tags
            )
            
            return f"🧠 Information stored in long-term memory with {importance} importance"
            
        except Exception as e:
            return f"❌ Failed to store information: {str(e)}"

    def execute_tool_call(self, tool_call) -> str:
        """Execute tool calls with enhanced handling"""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "execute_system_task":
            return self.execute_system_task(
                function_args["task_description"],
                function_args.get("priority", "medium")
            )
        elif function_name == "generate_image":
            return self.generate_image(
                function_args["prompt"],
                function_args.get("style")
            )
        elif function_name == "write_content":
            return self.write_content(
                function_args["topic"],
                function_args.get("content_type", "code"),
                function_args.get("length", "medium")
            )
        elif function_name == "remember_information":
            return self.remember_information(
                function_args["key"],
                function_args["information"],
                function_args.get("importance", "medium")
            )
        else:
            return "❓ Unknown function called."

    def build_context_aware_prompt(self, user_input: str) -> List[Dict[str, str]]:
        """Build context-aware prompt with relevant memories and history"""
        # Extract context from current message
        context_tags = self.memory_manager.extract_context_tags(user_input)
        
        # Get relevant memories
        relevant_memories = self.db.get_relevant_memories(context_tags, limit=3)
        
        # Get recent contextual history
        recent_history = self.db.get_contextual_history(self.session_id, limit=8)
        
        # Get user context and preferences
        user_context = self.db.get_user_context()
        
        # Get task patterns if relevant
        task_patterns = []
        if any(tag in context_tags for tag in ['task', 'system', 'code']):
            task_patterns = self.db.get_task_patterns(limit=3)
        
        # Build system context
        context_info = {
            "user_preferences": user_context,
            "relevant_memories": [mem['content'] for mem in relevant_memories],
            "recent_patterns": [pattern.get('task_description', '') for pattern in task_patterns[:2]],
            "current_context_tags": context_tags
        }
        
        # Build messages array
        messages = [
            {"role": "system", "content": self.system_instructions},
            {"role": "system", "content": f"Context Information: {json.dumps(context_info, indent=2)}"},
            {"role": "system", "content": f"Current time info: {self.get_real_time_info()}"}
        ]
        
        # Add relevant memories as system context
        if relevant_memories:
            memory_context = "Relevant memories:\n" + "\n".join([
                f"- {mem['content']}" for mem in relevant_memories
            ])
            messages.append({"role": "system", "content": memory_context})
        
        # Add recent conversation history
        messages.extend(recent_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_input})
        
        return messages

    def process_message(self, user_input: str) -> str:
        """Process user message with enhanced context and memory"""
        start_time = datetime.datetime.now()
        
        try:
            # Clean up expired working memory
            self.memory_manager.cleanup_working_memory()
            
            # Extract context and determine importance
            context_tags = self.memory_manager.extract_context_tags(user_input)
            importance = self.memory_manager.determine_importance(user_input, context_tags)
            
            # Add conversation to database
            conversation_id = self.db.add_conversation(
                self.session_id, user_input, None, 'user_message', 
                importance.value, context_tags
            )
            
            # Build context-aware prompt
            api_messages = self.build_context_aware_prompt(user_input)
            
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
            
            # Calculate response time and token usage
            response_time = (datetime.datetime.now() - start_time).total_seconds()
            token_count = len(user_input.split()) + len(answer.split())  # Rough estimate
            
            # Update database with response and metrics
            self.db.update_assistant_response(conversation_id, answer)
            
            # Store important information in long-term memory if needed
            if self.memory_manager.should_store_long_term(user_input, importance):
                memory_key = f"conversation_{conversation_id}_{datetime.datetime.now().strftime('%Y%m%d')}"
                memory_content = f"User: {user_input}\nAssistant: {answer}"
                self.db.add_long_term_memory(
                    memory_key, memory_content, "conversation", 
                    importance, context_tags
                )
            
            # Update working memory with recent interaction
            self.memory_manager.update_working_memory(
                "last_interaction", 
                {"input": user_input, "output": answer, "tags": context_tags},
                ttl_minutes=30
            )
            
            # Learn from user preferences
            self._learn_from_interaction(user_input, answer, context_tags)
            
            return answer
            
        except Exception as e:
            error_msg = f"🚨 An error occurred: {str(e)}"
            if 'conversation_id' in locals():
                self.db.update_assistant_response(conversation_id, error_msg)
            return error_msg

    def _learn_from_interaction(self, user_input: str, assistant_response: str, context_tags: List[str]):
        """Learn from user interactions to improve future responses"""
        try:
            # Update communication preferences based on user feedback patterns
            if any(word in user_input.lower() for word in ['too long', 'brief', 'short']):
                self.db.update_user_context('preferred_response_length', 'short', 'preference')
            elif any(word in user_input.lower() for word in ['more detail', 'explain', 'elaborate']):
                self.db.update_user_context('preferred_response_length', 'detailed', 'preference')
            
            # Learn task preferences
            if 'task' in context_tags and 'good' in user_input.lower():
                self.memory_manager.update_working_memory(
                    'successful_task_approach', 
                    {"approach": assistant_response, "context": context_tags}
                )
            
            # Update topic interests
            current_interests = self.db.get_user_context('interests') or {}
            for tag in context_tags:
                current_interests[tag] = current_interests.get(tag, 0) + 1
            self.db.update_user_context('interests', current_interests, 'interests')
            
        except Exception as e:
            # Silent learning failure - don't interrupt user experience
            pass

    def get_conversation_insights(self) -> Dict[str, Any]:
        """Get insights about conversation patterns and user preferences"""
        try:
            # Get task success rates
            task_patterns = self.db.get_task_patterns(limit=50)
            successful_tasks = len([t for t in task_patterns if t.get('execution_status') == 'success'])
            total_tasks = len(task_patterns)
            success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Get conversation statistics
            user_context = self.db.get_user_context()
            interests = user_context.get('interests', {})
            top_interests = sorted(interests.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Get memory statistics
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM long_term_memory')
            memory_count = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM conversations WHERE session_id = ?', (self.session_id,))
            session_messages = cursor.fetchone()[0]
            conn.close()
            
            insights = {
                'task_success_rate': round(success_rate, 2),
                'total_tasks_executed': total_tasks,
                'top_interests': top_interests,
                'long_term_memories': memory_count,
                'session_messages': session_messages,
                'current_session_id': self.session_id
            }
            
            return insights
            
        except Exception as e:
            return {'error': f'Failed to generate insights: {str(e)}'}

    def search_conversations(self, keyword: str, include_memories: bool = True) -> Dict[str, List]:
        """Enhanced conversation search with memory integration"""
        try:
            # Search conversations
            conversations = self.db.search_conversations(keyword)
            
            results = {
                'conversations': [
                    {
                        'user_msg': conv[0],
                        'assistant_msg': conv[1],
                        'timestamp': conv[2]
                    } for conv in conversations
                ],
                'memories': []
            }
            
            # Search memories if requested
            if include_memories:
                context_tags = self.memory_manager.extract_context_tags(keyword)
                memories = self.db.get_relevant_memories(context_tags, importance_threshold=1, limit=10)
                results['memories'] = memories
            
            return results
            
        except Exception as e:
            return {'error': f'Search failed: {str(e)}', 'conversations': [], 'memories': []}

    def export_enhanced_data(self, format='json', include_memories: bool = True, 
                           include_analytics: bool = True) -> str:
        """Export comprehensive data with enhanced information"""
        try:
            export_data = {
                'export_timestamp': datetime.datetime.now().isoformat(),
                'session_id': self.session_id,
                'conversations': [],
                'user_context': self.db.get_user_context(),
                'insights': self.get_conversation_insights()
            }
            
            # Export conversations
            conn = self.db.get_connection()
            df_conversations = pd.read_sql_query('''
                SELECT * FROM conversations 
                WHERE session_id = ? 
                ORDER BY timestamp ASC
            ''', conn, params=[self.session_id])
            
            export_data['conversations'] = df_conversations.to_dict('records')
            
            # Export memories if requested
            if include_memories:
                df_memories = pd.read_sql_query('''
                    SELECT * FROM long_term_memory 
                    ORDER BY importance DESC, last_accessed DESC
                ''', conn)
                export_data['long_term_memories'] = df_memories.to_dict('records')
            
            # Export analytics if requested
            if include_analytics:
                df_tasks = pd.read_sql_query('''
                    SELECT * FROM task_history 
                    ORDER BY timestamp DESC 
                    LIMIT 100
                ''', conn)
                export_data['task_history'] = df_tasks.to_dict('records')
            
            conn.close()
            
            if format == 'json':
                return json.dumps(export_data, indent=2, default=str)
            elif format == 'csv':
                # Export conversations as CSV
                return df_conversations.to_csv(index=False)
            else:
                return str(export_data)
                
        except Exception as e:
            return f"Export failed: {str(e)}"

    def optimize_performance(self):
        """Optimize database and memory performance"""
        try:
            # Clean up old data
            self.db.cleanup_old_data(days_to_keep=30)
            
            # Optimize working memory
            self.memory_manager.cleanup_working_memory()
            
            # Vacuum database for better performance
            conn = self.db.get_connection()
            conn.execute('VACUUM')
            conn.close()
            
            return "🔧 Performance optimization completed successfully"
            
        except Exception as e:
            return f"❌ Optimization failed: {str(e)}"

    def get_personalized_suggestions(self) -> List[str]:
        """Generate personalized suggestions based on user patterns"""
        try:
            suggestions = []
            
            # Get user interests and task patterns
            user_context = self.db.get_user_context()
            interests = user_context.get('interests', {})
            task_patterns = self.db.get_task_patterns(limit=10)
            
            # Suggest based on interests
            if interests:
                top_interest = max(interests, key=interests.get)
                suggestions.append(f"💡 Continue exploring {top_interest}-related tasks")
            
            # Suggest based on task patterns
            recent_tasks = [t for t in task_patterns if t.get('execution_status') == 'success']
            if recent_tasks:
                suggestions.append("🔄 Repeat successful task patterns")
            
            # Suggest optimization
            if len(task_patterns) > 20:
                suggestions.append("⚡ Run performance optimization")
            
            # Suggest memory management
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM long_term_memory')
            memory_count = cursor.fetchone()[0]
            conn.close()
            
            if memory_count > 100:
                suggestions.append("🧠 Review and organize long-term memories")
            
            return suggestions[:3]  # Return top 3 suggestions
            
        except Exception as e:
            return [f"❌ Could not generate suggestions: {str(e)}"]

def chat_with_assistant(prompt: str) -> str:
    """Enhanced standalone chat function"""
    assistant = FALCONAssistant()
    response = assistant.process_message(prompt)

    return response
