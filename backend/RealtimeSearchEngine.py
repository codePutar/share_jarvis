from googlesearch import search
from groq import Groq
from json import load, dump
import json
import datetime
from dotenv import dotenv_values

# load enviroment variable from the .env file
env_vars = dotenv_values(".env")

#retreive specific enviroment  variable  for username, assistant name, and API KEY
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client  using the provided API key
client = Groq(api_key=GroqAPIKey)

#define the system instruction  for the chatbot
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

#try to load chat logs from json file.
try:
    with open(r"ChatLog.json", "r") as f:
        messages = json.load(f)
except:
    with open(r"ChatLog.json", "w") as f:
        json.dump([], f)

#function to perform google search
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
    
    Answer += "[end]"
    return Answer

#function  to clean up the answer by removing empty line
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

#pre define chatbot conversation system message and an initial user message
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you ?"}
]

#Function to get real time information like current date and time
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Year: {year}\n"
    data += f"Month: {month}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

#function   to handle real-time search and response generation
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    #load the chat logs from the json file
    with open(r"ChatLog.json", "r") as f:
        messages = json.load(f)
    messages.append({"role": "user", "content":  f"{prompt}"})

    #add a google search results to the system chat bot messages
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    #generate a response using the groq client
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot +[{"role": "system", "content": Information()}] + messages,
        temperature= 0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )

    Answer = ""

    #concatenate response chunks from the streaming output
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content
    
    #Clean up the response
    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer})

    #save the updated chat log back to the json file
    with open(r"ChatLog.json", "w") as f:
        json.dump(messages, f, indent=4)
    
    #remove the most recent  system message from the chatbot conversation
    SystemChatBot.pop()
    return AnswerModifier(Answer=Answer)

#main enter point of the program

if __name__ == "__main__":
    while True:
        prompt = input("Enter your Query: ")
        print(RealtimeSearchEngine(prompt))