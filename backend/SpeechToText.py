import speech_recognition as sr
from dotenv import dotenv_values
import mtranslate as mt

# Load environment variables from the file .env
env_var = dotenv_values(".env")
InputLanguage = env_var.get("InputLanguage", "en-in")  # Default to "en-in" if not found

# Function to modify a query by adding proper punctuation and formatting
def QueryModifier(Query):
    if not Query:
        return ""
    
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom",
                        "can you", "what's", "where's", "how's"]

    # Add a question mark if the sentence is a question
    if any(new_query.startswith(word) for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        # Add a period if the query is not a question
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

# Function to translate text to English using mtranslate library
def UniversalTranslator(Text):
    if not Text:
        return ""
    
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition
def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        r.pause_threshold = 1
        r.phrase_threshold = 0.5
        r.sample_rate = 48000
        r.dynamic_energy_threshold = True
        r.operation_timeout = 10
        r.non_speaking_duration = 1
        r.dynamic_energy_adjustment = 1
        r.energy_threshold = 1  # Adjusted energy threshold

        audio = r.listen(source)

    # Recognize speech using Google Speech Recognition
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language=InputLanguage)
        print(f"User said: {query}\n")
        if query:
            translated_text = UniversalTranslator(query)
            formatted_text = QueryModifier(translated_text)
        return formatted_text
    except Exception as e:
        print("Say that again, please.")
        return None

# Main execution block
if __name__ == "__main__":
    while True:
        command()
