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

# Initialize messages and file_content
messages = []
file_content = None

print("\nMenu:\n1. Send a chat message\n2. Send a file\n3. Exit\n")

while True:
    choice = input("Choose an option (1-chat, 2-file, 3-exit): ").strip()
    if choice == "1":
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break
        messages.append({"role": "user", "content": user_input})
        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=messages
            )
            assistant_reply = response.choices[0].message.content
            print(f"tsbuddy: {assistant_reply}\n")
            messages.append({"role": "assistant", "content": assistant_reply})
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "2":
        file_path = input("Enter the path to the file you want to send: ").strip()
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
            print(f"Loaded file '{file_path}' into the chat.\n")
            messages.append({
                "role": "user",
                "content": f"Please load and remember the following file for this session.\n\n{file_content}"
            })
        else:
            print(f"File '{file_path}' not found.")
    elif choice == "3":
        print("Exiting chat.")
        break
    else:
        print("Invalid option. Please choose 1, 2, or 3.")
