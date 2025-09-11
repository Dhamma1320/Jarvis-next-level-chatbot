# main.py

from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech

from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

# Default welcome message
DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

# Globals
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

# ----------------------- CHAT LOG HELPERS -----------------------

def ShowDefaultChatIfNoChats():
    try:
        with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as db_file:
                    db_file.write("")
                with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as resp_file:
                    resp_file.write(DefaultMessage)
    except FileNotFoundError:
        os.makedirs("Data", exist_ok=True)
        with open(r"Data\ChatLog.json", "w", encoding="utf-8") as file:
            file.write("[]")

def ReadChatLogJson():
    with open(r"Data\ChatLog.json", "r", encoding="utf-8") as file:
        return json.load(file)

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath("Database.data"), "r", encoding="utf-8") as file:
            data = file.read()
        if data.strip():
            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as resp_file:
                resp_file.write(data)
    except FileNotFoundError:
        pass

# ----------------------- EXECUTION HELPERS -----------------------

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username} : {Query}")
    SetAssistantStatus("Thinking...")

    Decision = FirstLayerDMM(Query)
    print(f"\nDecision : {Decision}\n")

    # classify
    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    # merge queries
    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith(("general", "realtime"))]
    )

    # detect image generation
    for q in Decision:
        if "generate" in q:
            ImageGenerationQuery = q
            ImageExecution = True

    # detect automation
    for q in Decision:
        if not TaskExecution and any(q.startswith(func) for func in Functions):
            run(Automation(list(Decision)))
            TaskExecution = True

    # trigger image generation
    if ImageExecution:
        with open(r"Frontend\Files\ImageGeneration.data", "w", encoding="utf-8") as file:
            file.write(f"{ImageGenerationQuery}, True")

        try:
            p1 = subprocess.Popen(
                ["python", r"Backend\ImageGeneration.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    # realtime query handling
    if (G and R) or R:
        SetAssistantStatus("Searching...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering...")
        TextToSpeech(Answer)
        return True

    # handle other query types
    for q in Decision:
        if "general" in q:
            SetAssistantStatus("Thinking...")
            QueryFinal = q.replace("general ", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "realtime" in q:
            SetAssistantStatus("Searching...")
            QueryFinal = q.replace("realtime ", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "exit" in q:
            Answer = ChatBot("Okay, Bye!")
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            os._exit(1)

# ----------------------- THREADING -----------------------

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

# ----------------------- MAIN -----------------------

if __name__ == "__main__":
    InitialExecution()
    thread1 = threading.Thread(target=FirstThread, daemon=True)
    thread1.start()
    SecondThread()
