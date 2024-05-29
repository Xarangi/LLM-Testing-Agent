# from transformers import pipeline
import replicate
import sys

def main(prompt):
    # chat = [
    #     {"role": "system", "content": "You are a question-answering system that provides a single letter answer corresponding to the correct option (A,B,C,D)"},
    # ]

    # # Append the user's prompt from the command line arguments
    # chat.append({"role": "user", "content": prompt})

    # # Initialize the pipeline
    # pipe = pipeline("text-generation", model="meta-llama/Llama-2-7b-chat-hf")

    # # Generate a response
    # response = pipe(chat)
    
    # # Print the last content item from the generated text
    # print(response[0]['generated_text'][-1]['content'].strip())

    input = {
    "top_p": 0.95,
    "prompt": prompt +"\nAnswer: ",
    "temperature": 0.7,
    "system_prompt": "You are a question-answering system that provides a single letter answer corresponding to the correct option (A,B,C, or D) and nothing else. Don't output any words.",
    "presence_penalty": 0,
    "max_new_tokens": 2
    }

    output = replicate.run(
        "meta/llama-2-7b-chat",
        input=input
    )
    print("".join(output).strip())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = sys.argv[1]
        main(user_prompt)
    else:
        print("Please provide a prompt after the script name.")