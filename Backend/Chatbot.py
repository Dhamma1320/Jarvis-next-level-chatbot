# chatbot.py
# ----------------- IMPORTS -----------------
from groq import Groq                  # For interacting with the Groq API
from json import load, dump            # For reading and writing JSON files
import datetime                        # For real-time date and time information
from dotenv import dotenv_values       # For loading environment variables from .env file
import os

# ----------------- ENVIRONMENT VARIABLES -----------------
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# ----------------- CLIENT INIT -----------------
client = Groq(api_key=GroqAPIKey)

# ----------------- SYSTEM MESSAGE -----------------
System = f"""
Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question. ***
*** Reply in only English, even if the question is in Hindi, reply in English. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": System}]

# ----------------- CHAT LOG LOADING -----------------
CHATLOG_PATH = r"Data\ChatLog.json"

if not os.path.exists("Data"):
    os.makedirs("Data")

try:
    with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
        messages = load(f)
except FileNotFoundError:
    with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
        dump([], f, indent=4)
    messages = []

# ----------------- FUNCTIONS -----------------

def RealtimeInformation() -> str:
    """Return real-time date and time info as a formatted string."""
    current_date_time = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours : "
        f"{current_date_time.strftime('%M')} minutes : "
        f"{current_date_time.strftime('%S')} seconds.\n"
    )

def AnswerModifier(answer: str) -> str:
    """Remove empty lines for cleaner output."""
    return "\n".join([line for line in answer.split('\n') if line.strip()])

def ChatBot(Query: str) -> str:
    """Main chatbot function — handles queries and stores chat history."""
    global messages
    try:
        # Load existing messages
        with open(CHATLOG_PATH, "r", encoding="utf-8") as f:
            messages = load(f)

        # Add user query
        messages.append({"role": "user", "content": Query})

        # Request completion
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        # Save assistant response
        messages.append({"role": "assistant", "content": Answer})
        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"[ERROR ChatBot]: {e}")
        # Reset chat log instead of recursive retry to avoid infinite loops
        with open(CHATLOG_PATH, "w", encoding="utf-8") as f:
            dump([], f, indent=4)
        return "Sorry, something went wrong. Please try again."

# ----------------- MAIN -----------------
if __name__ == "__main__":
    while True:
        user_input = input("Enter Your Question: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        print(f"{Assistantname}: {ChatBot(user_input)}")
