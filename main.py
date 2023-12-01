import random
import autogen
import os
from flask import Flask, request, send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

openai_api_key = os.environ.get("OPENAI_API_KEY")

config_list_lm_1234 = [
    {
        'api_type': 'open_ai',
        'api_base': 'http://192.168.1.152:1234/v1',
        'api_key': "NULL"
    }
]
config_list_runpod = [
    {
        'api_type': 'open_ai',
        'api_base': 'https://o09ju7se1yeyun-5000.proxy.runpod.net/v1',
        'api_key': "NULL"
    }
]
config_list_gpt35 = [
    {
        'model': 'gpt-3.5-turbo-16k',
        'api_key': openai_api_key
    }
]
config_list_gpt4 = [
    {
        'model': 'gpt-4-1106-preview',
        'api_key': openai_api_key
    }
]


def create_ollama_config_list(model):
    return [{
        'api_type': 'open_ai',
        'model': model,
        'api_base': 'http://amd2.local:8000',
        'api_key': "NULL"
    }]


def create_ollama_runpod_config_list(model):
    return [{
        'api_type': 'open_ai',
        'model': model,
        'api_base': 'http://amd2.local:8001',
        'api_key': "NULL"
    }]


def read_file_content(file_path):
    return open(file_path, 'r').read()


def get_config_list_for_model(model):
    if model.startswith("ollama/"):
        return create_ollama_config_list(model)
    elif model.startswith("ollama_runpod/"):
        return create_ollama_runpod_config_list(model.replace("_runpod", ""))
    elif model == "runpod":
        return config_list_runpod
    elif model == "gpt35":
        return config_list_gpt35
    elif model == "gpt4":
        return config_list_gpt4
    else:
        return config_list_lm_1234

def get_llm_config(model_proxy, temperature):
    return { 
        "config_list": get_config_list_for_model(model_proxy),
        "seed": random.randint(1, 100000),
        "temperature": temperature,
        "request_timeout": 6000
    }




@app.route("/", methods=["GET"])
def index():
    return send_file("index.html")


@app.route("/initiate_chat_aider", methods=["POST"])
def initiate_chat_aider():
    # Extract 'task' and 'model' from the POST request
    request_json = request.get_json()
    task = request_json.get("task", "")
    model = request_json.get("model", "default_model")  # Default model if not provided
    if not task:
        return "Error: No task provided", 400

    # Inline system messages for each assistant role
    system_messages = {
        "CTO": "Oversee the technical aspects of the project. Ensure architectural decisions and technical standards are met.",
        "Senior Developer": "Write clean, efficient code and provide technical expertise. Collaborate with QA to ensure code quality.",
        "QA": "Perform thorough testing and validation. Report and track issues found, and work closely with developers to resolve them.",
        "Product Owner": "Keep the end-user in mind to ensure solutions meet user needs. Document all processes and decisions.",
        "User Proxy": "Facilitate communication between the user and the system. Log issues, notify other assistants, and handle errors."
    }

    # Define the configuration for the assistants
    llm_config = get_llm_config(model, 0.7)  # Example temperature

    # Create the assistants with their specific system messages
    assistants = {
        "CTO": autogen.AssistantAgent("CTO", llm_config, system_messages["CTO"]),
        "Senior Developer": autogen.AssistantAgent("Senior Developer", llm_config, system_messages["Senior Developer"]),
        "QA": autogen.AssistantAgent("QA", llm_config, system_messages["QA"]),
        "Product Owner": autogen.AssistantAgent("Product Owner", llm_config, system_messages["Product Owner"]),
        "User Proxy": autogen.UserProxyAgent("User Proxy", llm_config, system_messages["User Proxy"])
    }

    # Example of initiating chat with the Senior Developer assistant
    # This should be replaced with the actual logic for initiating the chat
    response = assistants["Senior Developer"].process(task)

    # Return a success response
    return "Chat initiated successfully with task: " + task

# Start the Flask application
if __name__ == "__main__":
    app.run(port=5005, host="0.0.0.0")
