from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt


## major fail this can't use selenium api for the ai


#load enviroment variables from the file .env
env_var = dotenv_values(".env")
#get the input language setting from the enviroment variables
InputLanguage = env_var.get("InputLanguage")

#define the html code for the speech recognition interface
HtmlCode ='''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

#replace
HtmlCode = str(HtmlCode).replace("Recognition.lang = '';",f"recognition.lang = '{InputLanguage}';")

#write the modified html code to a file
with open(r"Data\Voice.html", "w") as f:
    f.write(HtmlCode)

#get current distro
current_dir = os.getcwd()

Link = f"{current_dir}/Data/Voice.html"

chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")
# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager(). install())
driver = webdriver. Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
TempDirPath = rf"{current_dir}/Frontend/Files"

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}/Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

#function to modify a query to ensure proper punctuations and formatting
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how","what","who","where","when","why","which","whose", "whom","can you", "what's","where's","how's", "can you"]

    # checks if the query ias a question and add a question mark if necessary
    if any(word +" " in new_query for word in question_words):
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query +="?"
    else:
        #add a period if the query is not a question.
        if query_words[-1][-1] in ['.','?','!']:
            new_query = new_query[:-1] + "."
        else:
            new_query +="."
        
    return new_query.capitalize()

# function to translate text to english using mtranslate lib
def UniversalTranslator(Text):
        english_translation = mt.translate(Text, "en","auto")
        return english_translation.capitalize()

#speech recognition
def SpeechRecognition():

    driver.get("file:///"+Link)

    driver.find_element(by =By.ID, value="start").click()

    while True:
        try:

            Text = driver.find_element(by=By.ID, value="output").text

            if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                return QueryModifier(Text)
            else:

                SetAssistantStatus("Translating...")
                return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            pass

if __name__ == "__main__":
    while True:
        # continuously perform speech reognition and print the  recognizied text
        Text = SpeechRecognition()
        if Text.strip():
            print(Text)