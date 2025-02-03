from ollama import chat
from pydantic import BaseModel
import json


system_message ="""You are an expert education teacher who teaches students about a specific 
        subject for class XI and class XII.You will be given a subject and a difficulty level, 
        and you will generate a set of multiple-choice question for that subject with that difficulty level."""


class Question(BaseModel):
    question: str
    options: list[str]
    correct_answer: str


def generate_questions(subject, difficulty,num_questions=10,use_ollama=False):
    
    prompt = (
        f"Generate a multiple-choice question about "
        f"{subject} with difficulty level {difficulty}. "
        "Format the response as JSON with the following structure: "
        "{\"question\": \"...\", \"options\": [\"A. ...\", \"B. ...\", \"C. ...\", \"D. ...\"], "
        "\"correct_answer\": \"A/B/C/D\"}"
    )

    messages =[
        {"role":"system","content":system_message},
        {"role":"user","content":prompt }
    ]
    # model_name="llama3.2"
    model_name="deepseek-r1:1.5b"
    questions=[]
    for i in range(num_questions):
        response =chat(model=model_name, messages=messages,format=Question.model_json_schema())
        questions.append(Question.model_validate_json(response['message']['content']))
    return questions


if __name__ == "__main__":
    questions = generate_questions("Mathematics - Class XII  - Probability - IIT JEE", "medium", 4,use_ollama=True)
    question_data = json.dumps([q.dict() for q in questions])
    print(question_data)
    
    i=1
    for  q in questions:
        print(i,q.question, q.options, q.correct_answer)
        i+=1
        print("\n")
    
