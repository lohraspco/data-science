from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = None
        self.llm = ChatOpenAI(
            temperature=0.7,
            model_name="gpt-3.5-turbo",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.chain = None

    async def load_documents(self, directory: str):
        """
        Load documents from a directory and create the vector store.
        
        Args:
            directory (str): Path to the directory containing documents
        """
        try:
            # Load documents from directory
            loader = DirectoryLoader(
                directory,
                glob="**/*.txt",  # Adjust pattern based on your document types
                show_progress=True
            )
            documents = loader.load()

            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            texts = text_splitter.split_documents(documents)

            # Create vector store
            self.vector_store = FAISS.from_documents(texts, self.embeddings)

            # Create RAG chain
            prompt = ChatPromptTemplate.from_messages([
                ("system", "Answer the question based on the following context:\n\n{context}"),
                ("human", "{question}")
            ])

            self.chain = (
                {"context": self.vector_store.as_retriever(), "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
            )
        except Exception as e:
            raise ValueError(f"Error loading documents: {str(e)}")

    async def get_response(self, query: str) -> str:
        """
        Get a response for the given query using RAG.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The system's response
        """
        try:
            if self.chain is None:
                raise ValueError("Documents not loaded yet")

            response = await self.chain.ainvoke(query)
            return response
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"

    def clear_vector_store(self):
        """Clear the vector store."""
        self.vector_store = None
        self.chain = None 