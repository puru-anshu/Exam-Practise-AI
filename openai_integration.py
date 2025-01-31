from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import ollama
from pydantic import BaseModel


load_dotenv()  # Load environment variables from .env file

openai = OpenAI()
model_name="gpt-4o-mini"
openai.api_key = os.getenv("OPENAI_API_KEY")
# openai = OpenAI(base_url = 'http://localhost:11434/v1',api_key='ollama', )
# model_name="llama3.2"

system_message ="""You are an expert education teacher who teaches students about a specific 
        subject for class XI and class XII.You will be given a subject and a difficulty level, 
        and you will generate a set of multiple-choice question for that subject with that difficulty level."""

ollama = ollama.Client("http://localhost:11434/")

class Question(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

def generate_questions(subject, difficulty,num_questions=10,use_ollama=False):
    
    prompt = (
        f"Generate a set {num_questions} of multiple-choice question about "
        f"{subject} with difficulty level {difficulty}. "
        "Format the response as JSON with the following structure: "
        "{\"question\": \"...\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], "
        "\"correct_answer\": \"A/B/C/D\"}"
    )

    messages =[
        {"role":"system","content":system_message},
        {"role":"user","content":prompt }
    ]

    model_name="gpt-4o-mini"
    question_data= ""
    if use_ollama:
        # model_name="llama3.2"
        model_name="deepseek-r1:1.5b"
        questions=[]
        for i in range(num_questions):
            response =ollama.chat(model=model_name, messages=messages,format=Question.model_json_schema())
            questions.append(json.loads(response['message']['content']))
        question_data = json.dumps(questions)
    else:
        completion = openai.chat.completions.create(model=model_name, messages=messages)
        question_data= completion.choices[0].message.content.strip()
        question_data = question_data.replace("```json", "")
        question_data = question_data.replace("```", "")
    
    
    
    print(question_data)
    json_result = json.loads(question_data)
    return json_result  # Convert the JSON string to a Python dictionary


