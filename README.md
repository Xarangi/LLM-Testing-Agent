# LLM-Testing-Agent
A LLM Agent from [METR](https://github.com/METR/task-standard/tree/main/workbench/example-agents/legacy-baseline) modified for an LLM testing task.

# Report

## Introduction

For this task, I decided to evaluate the capabilities of >2 agents and classify them in 3 categories: 1) Completed the task with no hand-holding. 2) Completed the task with some hand-holding. 3) Couldn’t complete the task.

For the agent itself, I chose METR’s legacy-baseline example agent. My reasoning behind choosing the relatively basic agent was that it would allow me to jump into the code without spending a significant amount of time in understanding it. In designing the task description and editing the agent’s scaffolding, I had the liberty of using the Llama 3 70b model through my university’s HPC resources. I set the LLM up using vLLM so that I wouldn’t have to change any code that was previously designed for openai’s API calls (such as in METR’s example agent). I used Replicate for the individual LLM calls, and chose the Llama 2 7b chat, Llama 3 8b, Mistral 7bn instruct models as my LLMs to be tested. I wrote scripts for calling these 3 LLMs on a single prompt through the command line.

For the task description, I started with essentially rephrasing the task from the task description document and making minor edits. After I started running my agent on the task description, I kept noting common pitfalls and started to add clearer guidelines for the relevant sections of the task. Towards the end of the task, after I could semi-reliably finish the task using the Llama model, I created a simpler version of the task with clear guidelines for all sections, and a difficult version of the task that I’d expect a person with programming knowledge and basic LLM testing knowledge to be able to complete without using external resources such as the internet.

## Results

Given the relative simplicity of the task, the frontier open-source model Llama 3 70B faced significantly more difficulties than I had initially foreseen. It required relatively significant hand-holding for the LLM evaluation section. The METR legacy-baseline agent when powered by Llama 3 70B can successfully execute the final version of the task as defined in the instructions ~60-70% of the time. In my few attempts, GPT4 managed to finish the task 4/4 times indicating that it can potentially perform the task with less explicit task-specific prompting. In the limited amount of tests, the Llama 3 agent finished the easy version of the task in all the trials.

## Difficulties

The agent would often fail to output results in the correct format. To be specific, the METR agent requires command in the format: `Command ||| argument`. Additionally, the command needs to be wrapped in `<|ACTION_START>` and blocks. The agent LLM would often miswrite commands and waste iterations on correcting it. Additionally, it would often assume that certain commands had already been run, when in fact they hadn’t due to a formatting error. The original scaffolding wasn’t much helpful in this regard, because it returned a generic error message to the LLM. I edited the scaffolding to be more explicit as to the source of the error and how to potentially correct it. Specifically, I:

- Explicitly pointed the LLM agent when ACTION_START or ACTION_END blocks were missing or misformatted
- Pointed out when commands were misformatted along with the correct format.
- Cleared extra spaces that could potentially be causing errors using `.strip()` where relevant/
- Detected additional “|||” operators, because these indicated the agent having outputted multiple commands in a single action call. In this case, I notified the agent that its additional commands may not have been executed.

## Future Work

- Create an automated scoring mechanism to evaluate partially correct performance on the different tasks: The model would often perform the first part of the task well but fail at the second part.
- Test out more capable agents (reAct agents, and agents that explicitly reflect on prior outputs and results)
- Flesh out and test the easy and hard tasks, evaluate where GPT4/GemJni-Pro lie and how much hand holding they may need to do the hard task (if any)
- Change the instructions into METR’s defined standard task format for easier reproducibility.
- Make the experiment reproducible by creating a docker container etc.

## Advice for anyone that may work on this project:

- Set-up clear task definitions, goals, and guidelines from the start of the experiment.
- Even if creating a docker container isn’t possible, attempt to isolate the working environment from the system as much as possible given the agent can make any changes it sees fit.
- Evaluate agent action history thoroughly to identify breaking- points and potential areas that are regular sources of confusion.

