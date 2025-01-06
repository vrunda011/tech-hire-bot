"""Interactive Gradio chatbot with Google Generative AI and MongoDB for interviews."""
import ast
import os

import google.generativeai as genai
import gradio as gr
from pymongo import MongoClient
from langchain_core import messages, prompts
import interview_prompt
import questionnaire
import utils
import constants

latest_answers = dict()

# Creating a database client
client = MongoClient(constants.MONGO_URI)
db = client[constants.DB_NAME]
collection = db[constants.COLLECTION_NAME]

# Configure Google Generative AI with the provided API key
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the generative model
required_properties = [question["index"] for question in questionnaire.QUESTIONNAIRE]

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=utils.get_structured_generation_config(
        required_properties, constants.AI_RESPONSE_KEY
    ),
)

# Creating a chat prompt template
prompt = prompts.ChatPromptTemplate.from_messages(
    [
        ("system", interview_prompt.PROMPT),
        prompts.MessagesPlaceholder(variable_name="chat_history"),
    ]
)

question_ids = utils.get_question_ids(questionnaire=questionnaire.QUESTIONNAIRE)

def predict(message, history):
    """Predicts the next AI response based on user input."""
    global latest_answers

    chat_history = utils.convert_history(history)
    chat_history.append(messages.HumanMessage(content=message))

    prompt_text = prompt.format(
        chat_history=chat_history,
        questions=utils.build_question_md(questionnaire.QUESTIONNAIRE, latest_answers, question_ids),
    )

    response = model.generate_content(prompt_text)
    response_string = response.text

    structured_response = ast.literal_eval(response_string)
    next_ai_response_for_human = structured_response.pop(constants.AI_RESPONSE_KEY)

    if not next_ai_response_for_human:
        next_ai_response_for_human = (
            "Sorry, I totally missed that. Can you please repeat?"
        )

    latest_answers = structured_response

    if utils.is_conversation_ended(latest_answers):
        print("Conversation ended. Storing conversation...")
        utils.store_conversation(history, latest_answers, questionnaire.QUESTIONNAIRE, collection)

    return next_ai_response_for_human


# Launch the Gradio Chat Interface
gr.ChatInterface(
    fn=predict,
    type="messages",
    chatbot=gr.Chatbot(
        placeholder='<strong>Welcome to TalentScout</strong><br>Our smart assistant streamlines your tech hiring process by gathering key details and assessing your skills for the best job matches.<br>Say <strong>"Hello"</strong> to begin!'
    ),
).launch()
