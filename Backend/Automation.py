from AppOpener import close, open as appopen   # Open and close apps
from webbrowser import open as webopen         # Open URLs in browser
from pywhatkit import search, playonyt         # Google search and YouTube playback
from dotenv import dotenv_values               # Manage environment variables from .env
from bs4 import BeautifulSoup                  # Parse HTML content
from rich import print                         # Styled console output
from groq import Groq                          # Groq client for AI functionality
import webbrowser
import subprocess                              # Run subprocesses
import requests                                # Make HTTP requests
import keyboard                                # Detect and simulate keyboard actions
import asyncio                                 # Async programming support
import os                                      # Operating system functions

# -------------------- GLOBAL CONFIG --------------------

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey") # Retrieve API key

# Define CSS classes for parsing specific elements in HTML content
classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "ZOLcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
            "IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e", 
            "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.7339.81 Safari/537.36"


# Initialize the Groq client with the API key
client = Groq(api_key=GroqAPIKey)

# Predefined professional responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# Chatbot context
messages = []

# System message to provide context to the chatbot
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os.environ.get('Username', 'User')}," "You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}] 

# Google Search
def GoogleSearch(Topic):
    search(Topic)
    return True

# Content Generation
def Content(Topic):
    
    # --- Nested: open file in Notepad ---
    def OpenNotepad(File):
        default_text_editor = "notepad.exe"
        subprocess.Popen([default_text_editor, File])
    
    # --- Nested: generate content using AI ---
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # AI model name
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""  # Initialize an empty string for the response

        # Process streamed response chunks
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check for content in the current chunk
                Answer += chunk.choices[0].delta.content  # Append the content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer}) # Store assistant response
        return Answer

    Topic: str = Topic.replace("Content ", "")  # Remove "Content" from the topic
    ContentByAI = ContentWriterAI(Topic)       # Generate content using AI

    # Save the generated content to a text file
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")
    return True

# Function to search for a topic on YouTube.
def YouTubeSearch (Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}" 
    webbrowser.open(Url4Search) 
    return True 

# Function to play a video on YouTube. 
def PlayYoutube(query):
    playonyt(query)
    return True

# Function to open an application or a relevant webpage
def OpenApp(app, sess=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    
    except:
        # Nested func to extract links from HTML content
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links]

        # Nested func to perform a google search and retrieve HTML
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)

            if response.status_code == 200:
                return response.text
            else:
                print("Failed to retrieve search results.")
            return None

        html = search_google(app)

        if html:
            links = extract_links(html)[0]
            webopen(links)

        return True
    
# function to close an application
def CloseApp(app):

    if "chrome" in app: 
        pass  
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)
            return True 
        except:
            return False 

# function to execute system-level commands
def System(command):

    def mute():
        keyboard.press_and_release("volume mute") 

    def unmute():
        keyboard.press_and_release("volume unmute") 

    def volume_up():
        keyboard.press_and_release("volume up")  

    def volume_down():
        keyboard.press_and_release("volume down")  

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True 

# Asynchronous func to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):

    funcs = [] 

    for command in commands:

        if command.startswith("open "):  
            if "open it" in command: 
                pass

            if "open files" == command:
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):  
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
            fun = asyncio.to_thread(Content, command.removeprefix("content "))  
            funcs.append(fun)

        elif command.startswith("google search "): 
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))  
            funcs.append(fun)

        elif command.startswith("youtube search "): 
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))  
            funcs.append(fun)

        elif command.startswith("system "): 
            fun = asyncio.to_thread(System, command.removeprefix("system "))  
            funcs.append(fun)

        else:
            print(f"No Function Found. For {command}")  

    results = await asyncio.gather(*funcs)  

    for result in results:  
        if isinstance(result, str):
            yield result
        else:
            yield result

# Asynchronous function to automate command execution
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass

    return True  

if __name__ == "__main__":
    asyncio.run(Automation(["play saiyaara song", "open whatsapp"]))
