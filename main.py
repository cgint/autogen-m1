import random
import autogen
import os
from flask import Flask, request
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
        'api_base': 'https://6clldsku5klrlv-5000.proxy.runpod.net/v1',
        'api_key': "NULL"
    }
]
config_list_ollama_amd2 = [
    {
        'api_type': 'open_ai',
        'model': 'ollama/codellama',
        'api_base': 'http://192.168.1.234:8000',
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

llm_config_lm_1234 = {
    "config_list": config_list_lm_1234,
}
llm_config_runpod = {
    "config_list": config_list_runpod,
}
llm_config_ollama_amd2 = {
    "config_list": config_list_ollama_amd2,
}
llm_config_gpt35 = {
    "config_list": config_list_gpt35,
}
llm_config_gpt4 = {
    "config_list": config_list_gpt35,
}


def create_ollama_config(model):
    result = {
        "config_list": {
            'api_type': 'open_ai',
            'model': model,
            'api_base': 'http://192.168.1.234:8000',
            'api_key': "NULL"
        }
    }
    return result


def get_config_for_model(model):
    if model.startswith("ollama/"):
        return create_ollama_config(model)
    elif model == "runpod":
        return llm_config_runpod
    elif model == "gpt35":
        return llm_config_gpt35
    elif model == "gpt4":
        return llm_config_gpt4
    else:
        return llm_config_lm_1234


def initiate_chat_go(task, model):
    llm_config_selected = get_config_for_model(model)
    llm_config_selected["seed"] = random.randint(1, 100000)
    llm_config_selected["temperature"] = 0
    llm_config_selected["request_timeout"] = 6000

    assistant_cto = autogen.AssistantAgent(
        name="CTO",
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/cto.txt')
    )

    assistant_senior = autogen.AssistantAgent(
        name="senior_developer",
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/senior.txt')
    )

    assistant_qa = autogen.AssistantAgent(
        name="quality_assurance",
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/qa.txt')
    )

    user_proxy = autogen.UserProxyAgent(
        name="product_owner",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
        code_execution_config={"work_dir": "output", "use_docker": False},
        llm_config=llm_config_selected,
        system_message=read_file_content('/app/input/assistants/user_proxy.txt')
    )

    # groupchat = autogen.GroupChat(agents=[user_proxy, assistant_senior], messages=[], max_round=10)
    # manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config_selected)
    user_proxy.initiate_chat(assistant_senior, message=task)


def read_file_content(file_path):
    return open(file_path, 'r').read()


@app.route("/initiate_chat", methods=["POST"])
def initiate_chat():
    request_json = request.get_json()
    model = request_json["model"]
    task = request_json["task"]
    if not task:
        task = read_file_content('/app/input/task1/task.txt')
    initiate_chat_go(task, model)
    print("Request is done.")
    return "Chat initiated successfully"


if __name__ == "__main__":
    app.run(port=5005, host="0.0.0.0")
