import ast
import os
import re

import google.generativeai as genai
import gradio as gr
import pandas as pd
from langchain_core import messages, prompts
import interview_prompt
import questionnaire

prompt = prompts.ChatPromptTemplate.from_messages(
    [
        (
            "system",
            interview_prompt.PROMPT,
        ),
        prompts.MessagesPlaceholder(variable_name="chat_history"),
    ]
)


def _get_question_ids(questionnaire: list[dict]):
    """Gets the question ids from questionnaire."""
    return [question["index"] for question in questionnaire]


question_ids = _get_question_ids(questionnaire=questionnaire.QUESTIONNAIRE)
latest_answers = dict()


def _build_question_md(questionnaire, latest_answers):
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


genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

ai_response_key = "next_ai_response_for_human"
required_properties = [question["index"] for question in questionnaire.QUESTIONNAIRE]


def _get_structured_generation_config(required_properties: list[str], ai_response_key):
    """Returns a generation config to get structured output from gemini."""
    properties = {
        key: {
            "type": "string",
        }
        for key in required_properties + [ai_response_key]
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


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=_get_structured_generation_config(
        required_properties, ai_response_key
    ),
)


# print(response_string)
def convert_history(history):
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


def predict(message, history):
    global latest_answers

    chat_history = convert_history(history)
    chat_history.append(messages.HumanMessage(content=message))

    prompt_text = prompt.format(
        chat_history=chat_history,
        questions=_build_question_md(questionnaire.QUESTIONNAIRE, latest_answers),
    )

    response = model.generate_content(prompt_text)
    response_string = response.text

    structured_response = ast.literal_eval(response_string)

    next_ai_response_for_human = structured_response.pop(ai_response_key)

    if not next_ai_response_for_human:
        next_ai_response_for_human = (
            "Sorry, I totally missed that. Can you please repeat?"
        )

    latest_answers = structured_response

    return next_ai_response_for_human


gr.ChatInterface(fn=predict, type="messages").launch()
