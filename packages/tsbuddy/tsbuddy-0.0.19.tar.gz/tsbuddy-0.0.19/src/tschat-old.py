import os
import time
import openai

# Prompt for API key if not set
if "OPENAI_API_KEY" not in os.environ:
    api_key = input("Enter your OpenAI API key: ").strip()
    os.environ["OPENAI_API_KEY"] = api_key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Step 1: Create the Assistant (once)
assistant = openai.beta.assistants.create(
    name="Caching Assistant",
    instructions="You are a helpful assistant that explains things clearly.",
    model="gpt-4o"
)
print(f"Assistant created: {assistant.id}")

# Step 2: Create a thread to store conversation history
thread = openai.beta.threads.create()
print(f"Thread created: {thread.id}")

# Prompt for file path and load file content
file_path = input("Enter the path to the file you want to load into the thread: ").strip()
if os.path.isfile(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        file_content = f.read()
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Please load and remember the following file for this session.\n\n{file_content}"
    )
    print(f"Loaded file '{file_path}' into the thread.")
else:
    print(f"File '{file_path}' not found. Continuing without loading a file.")

# Continuous chat loop
print("\nType your message and press Enter. Type 'exit' to quit.\n")
while True:
    user_input = input("You: ").strip()
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting chat.")
        break
    # Add user message to thread
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    # Run the assistant
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )
    # Poll until run is complete
    while True:
        run_status = openai.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status in ["failed", "cancelled", "expired"]:
            print(f"Run {run_status.status}")
            break
        time.sleep(1)
    # Retrieve the assistant's reply
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    # Print only the latest assistant reply
    for msg in reversed(messages.data):
        if msg.role == "assistant":
            print(f"Assistant: {msg.content[0].text.value}\n")
            break
