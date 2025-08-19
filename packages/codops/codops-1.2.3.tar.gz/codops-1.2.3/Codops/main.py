import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the OpenAI and GitHub tokens
openai_api_key = os.getenv("OPENAI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
 
print("OpenAI API Key:", openai_api_key)

import openai


#openai.api_key="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"


completion = openai.ChatCompletion.create(
  model="gpt-4.1",
  store=True,
  messages=[
    {"role": "user", "content": "write a lorem ipsum text of 100 words"}
  ]
)

print(completion['choices'][0]['message']['content'])


#questions

def ask_question(question):
    response = openai.ChatCompletion.create(
        model='gpt-4.1',  
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response['choices'][0]['message']['content']


question = "What is an API?"
answer = ask_question(question)

print("Réponse de l'IA :", answer)


