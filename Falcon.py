import eel
import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import backend modules
try:
    from Backend.Brain import FALCONAssistant
    from Backend.TTS import SpeakFalcon
except ImportError as e:
    print(f"Critical Import Error: {e}")
    sys.exit(1)
except Exception as ex:
    print(f"An unexpected error occurred during initial imports: {ex}")
    sys.exit(1)

# Initialize FALCON Assistant
try:
    print("Initializing FALCON Assistant...")
    assistant = FALCONAssistant()
    print("FALCON Assistant initialized successfully.")
except ValueError as ve:
    print(f"Configuration Error: {ve}")
    sys.exit(1)
except Exception as e:
    print(f"Error initializing FALCONAssistant: {e}")
    sys.exit(1)

# Verify web folder exists
web_folder = os.path.join(current_dir, 'web')
if not os.path.isdir(web_folder):
    print(f"Error: The 'web' folder ('{web_folder}') was not found.")
    sys.exit(1)
if not os.path.isfile(os.path.join(web_folder, 'index.html')):
    print(f"Error: 'index.html' not found in the 'web' folder ('{web_folder}').")
    sys.exit(1)

# Initialize Eel
eel.init(web_folder)

@eel.expose
def process_user_query(user_query_text: str):
    """
    Process user query with FALCONAssistant and return response
    """
    print(f"User Query: {user_query_text}")
    
    if not user_query_text or user_query_text.strip() == "":
        no_input_response = "I didn't quite catch that. Could you say it again?"
        return {'response': no_input_response, 'should_speak': True}

    try:
        ai_response_text = assistant.process_message(user_query_text)
        print(f"FALCON Response: {ai_response_text}")
        
        # Determine if response should be spoken
        should_speak = True
        error_indicators = ["error", "apologize", "couldn't formulate", "issue processing"]
        if not ai_response_text or any(indicator in ai_response_text.lower() for indicator in error_indicators):
            should_speak = False

        return {'response': ai_response_text, 'should_speak': should_speak}
    
    except Exception as e:
        print(f"Error processing query: {str(e)}")
        error_response = "I encountered an issue while processing your request. Please try again."
        return {'response': error_response, 'should_speak': True}

@eel.expose
def request_tts(text_to_speak: str):
    """
    Handle text-to-speech requests from UI
    """
    print(f"TTS Request: {text_to_speak}")
    
    if text_to_speak and isinstance(text_to_speak, str) and text_to_speak.strip():
        try:
            SpeakFalcon(text_to_speak)
            print("TTS Playback initiated.")
        except Exception as e:
            print(f"Error during TTS: {e}")
    else:
        print("TTS Request: No valid text to speak.")

@eel.expose
def get_conversation_history():
    """
    Get conversation history from database
    """
    try:
        history = assistant.db.get_conversation_history(limit=50)
        return history
    except Exception as e:
        print(f"Error getting conversation history: {e}")
        return []

@eel.expose
def search_conversations(keyword: str):
    """
    Search conversations by keyword
    """
    try:
        results = assistant.search_messages(keyword)
        return results
    except Exception as e:
        print(f"Error searching conversations: {e}")
        return []

@eel.expose
def export_chat_history(format_type: str = 'csv'):
    """
    Export chat history in specified format
    """
    try:
        exported_data = assistant.export_chat_history(format_type)
        return exported_data
    except Exception as e:
        print(f"Error exporting chat history: {e}")
        return None

if __name__ == '__main__':
    print("Starting FALCON UI application...")
    print("Access the UI at http://localhost:8000")
    
    try:
        eel.start('index.html', size=(990, 540), block=True, host='localhost', port=8000)
    except (OSError, IOError) as e:
        print(f"Could not start Eel: {e}")
        print("Ensure port 8000 is not already in use.")
    except Exception as e:
        print(f"An unexpected error occurred while starting Eel: {e}")
    finally:
        print("FALCON UI application has closed.")