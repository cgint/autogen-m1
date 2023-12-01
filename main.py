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


if __name__ == "__main__":
    app.run(port=5005, host="0.0.0.0")
