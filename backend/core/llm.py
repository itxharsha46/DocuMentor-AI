# backend/core/llm.py

import google.generativeai as genai
from typing import AsyncGenerator, List, Dict

class GeminiLLM:
    def __init__(self, model_name="gemini-2.5-flash"):
        # CHANGED: Switched to 2.5-flash to bypass the 2.0 quota limit
        print(f"Initializing Gemini LLM with model: {model_name}")
        self.model = genai.GenerativeModel(model_name)
        print("Gemini LLM initialized.")

    def _format_chat_history(self, chat_history: List[Dict[str, str]]) -> str:
        if not chat_history:
            return "No previous conversation history."
        formatted_history = []
        for message in chat_history:
            role = "User" if message.get('sender') == 'user' else "Assistant"
            formatted_history.append(f"{role}: {message.get('text')}")
        return "\n".join(formatted_history)

    async def generate_answer_stream(
        self, 
        question: str, 
        context_chunks: list[str],
        chat_history: List[Dict[str, str]]
    ) -> AsyncGenerator[str, None]:
        if not context_chunks:
            yield "I could not find any relevant information in the document to answer your question."
            return

        context_str = "\n---\n".join(context_chunks)
        history_str = self._format_chat_history(chat_history)

        prompt = f"""
        You are a helpful assistant for DocuMentor AI.
        Your goal is to answer the user's "CURRENT QUESTION" based *only* on the provided "DOCUMENT CONTEXT".
        
        **Instructions:**
        1. Answer directly and clearly.
        2. Do not use outside knowledge.
        3. Suggest 2-3 follow-up questions at the end.

        ---
        CHAT HISTORY:
        {history_str}
        ---
        DOCUMENT CONTEXT:
        {context_str}
        ---
        CURRENT QUESTION:
        {question}
        ---
        ANSWER:
        """
        
        print("Generating streamed answer...")
        try:
            response_stream = await self.model.generate_content_async(prompt, stream=True)
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            print(f"Error during LLM stream generation: {e}")
            yield f"An error occurred while generating the answer: {e}"

    async def summarize_conversation(self, chat_history: List[Dict[str, str]]) -> str:
        """
        Generates a summary of the conversation for the PDF report.
        """
        print("Generating conversation summary...")
        
        history_text = self._format_chat_history(chat_history)
        
        prompt = f"""
        You are a professional technical writer. 
        Create a structured summary of the following Q&A conversation about a document.
        Focus on the key insights and answers provided.
        Do NOT use emojis or special characters. Keep the text clean and professional.
        
        CONVERSATION:
        {history_text}
        
        SUMMARY:
        """
        
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            print(f"Summary generation failed: {e}")
            return "Could not generate summary due to an AI error."

llm_instance = GeminiLLM()