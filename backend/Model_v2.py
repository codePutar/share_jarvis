import cohere
from rich import print
from  dotenv import dotenv_values
from chatBot_v2 import ChatBot
# from TextToSpeech_V2 import speak
from TextToSpeech_v4 import TextToSpeech, TTS
from RealtimeSearchEngine import RealtimeSearchEngine
from SpeechToText import QueryModifier, UniversalTranslator, command
from automation import GoogleSearch, System, OpenApp,YoutubeSearch,PlayYoutube,CloseApp,is_system_muted
from datetime import datetime, timedelta
import re

import json
import time
import threading



#load enviroment variables from the .evn file
env_vars = dotenv_values(".env")

#retrieve API key
CohereAPIKey = env_vars.get("CohereAPIKey")

#create a cohere client using the provided API key
co = cohere.Client(api_key=CohereAPIKey)

#define a list of  recognized function keywords for task categorization
funcs = [
    "exit", "general", "realtime", "open", "close",
    "play","generate image", "system", "content","google search",
    "youtube search", "reminder"
]

# Initialize an empty list  to store user messages
messages = []

#Define  the preamble  that guids the AI model on how to categorize queries
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc. Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer. Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc and if the query is asking about any individual or thing like if the query is 'who is akshay kumar' respond with 'realtime who is akshay kumar', if the query is 'what is today's news?' respond with 'realtime what is today's news?', if the query is 'what is today's headline?' respond with 'realtime what is today's headline?', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc. but if the query is asking to open multiple applications, respond with 'open 1st application name, open 2nd application name' and so on.
-> Respond with 'close (application name)' if a query is asking to close any application like 'close notepad', 'close facebook', etc. but if the query is asking to close multiple applications or websites, respond with 'close 1st application name, close 2nd application name' and so on.
-> Respond with 'play (song name)' if a query is asking to play any song like 'play afsanay by ys', 'play let her go', etc. but if the query is asking to play multiple songs, respond with 'play 1st song name, play 2nd song name' and so on.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate a image with given prompt like 'generate image of a lion', 'generate image of a cat', etc. but if the query is asking to generate multiple images, respond with 'generate image 1st image prompt, generate image 2nd image prompt' and so on.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder like 'set a reminder at 9:00pm on 25th june for my business meeting.' respond with 'reminder 9:00pm 25th june business meeting'.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down , etc. but if the query is asking to do multiple tasks, respond with 'system 1st task, system 2nd task', etc.
-> Respond with 'content (topic)' if a query is asking to write any type of content like application, codes, emails or anything else about a specific topic but if the query is asking to write multiple types of content, respond with 'content 1st topic, content 2nd topic' and so on.
-> Respond with 'google search (topic)' if a query is asking to search a specific topic on google but if the query is asking to search multiple topics on google, respond with 'google search 1st topic, google search 2nd topic' and so on.
-> Respond with 'youtube search (topic)' if a query is asking to search a specific topic on youtube but if the query is asking to search multiple topics on youtube, respond with 'youtube search 1st topic, youtube search 2nd topic' and so on.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# preamble = """
# You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
# You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write an application and open it in notepad', or 'set a reminder'.
# *** Do not answer any query, just decide what kind of query is given to you. ***

# -> Respond with 'general ( query )' if a query can be answered by a llm model (conversational AI chatbot) and doesn't require any up-to-date information. For example:
#     - "who was akbar?" → 'general who was akbar?'
#     - "how can I study more effectively?" → 'general how can I study more effectively?'
#     - "Thanks, I really liked it." → 'general thanks, I really liked it.'
#     - "what's the time?" → 'general what's the time?'
#     - "what's his net worth?" → 'general what's his networth?'
#     - "tell me more about him." → 'general tell me more about him.'

# -> Respond with 'realtime ( query )' if a query cannot be answered by a LLM alone and requires up-to-date information. Examples:
#     - "who is the Indian Prime Minister" → 'realtime who is Indian Prime Minister'
#     - "tell me about Facebook's recent update" → 'realtime tell me about Facebook's recent update'
#     - "what is today's news?" → 'realtime what is today's news?'

