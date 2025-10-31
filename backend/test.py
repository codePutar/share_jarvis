from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time  # Added for loop control

# Load environment variables
env_var = dotenv_values(".env")
InputLanguage = env_var.get("InputLanguage", "en-US")  # Default English if not set

# Define HTML Code
HtmlCode = f'''<!DOCTYPE html>
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
        let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = '{InputLanguage}';
        recognition.continuous = true;

        recognition.onresult = function(event) {{
            let transcript = event.results[event.results.length - 1][0].transcript;
            output.innerHTML = transcript; 
        }};

        function startRecognition() {{
            recognition.start();
        }}

        function stopRecognition() {{
            recognition.stop();
            output.innerHTML = "";
        }}
    </script>
</body>
</html>'''

# Write HTML to File
os.makedirs("Data", exist_ok=True)
with open("Data/Voice.html", "w") as f:
    f.write(HtmlCode)

# Chrome Options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# REMOVE Headless Mode
# chrome_options.add_argument("--headless=new")

# Start WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Load Speech Recognition HTML
Link = os.path.abspath("Data/Voice.html")
driver.get("file:///" + Link)

# Function to Modify Query
def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to Translate Text
def UniversalTranslator(Text):
    return mt.translate(Text, "en", "auto").capitalize()

# Speech Recognition Function
def SpeechRecognition():
    driver.find_element(By.ID, "start").click()
    prev_text = ""  # To track text updates

    while True:
        try:
            time.sleep(0.5)  # Avoid infinite fast looping
            text = driver.find_element(By.ID, "output").text

            if text and text != prev_text:  # Only process new text
                prev_text = text  # Update previous text
                print(f"Recognized: {text}")

                if InputLanguage.lower().startswith("en"):
                    return QueryModifier(text)
                else:
                    return QueryModifier(UniversalTranslator(text))

        except Exception as e:
            print(f"Error: {e}")

# Main Execution
if __name__ == "__main__":
    while True:
        Text = SpeechRecognition()
        print("Final Output:", Text)
