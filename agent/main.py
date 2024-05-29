from base import State, Node, Settings, TASK_INSTRUCTIONS_PATH
from templates import (
    generate_prompt,
    reject_command_prompt,
    initial_setting,
    format_action,
    unformat_action,
)
from commands import commands, noop_commands
import tiktoken
from openai import OpenAI
ACTION_START = "<|ACTION_START|>"

main_reject_command_prompt= reject_command_prompt
openai_client = OpenAI(base_url="http://localhost:8000/v1",
    api_key="token-abc123",)


def get_task():
    with open(TASK_INSTRUCTIONS_PATH, "r") as f:
        return f.read()


def format_prompt(state: State):
    return generate_prompt, {
        "instance_id": state.instance_id,
        "initial_setting": initial_setting,
        "nodes": "\n".join([x.body for x in state.nodes]),
        "individual_nodes": [x.body for x in state.nodes],
        "task": state.task,
    }


def parse_generation(generation):
    generation=generation.strip()
    global main_reject_command_prompt
    if "|||" not in generation:
        return None
    elif not generation.startswith(ACTION_START):
        main_reject_command_prompt=f"Invalid: Commands not executed. Start actions with {ACTION_START}. Ensure there is no text before it, or after it and before a command. Format: <|ACTION_START|> Command ||| Argument <|ACTION_END|>"
    return {
        "command": generation.split("|||")[0].strip(),
        "arg": "|||".join(generation.split("|||")[1:]).strip(),
    }


def step(state: State, settings: Settings):
    global main_reject_command_prompt
    if len(state.nodes) > 0:
        last_node = state.nodes[-1]

        if last_node.parsed_action is not None:
            command = commands.get(last_node.parsed_action["command"])
            if last_node.parsed_action["command"] in noop_commands:
                if "|||" in last_node.parsed_action["arg"]:
                    state.append(Node(body="If there are additional commands after reasoning, they were not executed. Ensure you run only one command within each action start and end block.", type="generation", parsed_action=None)
                )
                pass
            elif command is None:
                state.append(
                    Node(body=main_reject_command_prompt, type="error", parsed_action=None)
                )
                main_reject_command_prompt=reject_command_prompt
                return
            else:
                command(last_node.parsed_action["arg"], state, settings)
                return
        elif last_node.type == "generation":
            print("invalid", last_node.body, state.dict())
            state.append(
                Node(body=main_reject_command_prompt, type="error", parsed_action=None)
            )
            main_reject_command_prompt=reject_command_prompt
            return
    generation = generate_action(state, settings)
    parsed = parse_generation(unformat_action(generation))
    state.append(
        Node(
            body=generation,
            type="generation",
            parsed_action=parsed,
        )
    )


GENERATION_MODEL_SHORT_CTX_LEN = 8000


def generate_action(state: State, settings: Settings) -> str:
    template, template_values = format_prompt(state)
    gen_prompt = (
        template.replace("{{&initial_setting}}", initial_setting)
        .replace("{{&instance_id}}", template_values["instance_id"])
        .replace("{{&nodes}}", template_values["nodes"])
        .replace("{{&task}}", template_values["task"])
    )
    return format_action(
        openai_client.chat.completions.create(
            messages=[{"role": "system", "content": gen_prompt}], **settings.dict()
        )
        .choices[0]
        .message.content
    )


default_settings = Settings(
    n=1,
    model="meta-llama/Meta-Llama-3-70B-Instruct",
    temperature=1.0,
    max_tokens=1200,
    stop=["<|ACTION_END|>"],
)


def main(*args):
    print("STARTING AGENT")
    settings = default_settings
    task = get_task()
    state = State.new(task)
    print("Task:", task)
    while True:
        step(state, settings)
        if state.nodes[-1].body.startswith("Submitting: ```\n"):
            break


if __name__ == "__main__":
    main()
