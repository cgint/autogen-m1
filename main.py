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


def initiate_chat_duo_go(task, model, temperature):
    llm_config_selected = get_llm_config(model, temperature)
    # In the AutoGen example, we create an AssistantAgent to play the role of the coder
    assistant_senior = autogen.AssistantAgent(
        name="senior_developer",
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/senior.txt')
    )
    user_proxy = autogen.UserProxyAgent(
        name="product_owner",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "/app/output", "use_docker": False},
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/user_proxy.txt'),
        default_auto_reply="You are going to figure all out by your own. "
        "Work by yourself, the user won't reply until you output `TERMINATE` to end the conversation."
    )
    user_proxy.initiate_chat(assistant_senior, message=task)


def initiate_chat_group_go(task, model, model_proxy, model_qa, model_po, model_senior, temperature):

    # assistant_cto = autogen.AssistantAgent(
    #     name="CTO",
    #     llm_config=llm_config_selected,
    #     system_message=read_file_content('/app/input/assistants/cto.txt')
    # )

    # In the AutoGen example, we create an AssistantAgent to play the role of the coder
    assistant_senior = autogen.AssistantAgent(
        name="senior_developer",
        llm_config=get_llm_config(model_senior, temperature),
        system_message=read_file_content('/app/input/assistants/senior.txt')
    )
    assistant_qa = autogen.AssistantAgent(
        name="quality_assurance",
        llm_config=get_llm_config(model_qa, temperature),
        system_message=read_file_content('/app/input/assistants/qa.txt')
    )
    assistant_po = autogen.AssistantAgent(
        name="product_owner",
        llm_config=get_llm_config(model_po, temperature),
        system_message=read_file_content('/app/input/assistants/po.txt')
    )
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=5,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "/app/output", "use_docker": False},
        llm_config=get_llm_config(model_proxy, temperature),
        system_message=read_file_content('/app/input/assistants/user_proxy.txt'),
        default_auto_reply="You are going to figure all out by your own. "
        "Work by yourself, the user won't reply until you output `TERMINATE` to end the conversation."
    )
    groupchat = autogen.GroupChat(agents=[user_proxy, assistant_po, assistant_senior, assistant_qa], messages=[], max_round=8)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=get_llm_config(model, temperature))
    user_proxy.initiate_chat(manager, message=task)


def get_llm_config(model_proxy, temperature):
    return { 
        "config_list": get_config_list_for_model(model_proxy),
        "seed": random.randint(1, 100000),
        "temperature": temperature,
        "request_timeout": 6000
    }


@app.route("/initiate_chat_duo", methods=["POST"])
def initiate_chat_duo():
    print("Duo-Request has been triggered.")
    request_json = request.get_json()
    model = request_json["model"]
    temperature = request_json["temperature"]
    task = request_json["task"]
    if not task:
        task = read_file_content('/app/input/task1/task.txt')
    initiate_chat_duo_go(task, model, temperature)
    print("Duo-Request is done.")
    return "Duo-Chat initiated successfully"


@app.route("/initiate_chat_group", methods=["POST"])
def initiate_chat_group():
    print("Group-Request has been triggered.")
    request_json = request.get_json()
    model = request_json["model"]
    model_proxy = request_json["model_proxy"]
    model_qa = request_json["model_qa"]
    model_po = request_json["model_po"]
    model_senior = request_json["model_senior"]
    temperature = request_json["temperature"]
    task = request_json["task"]
    if not task:
        task = read_file_content('/app/input/task1/task.txt')
    initiate_chat_group_go(task, model, model_proxy, model_qa, model_po, model_senior, temperature)
    print("Group-Request is done.")
    return "Group-Chat initiated successfully"


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
