# Backend/model.py – Decision-Making Model with Cohere
import cohere  # Cohere AI API
from rich import print  # Pretty console output
from dotenv import dotenv_values  # Load API keys & env variables

# Load environment variables
env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")

# Initialize Cohere client
co = cohere.Client(api_key=CohereAPIKey)

# Recognized function keywords
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Store chat history for better context
messages = []

# Preamble (instruction set for Cohere model)
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.

You will decide whether a query is a 'general' query, a 'realtime' query, 
or is asking to perform any task or automation like 'open facebook, instagram', 
'can you write an application and open it in notepad'.

*** Do not answer any query, just decide what kind of query is given to you. ***

-> Respond with 'general ( query )' if a query can be answered by an LLM model 
   (conversational AI chatbot) and doesn't require up-to-date information.

-> Respond with 'realtime ( query )' if the query requires current, real-time information.

-> Respond with 'open ( app )' if the query is asking to open an app, website, or service.

-> Respond with 'close ( app )' if the query is asking to close an app, website, or service.

-> Respond with 'play ( media )' if the query is asking to play some media.

-> Respond with 'generate image ( description )' if the query is asking to generate an image.

-> Respond with 'system ( command )' if the query is asking for a system-level task.

-> Respond with 'content ( type )' if the query is asking to create or provide some content.

-> Respond with 'google search ( query )' if the query is asking to search something on Google.

-> Respond with 'youtube search ( query )' if the query is asking to search something on YouTube.

-> Respond with 'reminder ( details )' if the query is asking to set a reminder.

-> Respond with 'exit' if the query is asking to exit or stop the interaction.
"""

# Predefined chat history for guiding Cohere
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "what is today's date and remind me that i have a meeting tomorrow 8AM"},
    {"role": "Chatbot", "message": "general what is today's date, reminder tomorrow 8AM meeting"},
]


def FirstLayerDMM(prompt: str = "test"):
    """Classify the query using Cohere model and return decisions."""

    # Save query to history
    messages.append({"role": "user", "content": f"{prompt}"})

    # Stream Cohere response
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    response = ""

    # Collect model output
    for event in stream:
        if event.event_type == "text-generation":
            response += event.text

    # Normalize response
    response = response.replace("\n", "")
    response = [i.strip() for i in response.split(",")]

    # Filter only recognized functions
    valid_tasks = [task for task in response if any(task.startswith(func) for func in funcs)]

    # Safety fallback
    if not valid_tasks:
        return ["general " + prompt]

    return valid_tasks


# ------------------ TESTING ------------------
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        print(FirstLayerDMM(user_input))
