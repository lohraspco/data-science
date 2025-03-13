from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

class Chatbot:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.message_history = []
        self.chain = self.llm.bind(stop=["\nHuman:", "\n\nHuman:"])
        
    async def get_response(self, message: str) -> str:
        """
        Get a response from the chatbot for the given message.
        
        Args:
            message (str): The user's input message
            
        Returns:
            str: The chatbot's response
        """
        try:
            # Add user message to history
            self.message_history.append(HumanMessage(content=message))
            
            # Get response from model
            response = await self.chain.ainvoke(self.message_history)
            
            # Add AI response to history
            self.message_history.append(AIMessage(content=response.content))
            
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def clear_memory(self):
        """Clear the conversation memory."""
        self.message_history = [] 