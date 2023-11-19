import autogen
import os

config_list = [
    {
        # 'model': 'gpt-3.5-turbo-16k',
        'model': 'gpt-4-1106-preview',
        'api_key': os.environ.get("OPENAI_API_KEY")
    }
]

llm_config = {
    "request_timeout": 600,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0
}

assistant = autogen.AssistantAgent(
    name="CTO",
    llm_config=llm_config,
    system_message="""Chief technical officer of a tech company with long experience in software development.
Stick to the task. Do not be chatty."""
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web", "use_docker": False},
    llm_config=llm_config,
    system_message="""Reply TERMINATE if the task has been solved at full satisfaction.
Otherwise, reply CONTINUE, or the reason why the task is not solved yet. 
Stick to the task. Do not be chatty."""
)

task = """
Write python code to output numbers 1 to 100, and then store the python code in a file named "test1.py"
"""

user_proxy.initiate_chat(
    assistant,
    message=task
)

task2 = """
Change the code in the file you just created to instead output numbers 1 to 200. store the python code in a file named "test2.py"
"""

user_proxy.initiate_chat(
    assistant,
    message=task2
)
