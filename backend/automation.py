#import required libes
from AppOpener import close, open as appopen #include function to open and close apps
from webbrowser import open as webopen #include web browser functionality
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os
import time

#load enviroment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

#define css classes for parsing specific elements in HTML content
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf","pclqee", 
        "tw-Data-text tw-text-small tw-ta","IZ6rdc","O5uR6d LTKOO","vlzY6d",
        "webanswers-webanswers_table_webanswers-table","dDoNo ikb4Bb gsrt","sXLaOe","LWkfKe","VQF4g","qv3Wpe","kno-rdesc","SPZz6b"]

#Define a user-agent for making web-request
useragent = 'Mozilla/5.0 (Window NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

#initialize the  Groq client with the api key
client = Groq(api_key=GroqAPIKey)

#predefine professional response for user interaction
professional_responses =[
        "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
        "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]

#list to store chatbot messages
messages = []

#system messgae to provide context to the chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I an{os.environ['Username']},You are an AI writing assistant that generates well-structured and contextually appropriate content, including letters, applications, and essays. Ensure correct grammar, clarity, proper formatting, and adjust tone based on the purpose and audience."}]

#function to perform google search
def GoogleSearch(Topic):
        search(Topic)
        return True

#function to generate content using ai and save it to a file
#def Content(Topic):

        #nested function to open a file in Notepad
        def OpenNotepad(File):
                default_text_editor = 'notepad.exe'
                subprocess.Popen([default_text_editor, File])
        
        # Nested function to generate content using the ai chatbot
        def ContentWriterAI(prompt):
                messages.append({"role": "user", "content": f"{prompt}"})
                
                completion = client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=SystemChatBot + messages,  # Include system instructions and chat history
                max_tokens=1024,  # Reduced to avoid hitting token limits
                temperature=0.7,
                top_p=1,
                stream=True,  # Streaming enabled
        )               

                Answer = ""

                #process streamed reponse chunks
                for chunk in completion:
                        if hasattr(chunk, "choices") and chunk.choices:
                                delta_content = chunk.choices[0].delta.get("content", "")
                        if delta_content:
                                Answer += delta_content
                                print(delta_content, end="", flush=True)  # Print as it streams
                Answer = Answer.replace("</s", "").strip()
                messages.append({"role": "assistant", "content": Answer})
        
        Topic: str = Topic.replace("Content ", "")
        ContentByAI = ContentWriterAI(Topic)

        #save the generated content to a text file
        with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
                file.write(ContentByAI)
                file.close()

        OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
        return True
#TODO: Problem in Content Function 
# Content("write a letter on sick leave")
#function to search for a topic on youtube
def YoutubeSearch(Topic):
        song = Topic.replace('play','')
        Url4Search = f"https://www.youtube.com/results?search_query={song}"
        webbrowser.open(Url4Search)
        return True

def PlayYoutube(query):
        song = query.replace('play','')
        playonyt(song)

# Function to open application on the relevant webpage
def OpenApp(app, sess=requests.session()):

        try:
                appopen(app, match_closest=True, output=True, throw_error=True)
                return True
        except:
                # nested function to extract links from html content
                def extract_links(html):
                        if html is None:
                                return []
                        soup = BeautifulSoup(html, 'html.parser')
                        links = soup.find_all('a', {'jisname': 'UWckNb'})
                        return [link.get('herf') for link in links]
                #nested function to perform a google search and retrieve html
                def search_google(query):
                        url = f"html://www.google.com/search?q={query}"
                        headers = {"User-Agent": useragent}
                        response = sess.get(url, headers=headers)

                        if response.status_code == 200:
                                return response.txt
                        else:
                                print("failed to retrieve search results")
                        return None
                html = search_google(app)

                if html:
                        link = extract_links(html)[0]
                        webopen(link)

                return True

#function to close an application
def CloseApp(app):

        if "chrome" in app:
                pass
        else:
                try:
                        close(app, match_closest=True, output=True, throw_error=True)
                        return True
                except:
                        return False

#function to execute system-level commands
def System(command):

        # Simulate checking mute status (workaround)
        keyboard.press_and_release("volume mute")  # Toggle mute
        time.sleep(0.5)  # Short delay to allow the system to register the change
        keyboard.press_and_release("volume mute")  # Toggle back to restore original state


        #nested function to mute the system volume
        def mute():
                if not is_system_muted():  # Only mute if it's not already muted
                        keyboard.press_and_release("volume mute")
        
        #nested function to unmute the system volume
        def unmute():
                if is_system_muted():  # Only mute if it's not already muted
                        keyboard.press_and_release("volume mute")
        
        #nested fucntion to volume up system volume
        def volume_up():
                keyboard.press_and_release("volume up")

        #nested function to volume down system volume
        def volume_down():
                keyboard.press_and_release("volume down")
        
        #execute the appropiate command
        if command == "mute":
                mute()
        elif command == "unmute":
                unmute()
        elif command == "volume up":
                volume_up()
        elif command == "volume down":
                volume_down()
        
        return True #indicates success

def is_system_muted():
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        return volume.GetMute()  # Returns 1 if muted, 0 if unmuted



#asynchronous function to translate and execute user command
async def TranslateAndExecute(commands: list[str]):

        funcs = []

        for command in commands:

                if command.startswith("open "):
                        if "open it" in command:
                                pass
                        elif "open file" in command:
                                pass

                        else:
                                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                                funcs.append(fun)
                
                elif command.startswith("genral "):
                        pass
                elif command.startswith("realtime "):
                        pass
                elif command.startswith("close "):
                        fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
                        funcs.append(fun)
                elif command.startswith("play "):
                        fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
                        funcs.append(fun)
                elif command.startswith("content "):
                        fun = asyncio.to_thread(CloseApp, command.removeprefix("content "))
                        funcs.append(fun)
                elif command.startswith("google search "):
                        fun = asyncio.to_thread(CloseApp, command.removeprefix("google search "))
                        funcs.append(fun)
                elif command.startswith("youtube search "):
                        fun = asyncio.to_thread(CloseApp, command.removeprefix("youtube search "))
                        funcs.append(fun)
                elif command.startswith("system "):
                        fun = asyncio.to_thread(CloseApp, command.removeprefix("system "))
                        funcs.append(fun)
                else:
                        print(f"no fucntion found for{command}")
        results = await asyncio.gather(*funcs)

        for result in results:
                if isinstance(result, str):
                        yield result
                else:
                        yield result

#asynchronous function to automate command execution
async def Automation(commands: list[str]):
        async for result in TranslateAndExecute(commands):
                pass

        return True