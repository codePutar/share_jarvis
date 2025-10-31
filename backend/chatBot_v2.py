from groq import Groq
from json import load, dump
import json
import datetime
import logging
from dotenv import dotenv_values
from SpeechToText import QueryModifier, UniversalTranslator, command
from TextToSpeech_V2 import speak

# Configure Logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
Username = env_vars.get("Username")
GroqAPIKey = env_vars.get("GroqAPIKey")
groqAiName = env_vars.get("GroqModel")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# Chat log file path
CHAT_LOG_PATH = r"Data\chatLog.json"

# Load chat history or create new
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []
    with open(CHAT_LOG_PATH, "w") as f:
        json.dump(messages, f)

# Fix old messages to use valid roles and content key
for msg in messages:
    # Old logs might have "User" or "Chatbot" roles
    if msg.get("role", "").lower() not in ["user", "assistant", "system"]:
        msg["role"] = "user"
    # Old logs might have "message" instead of "content"
    if "message" in msg:
        msg["content"] = msg.pop("message")

# System message for chatbot behavior
System = f"""Hello, I am {Username}. You are {Assistantname}, an accurate AI chatbot with real-time internet access.
*** Do not tell time until I ask. Keep responses brief. ***
*** Always reply in English, even if the question is in Hindi. ***
*** Do not provide notes or mention your training data. ***
"""

# System instructions
SystemChatBot = [{"role": "system", "content": System}]

# Function to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Day: {current_date_time.strftime('%A')}, Date: {current_date_time.strftime('%d-%B-%Y')}, Time: {current_date_time.strftime('%H:%M:%S')}"

# Function to clean and format chatbot responses
def AnswerModified(Answer):
    return ' '.join(Answer.split())  # Removes extra spaces

# Main chatbot function
def ChatBot(Query):
    """ Sends user query to chatbot and returns the AI response. """
    try:
        # Load existing chat log
        with open(CHAT_LOG_PATH, "r") as f:
            messages = json.load(f)

        # Fix old messages in case roles/content are incorrect
        for msg in messages:
            if msg.get("role", "").lower() not in ["user", "assistant", "system"]:
                msg["role"] = "user"
            if "message" in msg:
                msg["content"] = msg.pop("message")

        # Prepare messages for Groq request (without modifying stored file yet)
        chat_input = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages + [{"role": "user", "content": Query}]

        # Make a request to Groq API
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_input,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False
        )

        Answer = completion.choices[0].message.content.strip()  # Get full response

        # Append the user query and assistant response to messages
        messages.append({"role": "user", "content": Query})
        messages.append({"role": "assistant", "content": Answer})

        # Save updated chat log
        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModified(Answer)

    except Exception as e:
        logging.error(f"Error in ChatBot function: {e}")
        return "I encountered an error. Please try again."

# Main program entry point
if __name__ == "__main__":
    print("JARVIS STARTED......")
    speak("Jarvis is now online. How can I assist you?")
    while True:
        user_input = command()
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Exiting Jarvis. Goodbye!")
            break

        response = ChatBot(user_input)  # Fetch response once
        print("\nJarvis said:", response)
        speak(response)
        print()