# -> Respond with 'open (application name or website name)' for opening applications:
#     - "open facebook" → 'open facebook'
#     - "open chrome and firefox" → 'open chrome, open firefox'

# -> Respond with 'close (application name)' for closing applications:
#     - "close notepad" → 'close notepad'

# -> Respond with 'play (song name)' for playing music:
#     - "play let her go" → 'play let her go'

# -> Respond with 'generate image (image prompt)' for image generation:
#     - "generate image of a lion" → 'generate image of a lion'

# -> Respond with 'reminder (datetime with message)' for reminders:
#     - "set a reminder at 9:00pm on 25th June for my business meeting" → 'reminder 21:00 25th June business meeting'
#     - "remind me to call mom tomorrow at 8 AM" → 'reminder 08:00 [tomorrow's date] call mom'

# -> Respond with 'system (task name)' for system actions:
#     - "mute system" → 'system mute'
#     - "volume up" → 'system volume up'

# -> Respond with 'content (topic)' for content creation:
#     - "write a Python calculator program" → 'content Python calculator program'

# -> Respond with 'google search (topic)' for Google searches:
#     - "search Python classes online" → 'google search Python classes online'

# -> Respond with 'youtube search (topic)' for YouTube searches:
#     - "search Java tutorial for beginners" → 'youtube search Java tutorial for beginners'

# *** If multiple tasks are requested, list them in order:
#     Example: "open facebook, telegram and close whatsapp" → 'open facebook, open telegram, close whatsapp'

# *** If the user says goodbye like "bye Jarvis", respond with 'exit'.***

# *** Respond with 'general (query)' if you cannot decide the type or if the query doesn't match any of the categories above. ***
# """

#define a chat history with predefined user-chatbot interaction for context.
ChatHistory =[
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dace performance"},
    {"role": "User", "message": "chat with me"},
    {"role": "Chatbot", "message": "general chat with me"}
]

#define the main function for decision making on queries
def FirstLayerDMM(prompt: str = "test"):
    # Check if the prompt is empty or only spaces
    if not prompt or prompt.strip() == "":
        return ["general The message is not clear, please say it again."]
    
    #add  the user's query to the message list.
    messages.append({"role": "user", "content": f"{prompt}"})

    #Create a streaming  chat session with  the Cohere Model
    stream = co.chat_stream(
        model = 'command-a-03-2025',
        message= prompt,
        temperature= 0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble= preamble
    )

    #initialize an empty string to store generated response
    response = ""

    # Iterate over events in the stream and capture text generation events
    for event in stream:
        if event.event_type == "text-generation":
            response +=event.text
    
    #remove newline characters and split the response into individual tasks.
    response = response.replace("\n","")
    response = response.split(",")

    #strip leading  and  trailing whitespaces from each task
    response = [i.strip() for i in response]

    # Initializing  an list  to filter valid tasks.
    temp = []

    #filter the tasks based on recognizing function keywords.
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)
    
    # update  the response  with the filtered list of task
    response = temp

    #if query is in the response , recursively call the function for  further clarification
    if "(query)" in response:
        newresponse = FirstLayerDMM(prompt=prompt)
        return newresponse
    else:
        return response

def parse_reminder(text):
    """
    Extracts datetime and message from a user query.
    Example:
    "remind me to call mom at 8 PM tomorrow"
    Returns: (datetime_object, "call mom")
    """
    # Look for 'at' or 'on' followed by time/date
    match = re.search(r'remind me to (.+) at (\d{1,2}(:\d{2})?\s?(AM|PM)?)', text, re.IGNORECASE)
    if match:
        message = match.group(1).strip()
        time_str = match.group(2).strip()

        # parse time
        reminder_time = datetime.strptime(time_str, "%I %p")  # simple case, handle "8 PM"
        
        # If the time is already passed today, schedule for tomorrow
        now = datetime.now()
        reminder_time = reminder_time.replace(year=now.year, month=now.month, day=now.day)
        if reminder_time < now:
            reminder_time += timedelta(days=1)
        return reminder_time, message
    return None, None

REMINDER_FILE = "Data/reminders.json"

