import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# --- 1. SETUP API KEY ---
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GOOGLE_API_KEY not found in environment!")
else:
    genai.configure(api_key=api_key)

class LLM:
    def __init__(self):
        # We use the standard gemini-pro model
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_answer_stream(self, question, context_chunks, chat_history):
        """
        Generates an answer for the chat window (Streaming).
        """
        # 1. Build context string
        context_text = "\n\n".join([chunk['text'] for chunk in context_chunks])
        
        # 2. Build history string (limit to last 5 messages to save tokens)
        history_text = ""
        for msg in chat_history[-5:]:
            sender = msg.get('sender', 'User')
            text = msg.get('text', '')
            history_text += f"{sender}: {text}\n"

        # 3. Create the Prompt
        prompt = f"""
        You are a helpful AI assistant named DocuMentor.
        Use the following context from a document to answer the user's question.
        
        CONTEXT:
        {context_text}

        CHAT HISTORY:
        {history_text}

        USER QUESTION: 
        {question}

        Answer:
        """

        # 4. Stream the response
        response = self.model.generate_content(prompt, stream=True)
        for chunk in response:
            if chunk.text:
                yield chunk.text

    async def summarize_conversation(self, chat_history):
        """
        Generates a summary for the PDF Export.
        """
        try:
            if not chat_history:
                return "No conversation to summarize."

            # 1. Convert chat history list to a single string
            conversation_text = ""
            for msg in chat_history:
                sender = msg.get('sender', 'Unknown')
                text = msg.get('text', '')
                conversation_text += f"{sender}: {text}\n"

            # 2. Create the Summary Prompt
            prompt = f"""
            Please provide a professional, concise summary of the following conversation between a User and an AI Assistant.
            Highlight the key questions asked and the main answers provided.
            
            CONVERSATION:
            {conversation_text}

            SUMMARY:
            """

            # 3. Generate (Not streaming, just standard wait)
            # We use `await` conceptually, but the library is synchronous, so we run it directly.
            response = self.model.generate_content(prompt)
            
            return response.text

        except Exception as e:
            print(f"SUMMARIZATION ERROR: {e}")
            return f"Error: Could not generate summary. Details: {e}"

# Create the single instance to be used by main.py
llm_instance = LLM()