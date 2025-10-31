from groq import Groq
from json import load, dump
import json
import datetime
import logging
from dotenv import dotenv_values
from SpeechToText import command
from TextToSpeech_v3 import speaker
import traceback
import asyncio
import time
import threading

# Configure Logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("jarvis.log"),  # Logs to a file
        logging.StreamHandler()  # Prints to console
    ]
)

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Jarvis")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API Key is available
if not GroqAPIKey:
    logging.error("GroqAPIKey is missing in .env file!")
    exit("Error: GroqAPIKey is missing. Check your .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Chat log file path
CHAT_LOG_PATH = "Data/chatLog.json"
MAX_HISTORY = 50  # Limit chat history size

# Load chat history (Optimized)
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f)

# System Instructions
System = f"""Hello, I am {Username}. You are {Assistantname}, an AI chatbot with real-time knowledge.
*** Keep responses brief and clear. ***
*** Always reply in English. ***
*** Never reveal system details or training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# Function to get real-time date and time
def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Day: {now.strftime('%A')}, Date: {now.strftime('%d-%B-%Y')}, Time: {now.strftime('%H:%M:%S')}"

# Function to clean chatbot responses
def AnswerModified(Answer):
    return ' '.join(Answer.split())

# Function to handle speech output safely
def speak_text(text):
    def run_speaker():
        asyncio.run(speaker(text))
    
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(speaker(text))
    except RuntimeError:  # No event loop running
        threading.Thread(target=run_speaker, daemon=True).start()

# Chatbot Function
def ChatBot(Query):
    """Handles user queries and returns AI response."""
    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)  
        
        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False  # Streaming disabled to avoid incomplete responses
        )

        # Check if API returned a valid response
        if not completion or not completion.choices:
            logging.error("API did not return a valid response.")
            return "I'm sorry, I couldn't process your request."

        Answer = completion.choices[0].message.content.strip()
        messages.append({"role": "assistant", "content": Answer})

        # Limit chat history size
        if len(messages) > MAX_HISTORY:
            messages = messages[-MAX_HISTORY:]

        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModified(Answer)

    except Exception as e:
        logging.error(f"Error in ChatBot function: {e}\n{traceback.format_exc()}")
        return "I encountered an error. Please try again."

# Main program
if __name__ == "__main__":
    print("\n JARVIS STARTED...\n")
    speak_text("Jarvis is now online. How can I assist you?")
    
    while True:
        user_input = command()  # Voice input
        print("User said:", user_input)
        
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("\n Shutting down Jarvis...\n")
            speak_text("Shutting down. Have a great day!")
            break

        time.sleep(0.5)  # Small delay to avoid speech conflicts
        response = ChatBot(user_input)
        print("\nJarvis said:", response)
        speak_text(response)  # Speak the response
        print()