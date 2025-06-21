import speech_recognition as sr

def recognize_speech(callback=None):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language='en-IN')
        print(f"🗣️  Mr. Rishi : {text}")
        if callback:
            callback(text)
        return text
    except sr.UnknownValueError:
        print("🤖 Could not understand audio.")
    except sr.RequestError as e:
        print(f"🔌 Could not request results; {e}")