import os
import openai
import time

ENV_FILE = ".env"

def load_env_file():
    """Load key-value pairs from .env into os.environ"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, sep, value = line.strip().partition("=")
                    if sep:  # Only set if '=' was found
                        os.environ.setdefault(key, value)

def append_to_env_file(key, value):
    """Append a new key=value to .env"""
    with open(ENV_FILE, "a") as f:
        f.write(f"{key}={value}\n")

# Load .env into environment
load_env_file()

# Prompt if API key not set
if "OPENAI_API_KEY" not in os.environ:
    api_key = input("Enter your OpenAI API key: ").strip()
    os.environ["OPENAI_API_KEY"] = api_key
    append_to_env_file("OPENAI_API_KEY", api_key)

# Use the key
openai.api_key = os.environ["OPENAI_API_KEY"]

# # Prompt for API key if not set
# if "OPENAI_API_KEY" not in os.environ:
#     api_key = input("Enter your OpenAI API key: ").strip()
#     os.environ["OPENAI_API_KEY"] = api_key
# openai.api_key = os.environ["OPENAI_API_KEY"]

# Prompt for file path and load file content
file_path = input("Enter the path to the file you want to load into the chat: ").strip()
file_content = None
if os.path.isfile(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_content = f.read()
    print(f"Loaded file '{file_path}' into the chat.")
else:
    print(f"File '{file_path}' not found. Continuing without loading a file.")

# Start a continuous chat loop using the Responses API
print("\nType your message and press Enter. Type 'exit' to quit.\n")

# Prepare the initial messages list
messages = []
if file_content:
    messages.append({
        "role": "user",
        "content": f"Please load and remember the following file for this session.\n\n{file_content}"
    })

while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat.")
        break
    messages.append({"role": "user", "content": user_input})
    try:
        response = openai.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages
        )
        assistant_reply = response.choices[0].message.content
        print(f"Assistant: {assistant_reply}\n")
        messages.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        print(f"Error: {e}")
