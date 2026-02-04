import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

class LLM:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is missing")
        
        genai.configure(api_key=api_key)
        
        # FIX: Use the specific, stable version name
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    async def generate_answer_stream(self, question, context_chunks, chat_history):
        """Streams the answer from Gemini based on context."""
        
        # 1. ROBUST CHUNK HANDLING
        # This fixes the "AttributeError: 'str' object has no attribute 'page_content'"
        processed_chunks = []
        for chunk in context_chunks:
            if isinstance(chunk, str):
                processed_chunks.append(chunk)
            elif hasattr(chunk, 'page_content'):
                processed_chunks.append(chunk.page_content)
            else:
                processed_chunks.append(str(chunk))
                
        context_text = "\n\n".join(processed_chunks)
        
        # 2. SYSTEM PROMPT
        prompt = f"""You are a helpful document assistant. Use the following context to answer the user's question.
        
        Context:
        {context_text}
        
        Chat History:
        {chat_history}
        
        User Question: {question}
        
        Answer:"""
        
        try:
            # stream=True is standard for chat interfaces
            response = self.model.generate_content(prompt, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            # This sends the error to the chat window so you can see it
            yield f"Error generating answer: {str(e)}"

    async def summarize_conversation(self, chat_history):
        """Generates a concise summary of the chat history."""
        try:
            if not chat_history:
                return "No conversation to summarize."

            history_text = "\n".join([f"{msg['sender']}: {msg['text']}" for msg in chat_history])
            
            prompt = f"""Summarize this conversation in bullet points:
            
            {history_text}"""
            
            response = self.model.generate_content(prompt)
            
            return response.text if response.text else "Empty summary."

        except Exception as e:
            print(f"!!! SUMMARIZATION ERROR: {e}")
            return f"Error: {str(e)}"

# Create the singleton instance
llm_instance = LLM()