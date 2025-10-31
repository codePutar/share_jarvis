import pygame
from pygame import mixer
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# ✅ Force SDL to use DirectSound for stable initialization
os.environ["SDL_AUDIODRIVER"] = "directsound"

# Load environment variables from .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# ✅ Asynchronous function to convert text to an audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3"

    if os.path.exists(file_path):
        os.remove(file_path)
    
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+10Hz', rate='+2%')
    await communicate.save(file_path)

# ✅ Function to play text-to-speech (TTS)
def TTS(Text, func=lambda r=None: True):
    try:
        # Convert text to an audio file asynchronously
        asyncio.run(TextToAudioFile(Text))

        # ✅ Initialize Pygame Mixer Properly (with error handling)
        if not pygame.mixer.get_init():  # Check if already initialized
            mixer.init(frequency=48000, size=-16, channels=2, buffer=1024)

        # ✅ Load the generated speech file into pygame mixer
        pygame.mixer.music.load(r"Data\speech.mp3")
        pygame.mixer.music.play()

        # ✅ Loop until the audio is done playing
        while pygame.mixer.music.get_busy():
            if func() == False:
                break
            pygame.time.Clock().tick(10)

        return True

    except Exception as e:
        print(f"❌ Error in TTS: {e}")
    
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"❌ Error in cleanup: {e}")

# ✅ Function to handle long text with a response
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "Sir, please check the chat screen for more information.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, take a look at the chat screen for additional text."
    ]

    if len(Data) > 4 and len(Text) > 250:
        TTS(" ".join(Text.split(".")[0:2]) + "." + random.choice(responses), func)
    else:
        TTS(Text, func)

# ✅ Main execution loop
if __name__ == "__main__":
    while True:
        TextToSpeech(input("Enter the text: "))
