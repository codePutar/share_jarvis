import os
import pygame
from pygame import mixer

# Different audio drivers for testing
drivers = ["directsound", "waveout", "dsound", "winmm"]

for driver in drivers:
    os.environ["SDL_AUDIODRIVER"] = driver
    print(f"Trying SDL_AUDIODRIVER={driver}")

    try:
        pygame.mixer.quit()  # Quit previous attempts
        pygame.init()  # Reinitialize Pygame
        mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        if mixer.get_init():  # If mixer initializes successfully
            print(f"Mixer initialized successfully with {driver}! ")
            break  # Stop if it works
    except pygame.error as e:
        print(f"Failed with {driver}: {e}")

# Final Check
if mixer.get_init():
    print("Mixer is running successfully! ")
else:
    print("❌ All methods failed. Check system settings or reinstall Pygame.")