def save_reminder(reminder_time, message):
    """
    Save a new reminder into reminders.json
    while keeping all existing reminders intact.
    """
    try:
        # Load existing reminders
        with open(REMINDER_FILE, "r") as f:
            reminders = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        reminders = []

    # Append the new reminder
    reminders.append({
        "role": "reminder",  # optional: to keep consistency like chat logs
        "time": reminder_time.strftime("%Y-%m-%d %H:%M:%S"),
        "message": message
    })

    # Save all reminders back to the JSON file
    with open(REMINDER_FILE, "w") as f:
        json.dump(reminders, f, indent=4)

    print(f"Reminder saved: {message} at {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}")


def check_reminders():
    while True:
        try:
            with open(REMINDER_FILE, "r") as f:
                reminders = json.load(f)
        except:
            reminders = []

        now = datetime.now()
        pending = []
        for r in reminders:
            reminder_time = datetime.strptime(r["time"], "%Y-%m-%d %H:%M:%S")
            if now >= reminder_time:
                TTS(f"Reminder: {r['message']}")
            else:
                pending.append(r)

        # Save only pending reminders
        with open(REMINDER_FILE, "w") as f:
            json.dump(pending, f, indent=4)

        time.sleep(60)  # check every 1 minute

threading.Thread(target=check_reminders, daemon=True).start()

#enter point  for the script
if __name__ =="__main__":
    # Continuosly prompt the user for input and process it.
    Assistantname = env_vars.get("Assistantname")
    print(f"{Assistantname} Started....")
    # speak("Jarvis is now Online")
    TTS(f"{Assistantname} is now Online")
    while True:
        query = QueryModifier(UniversalTranslator(command()))
        categories = FirstLayerDMM(query)
        
        for cat in categories:
            if cat.startswith("general"):
                response = UniversalTranslator(ChatBot(query))
                print(f"[General Answer]: {response}")
                # speak(response)
                TTS(response)
            elif cat.startswith("realtime"):
                response = UniversalTranslator(RealtimeSearchEngine(query))
                print(f"[Realtime Search]: {response}")
                # speak(response)
                TTS(response)
            
            elif cat.startswith("google search"):
                response = GoogleSearch(query)
                print(f"[Google Search]: {response}")
                # speak(response)
                TTS("Response is now displayed on the screen")

            elif cat.startswith("system"):
                commands = cat.replace("system ", "").strip().lower() # Extract the actual command
                print(is_system_muted)
                if is_system_muted == 1:
                    # Execute the system command first
                    # Speak "Task Completed" only after executing the command
                    response = System(commands)
                    TTS("Task Completed")

                else:
                    TTS("Task Completed")
                    response = System(commands)

                print(f"[System]: {response}")

            elif cat.startswith("youtube search"):
                response = YoutubeSearch(query)
                print(f"[Youtube Search]: {response}")
                # speak(response)
                TTS("Search completed")

            elif cat.startswith("play"):
                response = PlayYoutube(YoutubeSearch(query))
                print(f"[Youtube Search play]: {response}")
                # speak(response)
                TTS("Playing the video")

            elif cat.startswith("open"):
                response =OpenApp(query)
                print(f"[Opening app]]: {response}")
                # speak(response)
                TTS("Opening the app")

            elif cat.startswith("close"):
                response = CloseApp(query)
                print(f"[Closing app]: {response}")
                # speak(response)
                TTS("Closing the app")

            elif cat.startswith("reminder"):
                reminder_time, message = parse_reminder(query)
                if reminder_time:
                    save_reminder(reminder_time, message)
                    TextToSpeech(f"Reminder set for {reminder_time.strftime('%I:%M %p on %d %b')}")
                else:
                    TextToSpeech("Sorry, I couldn't understand the reminder time.")

            elif cat.strip().lower().startswith("exit"):
                TTS("Thanks for taking me in your service")
                break
            
            else:
                print(f"[Task]: {cat}")
                if cat.lower() in ["exit", "quit", "stop"]:
                    print("Hope I help you well..")
                    # speak("Hope I help You well.. ")
                    TextToSpeech("Hope I help You well.. ")
                    break


    # "generate image", , "content",
    # , "reminder"