# chatBot_groq_safe.py
from groq import Groq
from json import load, dump
import json
import datetime
import logging
from dotenv import dotenv_values
from SpeechToText import QueryModifier, UniversalTranslator, command
from TextToSpeech_V2 import speak

# Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load environment variables from .env file
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname", "Jarvis")
Username = env_vars.get("Username", "User")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Models (primary + comma-separated fallbacks in .env)
# Example FALLBACK env: "llama-3.1-8b-instant,llama-3.1-70b-specdec"
PRIMARY_GROQ_MODEL = env_vars.get("GROQ_MODEL", "llama-3.1-70b-versatile")
GROQ_MODEL_FALLBACKS = env_vars.get("GROQ_MODEL_FALLBACKS", "")
# build ordered list
GROQ_MODELS = [m for m in ([PRIMARY_GROQ_MODEL] + ([s.strip() for s in GROQ_MODEL_FALLBACKS.split(",")] if GROQ_MODEL_FALLBACKS else [])) if m]

# Initialize the Groq client (guard missing key)
if not GroqAPIKey:
    raise RuntimeError("Groq API key missing. Set GroqAPIKey in your .env")

client = Groq(api_key=GroqAPIKey)

# Chat log file path
CHAT_LOG_PATH = r"Data\chatLog.json"

# Load chat history
try:
    with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
        messages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    messages = []
    # ensure folder exists and create the file
    try:
        with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(messages, f)
    except Exception:
        pass

# System message for chatbot behavior
System = f"""Hello, I am {Username}. You are {Assistantname}, an accurate AI chatbot with real-time internet access.
*** Do not tell time until I ask. Keep responses brief. ***
*** Always reply in English, even if the question is in Hindi. ***
*** Do not provide notes or mention your training data. ***
"""

# System instructions
SystemChatBot = [{"role": "system", "content": System}]

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Day: {current_date_time.strftime('%A')}, Date: {current_date_time.strftime('%d-%B-%Y')}, Time: {current_date_time.strftime('%H:%M:%S')}"

def AnswerModified(Answer):
    return ' '.join(Answer.split()).strip()

def _attempt_chat_with_model(model_name: str, combined_messages: list):
    """
    Attempt a single Groq chat completion call with model_name.
    Returns (ok:bool, answer_or_error:str)
    """
    try:
        logging.info(f"Trying Groq model: {model_name}")
        completion = client.chat.completions.create(
            model=model_name,
            messages=combined_messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=False
        )
        # Extract answer
        answer = completion.choices[0].message.content.strip()
        return True, answer
    except Exception as e:
        # Return full exception for debugging and detection
        logging.error(f"Groq error for model={model_name}: {e}", exc_info=True)
        return False, str(e)

def ChatBot(Query):
    """ Sends user query to chatbot and returns the AI response. Tries fallback models if needed. """
    try:
        # Reload chat log to avoid race conditions
        try:
            with open(CHAT_LOG_PATH, "r", encoding="utf-8") as f:
                local_messages = load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            local_messages = []

        # Append user query (role must be 'user')
        local_messages.append({"role": "user", "content": Query})

        # Compose the messages to send: system instructions + realtime info + chat history
        combined_messages = SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + local_messages

        last_err = None
        # Try each model in order until one succeeds or all fail
        for model in GROQ_MODELS:
            ok, out = _attempt_chat_with_model(model, combined_messages)
            if ok:
                Answer = out
                # Save assistant reply into history (assistant role)
                local_messages.append({"role": "assistant", "content": Answer})
                # Persist chat log
                try:
                    with open(CHAT_LOG_PATH, "w", encoding="utf-8") as f:
                        dump(local_messages, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    logging.warning(f"Failed to write chat log: {e}")

                return AnswerModified(Answer)

            # if not ok, detect decommissioned / model unavailable and continue to next fallback
            err_text = out.lower()
            last_err = out
            if "decommissioned" in err_text or "model_decommissioned" in err_text or "model not found" in err_text or "invalid_request_error" in err_text:
                logging.warning(f"Model {model} appears decommissioned/unavailable. Trying next fallback (if any).")
                continue
            else:
                # For other errors, we still attempt next model but log
                logging.warning(f"Model {model} failed with non-decommission error. Trying next fallback (if any).")
                continue

        # All models exhausted -> return an informative message
        logging.error(f"All Groq models failed. Last error: {last_err}")
        return "I encountered an error (model unavailable). Please try again or update the model in .env."

    except Exception as e:
        logging.error(f"Error in ChatBot function: {e}", exc_info=True)
        return "I encountered an error. Please try again."

if __name__ == "__main__":
    print(f"{Assistantname} STARTED......")
    speak(f"{Assistantname} is now online. How can I assist you?")
    while True:
        user_input = command()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "stop"]:
            print("Exiting. Goodbye!")
            break

        response = ChatBot(user_input)
        print(f"\n{Assistantname} said:", response)
        speak(response)
        print()
