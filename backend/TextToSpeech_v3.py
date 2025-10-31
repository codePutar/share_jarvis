import pyttsx3
import threading
import time

class HumanLikeTTS:
    def __init__(self, voice_type="male", rate=190, volume=1.0):
        self.engine = pyttsx3.init('sapi5')
        self.voices = self.engine.getProperty('voices')

        # Select Male or Female voice
        if voice_type.lower() == "male":
            self.engine.setProperty('voice', self.voices[1].id)  # Male voice
        else:
            self.engine.setProperty('voice', self.voices[0].id)  # Female voice

        self.engine.setProperty('rate', rate)  # Adjust speaking speed
        self.engine.setProperty('volume', volume)  # Adjust volume

    def speak(self, text):
        """Speak in a background thread for smooth execution."""
        threading.Thread(target=self._speak_thread, args=(text,)).start()

    def _speak_thread(self, text):
        """Internal function to process and speak text naturally."""
        try:
            sentences = text.split('. ')  
            for sentence in sentences:
                if "!" in sentence:  
                    self.engine.setProperty('rate', 190)
                elif "?" in sentence:  
                    self.engine.setProperty('rate', 175)
                else:
                    self.engine.setProperty('rate', 170)

                self.engine.say(sentence)
                self.engine.runAndWait()
                time.sleep(0.3)  
        except Exception as e:
            print(f"Speech Error: {e}")

def speaker(query):
    speaker = HumanLikeTTS(voice_type="male", rate=180, volume=2.0)
    speaker.speak(query)

if __name__ == "__main__":
    
    
    speaker("Hey Ashutosh! How's your day going? I hope you are doing great.")
    time.sleep(2)
    speaker("Let me know if you need any help. I'm always here for you.")
