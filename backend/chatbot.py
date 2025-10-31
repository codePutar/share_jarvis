from groq import Groq
from json import load, dump
import json
import datetime
from dotenv import dotenv_values
from SpeechToText import QueryModifier,UniversalTranslator, command;
# from TextToSpeech import TextToSpeech;
from TextToSpeech_V2 import speak;

# load enviroment variable from the .env file
env_vars = dotenv_values(".env")

#retreive specific enviroment  variable  for username, assistant name, and API KEY
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client  using the provided API key
client = Groq(api_key=GroqAPIKey)

# Initialize an empty list  to store chat msg
messages = []

#define a system message that provides the  context to the AI chatbot about it's role and behavior
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""
# A list of system instruction for chatbot
SystemChatBot = [
    {"role": "system", "content": System}
]

# attempt  to load th chat log from a json file
try:
    with open(r"Data\chatLog.json", "r") as f:
        messages = json.load(f) # load existing messages from the chat log
except (FileNotFoundError,  json.JSONDecodeError):
    #if  the file doesn't exist, create an empty json file to store chat logs.
    with open(r"Data\chatLog.json", "w") as f:
        json.dump([], f)

#fucntion to get real-time date and time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    seconds = current_date_time.strftime("%S")

    #formate the information into a string
    data = f"please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{seconds} seconds.\n"
    return data

#function to modify the chatbot's response for better formatting.
def AnswerModified(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#main chat bot function to handle user queries
def ChatBot(Query):
    """ This function sends the user's query to the chatbot and returns the AI's response. """

    try:
        # load existing chatlog from the json file
        with open(r"Data\chatLog.json", "r") as f:
            messages = load(f) 

        #   Append the user's query to the message list.
        messages.append({"role": "user", "content": f"{Query}"})

        # Make a request to the Groq API  for a response.
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream= True,
            stop=None
        )

        Answer = ""

        #process the streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content
        
        Answer = Answer.replace("</s>","")

        #append the chatbot's response  to the message list
        messages.append({"role": "assistant", "content": Answer})

        #save the update chat log to the json file
        with open(r"Data\chatLog.json", "w") as f:
            dump(messages, f, indent=4)
        
        #return the formatted response
        return AnswerModified(Answer=Answer)

    except Exception as e:
        #handle errors by printing the exception and  resetting the chat log.
        print(f"Error: {e}")
        with open(r"Data\chatLog.json", "w") as f:
            dump([], f, indent=4)
        return ChatBot(Query)

#main program entery point
if __name__ =="__main__":
    print("JARVIS STARTED......")
    while True:

        user_input = command()
        print()
        print("Jarvis said: "+ChatBot(user_input)),
        speak(ChatBot(user_input))
        print()