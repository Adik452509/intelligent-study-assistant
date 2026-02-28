from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import traceback

load_dotenv()

class StudyChatbot:
    def __init__(self):
        print("Initializing chatbot...")
        
        # Create base endpoint
        llm = HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",  # Works well with chat
            temperature=0.7,
            max_new_tokens=512,
        )
        
        # Wrap with ChatHuggingFace
        self.llm = ChatHuggingFace(llm=llm)
        
        # Use ChatPromptTemplate for chat models
        self.prompt = ChatPromptTemplate.from_template(
            """You are a helpful study assistant. Answer the student's question clearly and concisely.

Context: {context}
Question: {question}

Answer:"""
        )
        
        self.chain = self.prompt | self.llm
        print("✅ Chatbot ready!")
    
    def ask(self, question, context=""):
        """Ask a question to the chatbot"""
        try:
            print(f"Processing: {question}")
            response = self.chain.invoke({
                "question": question,
                "context": context
            })
            # Extract content from AIMessage
            return response.content.strip()
        except Exception as e:
            print(f"\n❌ FULL ERROR DETAILS:")
            print(f"Error: {str(e)}")
            traceback.print_exc()
            return f"Error: {str(e)}"

if __name__ == "__main__":
    try:
        chatbot = StudyChatbot()
        response = chatbot.ask("What is machine learning?")
        print("\n" + "="*60)
        print("Response:")
        print(response)
        print("="*60)
    except Exception as e:
        print(f"\n❌ Critical error:")
        traceback.print_exc()