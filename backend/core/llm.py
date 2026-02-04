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
        # Using the high-quota model
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_answer_stream(self, question, context_chunks, chat_history):
        """
        Generates an answer for the chat window (Streaming).
        """
        # --- FIX STARTS HERE ---
        # Robustly handle context whether it's a list of strings OR dictionaries
        context_parts = []
        for chunk in context_chunks:
            if isinstance(chunk, str):
                context_parts.append(chunk)
            elif isinstance(chunk, dict):
                context_parts.append(chunk.get('text', ''))
            else:
                context_parts.append(str(chunk))
        
        context_text = "\n\n".join(context_parts)
        # --- FIX ENDS HERE ---
        
        # 2. Build history string (limit to last 5 messages)
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
        try:
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"LLM STREAM ERROR: {e}")
            yield "I'm sorry, I encountered an error while generating the response."

    async def summarize_conversation(self, chat_history):
        """
        Generates a summary for the PDF Export.
        """
        try:
            if not chat_history:
                return "No conversation to summarize."

            conversation_text = ""
            for msg in chat_history:
                sender = msg.get('sender', 'Unknown')
                text = msg.get('text', '')
                conversation_text += f"{sender}: {text}\n"

            prompt = f"""
            Please provide a professional, concise summary of the following conversation.
            
            CONVERSATION:
            {conversation_text}

            SUMMARY:
            """

            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            print(f"SUMMARIZATION ERROR: {e}")
            return f"Error: Could not generate summary. Details: {e}"

llm_instance = LLM()