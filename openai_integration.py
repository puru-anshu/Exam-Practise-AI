from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()  # Load environment variables from .env file

openai = OpenAI()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_questions(subject, difficulty,num_questions=10):
    system_message ="You are an expert education teacher who teaches students about a specific subject for class XI and class XII.\
          You will be given a subject and a difficulty level, and you will generate a set of multiple-choice question for that subject with that difficulty level."
    prompt = f"Generate a set {num_questions} of multiple-choice question about {subject} with difficulty level {difficulty}.\
          Format the response as JSON with the following structure: {{\"question\": \"...\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], \
              \"correct_answer\": \"A/B/C/D\"}}"

    messages =[
        {"role":"system","content":system_message},
        {"role":"user","content":prompt }
    ]
    
    completion = openai.chat.completions.create(model='gpt-4o-mini', messages=messages)
    

    question_data = completion.choices[0].message.content.strip()
    question_data = question_data.replace("```json", "")
    question_data = question_data.replace("```", "")
    json_result = json.loads(question_data)
    return json_result  # Convert the JSON string to a Python dictionary


