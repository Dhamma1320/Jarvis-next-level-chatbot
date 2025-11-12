import cohere  # Cohere AI SDK
from rich import print  # For colorful console logging
from dotenv import dotenv_values  # To load .env file

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

# Retrieve API key
CohereAPIKey = env_vars.get("CohereAPIKey")

# Initialize Cohere client
co = cohere.Client(api_key=CohereAPIKey)

# Predefined keywords for possible command recognition
funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

# Store conversation history
messages = []

# System preamble: defines AI’s personality and context
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', or 'can you write an application and open it in notepad'.
*** Do not answer any query; just decide what kind of query is given to you. ***
→ Respond with 'general (query)' if a query can be answered by an LLM model (conversational AI chatbot) 
and doesn't require any up-to-date information.
Examples:
- If the query is 'who was akbar?' respond with 'general who was akbar?'
- If the query is 'how can I study more effectively?' respond with 'general how can I study more effectively?'
- If the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?'
- If the query is 'Thanks, I really liked it.' respond with 'general thanks, I really liked it.'
- If the query is 'what is python programming language?' respond with 'general what is python programming language?'
"""

# Predefined chat history for context
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi."},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi."},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User", "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"},
    {"role": "User", "message": "chat with me."},
    {"role": "Chatbot", "message": "general chat with me."}
]

def FirstLayerDMM(prompt: str):
    # Add the user's query to the messages list
    messages.append({"role": "user", "content": prompt})

    # Create a streaming chat session with the Cohere model
    stream = co.chat_stream(
        model="command-xlarge-nightly",
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,
        prompt_truncation="OFF",
        connectors=[],
        preamble=preamble
    )

    # Collect the generated text from the stream
    response_text = ""

    for event in stream:
        if event.event_type == "text-generation":
            response_text += event.text

    # Process the text: remove newlines, split by comma, and strip spaces
    response = response_text.replace("\n", "")
    response = response.split(",")
    response = [i.strip() for i in response]

    temp = []

    # Filter tasks based on recognized keywords
    for task in response:
        for func in funcs:
            if task.startswith(func):
                temp.append(task)

    # Handle '(query)' responses safely
    if any("(query)" in r for r in response):
        print("[yellow]Model returned '(query)', retrying once...[/yellow]")
        return FirstLayerDMM(prompt)
    else:
        return temp

# Entry point for the script
if __name__ == "__main__":
    try:
        while True:
            user_input = input(">>> ")
            if user_input.lower() in ["exit", "quit"]:
                print("[red]Exiting Decision-Making Model...[/red]")
                break
            print(FirstLayerDMM(user_input))
    except KeyboardInterrupt:
        print("\n[red]Program interrupted. Exiting...[/red]")
