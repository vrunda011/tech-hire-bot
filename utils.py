"""Utility functions used by AI chatbot project."""
import re
import pandas as pd
import google.generativeai as genai
from langchain_core import messages


def get_question_ids(questionnaire: list[dict]):
    """Gets the question ids from questionnaire."""
    return [question["index"] for question in questionnaire]

def build_question_md(questionnaire, latest_answers, question_ids):
    """Renders questions and received answers as markdown table."""
    # Convert questions and answers to markdown table.
    qa_df = pd.DataFrame(data=questionnaire)
    qa_df.set_index("index", inplace=True)
    qa_df["answers"] = [
        latest_answers.get(question_id, "") for question_id in question_ids
    ]
    qa_md = qa_df.to_markdown()

    # Clean markdown.
    re_combine_lines = re.compile(r"---+")
    re_combine_whitespace = re.compile(r" +")

    qa_md = re_combine_lines.sub("---", qa_md)
    qa_md = re_combine_whitespace.sub(" ", qa_md)

    return qa_md

def get_structured_generation_config(required_properties: list[str], ai_response_key):
    """Returns a generation config to get structured output from gemini."""
    properties = {
        key: {"type": "string"} for key in required_properties + [ai_response_key]
    }
    gen_config = genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema={
            "type": "object",
            "properties": properties,
            "required": required_properties,
        },
    )
    return gen_config

def convert_history(history):
    """Converts chat history to the format required by Langchain."""
    history_langchain_format = []
    for msg in history:
        if msg["role"] == "user":
            history_langchain_format.append(
                messages.HumanMessage(content=msg["content"])
            )
        elif msg["role"] == "assistant":
            history_langchain_format.append(messages.AIMessage(content=msg["content"]))
    return history_langchain_format

def is_conversation_ended(latest_answers) -> bool:
    """Ends the conversation if all questions are answered."""
    if len(latest_answers.values()) != 0:
        tmp_list = [ele for ele in latest_answers.values() if ele == ""]
        if len(tmp_list) == 0:
            return True
    return False

def store_conversation(history, latest_answers, questionnaire, collection):
    """Stores the entire conversation in MongoDB Atlas in a clean Q&A format."""
    
    q_and_a = []
    
    for question in questionnaire:
        question_text = question.get("question", "Unknown question")
        question_id = question.get("index")
        answer_text = latest_answers.get(question_id, "No answer provided")  
        
        q_and_a.append({"question": question_text, "answer": answer_text})

    data = {
        "history": history,  
        "q_and_a": q_and_a   
    }

    result = collection.insert_one(data)
    print(f"Conversation stored successfully with ID: {result.inserted_id}")
