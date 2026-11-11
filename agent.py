import time
import requests
import subprocess
import os

# Set your Render service URL
RELAY_URL = "https://device-agent-relay.onrender.com"

def execute_command(command_text):
    """Executes local OS commands or shell actions safely."""
    try:
        # Example shell execution (or custom script routing)
        output = subprocess.check_output(command_text, shell=True, stderr=subprocess.STDOUT, text=True)
        return output if output else "Command executed successfully with no output."
    except Exception as e:
        return f"Execution Error: {str(e)}"

def poll_relay():
    print("Agent started. Polling for tasks...")
    while True:
        try:
            response = requests.get(f"{RELAY_URL}/agent/poll", timeout=10)
            data = response.json()

            if data.get("status") == "task_available":
                task = data["task"]
                cmd = task["command"]
                chat_id = task["chatId"]
                print(f"Executing task: {cmd}")

                # Execute task locally
                result = execute_command(cmd)

                # Send back execution result
                requests.post(f"{RELAY_URL}/agent/results", json={
                    "chatId": chat_id,
                    "output": result
                })

        except Exception as e:
            print(f"Polling error: {e}")

        time.sleep(3) # Polls every 3 seconds

if __name__ == "__main__":
    poll_relay()
