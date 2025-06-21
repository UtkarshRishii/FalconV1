import pygame
import random
import asyncio
import edge_tts
import os
import re
import unicodedata
from dotenv import load_dotenv

load_dotenv()

def clean_text(text):
    """
    Thoroughly cleans text for speech synthesis by removing emojis and 
    normalizing special characters while preserving speech-relevant punctuation.
    
    Args:
        text (str): The input text to clean
    Returns:
        str: Speech-ready cleaned text
    """
    # First normalize unicode characters
    normalized_text = unicodedata.normalize('NFKD', text)
    
    # Remove emojis and other symbol characters
    cleaned_text = ''.join(
        char for char in normalized_text
        if not unicodedata.category(char).startswith('So') and  # Symbol, other
           not unicodedata.category(char).startswith('Cs') and  # Surrogate pairs
           not unicodedata.category(char).startswith('Co')      # Private use
    )
    
    # Keep only alphanumeric, spaces, and punctuation important for speech
    cleaned_text = re.sub(r'[^\w\s.,!?:;\'"-]', '', cleaned_text)
    
    # Normalize whitespace
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    return cleaned_text

async def text_to_audio_file(text):
    """
    Converts text to speech audio file using edge-tts.
    
    Args:
        text (str): Text to convert to speech
    """
    file_path = "Database/Audio/TTS.mp3"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Remove existing file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Get voice from environment or use default
    voice = os.environ.get('Voice')
    
    # Convert text to speech
    communicate = edge_tts.Communicate(text, voice, pitch='+0Hz', rate='+0%')
    await communicate.save(file_path)
    
    return file_path

def text_to_speech(text, callback_func=None):
    """
    Plays text as speech using pygame.
    
    Args:
        text (str): Text to speak
        callback_func: Optional function to call during playback that can 
                      return False to stop playback
    """
    if callback_func is None:
        callback_func = lambda r=None: True
        
    try:
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()

        # Generate the audio file
        audio_file = asyncio.run(text_to_audio_file(text))

        # Play the audio
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait while audio is playing
        while pygame.mixer.music.get_busy():
            if callback_func() is False:
                break
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Text-to-speech error: {e}")

    finally:
        # Clean up
        callback_func(False)
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
            
def SpeakFalcon(text, callback_func=None):
    """
    Smart text-to-speech function that handles long text appropriately.
    
    For long text, speaks only the beginning and notifies that the rest
    is available on screen.
    
    Args:
        text (str): Text to speak
        callback_func: Optional callback function
    """
    if callback_func is None:
        callback_func = lambda r=None: True
        
    # Clean the input text
    cleaned_text = clean_text(text)
    
    # For long text, speak only the beginning
    if len(cleaned_text) >= 1000:
        # Split by sentences
        sentences = re.split(r'(?<=[.!?])\s+', cleaned_text)
        
        # Speak first couple of sentences
        if len(sentences) > 2:
            shortened_text = ' '.join(sentences[:2])
            text_to_speech(shortened_text, callback_func)
        else:
            # If we don't have enough sentences, just speak what we have
            text_to_speech(cleaned_text, callback_func)
    else:
        # For shorter text, speak it all
        text_to_speech(cleaned_text, callback_func)