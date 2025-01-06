# Hiring Assistant Chatbot

## Project Overview
The Hiring Assistant chatbot is designed to streamline technical interviews by acting as a personal talent scout. It can conduct interactive Q&A sessions, generate structured responses, and store the entire conversation in a MongoDB database.

## Installation Instructions
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd tech-hire-bot
2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use venv\Scripts\activate
3. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
4. **Set up environment variables:**
   To get the Key: [URL](https://aistudio.google.com/prompts/new_chat)
   ```bash
   GOOGLE_API_KEY: Your Google Generative AI API key.
   
6. **Run the Application:**
   ```bash
   python main.py

## Usage Guide
1. Launch the application by running python main.py.
2. Open the displayed local URL in your web browser.
3. Interact with the chatbot by typing your questions.

## Technical Details
**Libraries Used**
- Google Generative AI: For generating human-like responses.
- Gradio: To create an intuitive web-based interface.
- Pandas: For tabular data manipulation.
- PyMongo: To interact with MongoDB Atlas for storing conversation history.
- LangChain Core: For prompt management and message handling.
  
## Model Details
- Generative Model: Gemini-2.0-flash-exp with structured generation configuration.
  
## Architectural Decisions
- The chatbot uses a predefined set of questions stored in questionnaire.py.
- MongoDB Atlas is used to store conversation history for later review and analysis.
  
## Prompt Design
Prompts were carefully crafted to handle both information gathering and technical question generation. A system prompt initializes the conversation, followed by user and AI messages to maintain context.


## Challenges & Solutions

1. **Structured Response Parsing:**
   - Challenge: Ensuring the AI response is in a structured JSON format.
   - Solution: Used genai.GenerationConfig with a response schema to enforce the structure.
  
2. **Conversation Storage:**
   - Challenge: Storing and retrieving conversations in a scalable way.
   - Solution: MongoDB Atlas was chosen for its flexibility and scalability.
  
## Future Enhancements
- Add support for more interview topics.
- Improve the chatbot’s conversational capabilities using advanced NLP models.
- Provide analytics on past conversations.
