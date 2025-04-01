
import uuid
from openai import OpenAI
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks import StreamlitCallbackHandler
from models.session_data import SessionDataManager
from typing import Optional
import re

class AIService:
    def __init__(self, db_client=None):
        self.db = db_client
        self.session_manager = SessionDataManager()

        # Get available jobs from database
        self.available_jobs = self.db.get_all_jobs() if self.db else []
        
        # Configure DeepSeek client
        self.client = OpenAI(
            base_url="https://api.deepseek.com",  # DeepSeek API endpoint
            api_key=st.secrets.get("DEEPSEEK_API_KEY", "")  # Use DeepSeek API key
        )
        
        # Update LangChain to use DeepSeek
        self.llm = ChatOpenAI(
            model="deepseek-chat",  # Use DeepSeek model
            temperature=0.7,
            openai_api_key=st.secrets.get("DEEPSEEK_API_KEY", ""),
            openai_api_base="https://api.deepseek.com"
        )
        
        # Initialize or get session ID
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        # Format available jobs text
        self.available_jobs_text = "\n".join([f"- {job['title']}" for job in self.available_jobs])

        # Initialize memory with return_messages=True and input/output keys
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="history",
            input_key="input"
        )

        # Create prompt template
        self.prompt = PromptTemplate(
            input_variables=["history", "input"],  # Remove available_jobs_text from input_variables
            template="""You are AI hiring assistant named 'Recruiter'. 

Available Positions in right tab:
""" + self.available_jobs_text + """

Follow these guidelines:

1. Response Style:
   - Only english language required. If user provides any other language politely ask them to use english language.
   - Use a short sentenses
   - Do not allow slangs or sour words. Politely ask user to provide correct information.
   - Be professional yet friendly and conversational
   - Use varied expressions
   - Include appropriate emojis occasionally
   - Keep responses concise and focused

2. Job Selection Rules:
   - ONLY accept job selections from the above list of available positions
   - If user mentions any job not from the above list, say: "I don't see that position in our current openings. Please check the available positions in the right tab and click 'I'm Interested' on the role you'd like to apply for. 🎯"
   - Do not proceed with any job-related questions until a valid selection is made from the available positions

3. Initial Interaction:
   - If user hasn't selected a role, encourage them to browse positions
   - Vary your responses while maintaining the same core message
   - Don't repeat exact phrases from previous messages

4. After Role Selection:
   - Guide the conversation to gather key information:
     * Full Name
     * Phone Number
     * Email Address
     * Age is greater then 16 or not (If below 16 then they are not eligible for the post,don't ask any further questions)
     * Can they work in USA or not (If not then they are not eligible for the post,don't ask any further questions)
     * Which shift they prefer (Morning or Night)
     * Confortable with a fast paced environment or not (If not then they are not eligible for the post,don't ask any further questions)
     * How to connect with them (via phone or email). This is the last question (Don't ask anything after that)
   - Ask one question at a time
   - Keep the conversation flowing naturally
   - Flow should be same as mentioned above. If user tries to navigate the flow then guide them back to the flow.
5. After key information gathering
    - Tell them that a 20 minute interview is scheduled at a time of their convenience after connecting with them if they provide all key information and all eligiblity passes else tell them that they are not eligible for the post.
    - After this everytime user asks anything tell them that their interview is already scheduled or they are not eligible for the post.

Current conversation:
{history}
        
Human: {input}
Assistant: """
        )

        # Initialize conversation chain
        self.chain = ConversationChain(
            llm=self.llm,
            prompt=self.prompt,
            memory=self.memory,
            verbose=False
        )

    def generate_career_response(
        self, 
        user_input: str, 
        message_history: list = None,
        user_context: dict = None,
        session_id: str = None
    ) -> str:
        if session_id is None:
            session_id = st.session_state.session_id
            
        user_data = self.session_manager.get_user_data(session_id)

        # Update conversation memory with message history if provided
        if message_history:
            for msg in message_history:
                if msg["role"] == "user":
                    self.memory.save_context(
                        {"input": msg["content"]}, 
                        {"output": ""}
                    )
                elif msg["role"] == "assistant":
                    self.memory.save_context(
                        {"input": ""}, 
                        {"output": msg["content"]}
                    )
        
        # Generate response using the conversation chain
        response = self.chain.invoke(
            {
                "input": user_input
            }
        )
        
        return response["response"]

    def _is_greeting(self, text):
        """Check if input is a greeting"""
        messages = [
            SystemMessage(content="You are a classifier that responds with only 'true' or 'false'. Determine if the following text is a greeting response (like 'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', etc.)."),
            HumanMessage(content=text.lower())  # Call lower() here
        ]
        
        response = self.llm.invoke(messages)
        return response.content.lower().strip() == 'true'

    def _is_generic_response(self, text: str) -> bool:
        """Check if input is a generic response using GPT"""
        messages = [
            SystemMessage(content="You are a classifier that responds with only 'true' or 'false'. Determine if the following text is a generic/basic response (like 'ok', 'yes', 'thanks', etc.)."),
            HumanMessage(content=text.lower())  # Call lower() here
        ]
        
        response = self.llm.invoke(messages)
        return response.content.lower().strip() == 'true'

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text using regex"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def _extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from text using regex"""
        phone_pattern = r'\b\d{10,12}\b'
        match = re.search(phone_pattern, text)
        return match.group(0) if match else None

    def get_collected_data(self, session_id: str) -> dict:
        """Get all collected data for a session"""
        return self.session_manager.get_user_data(session_id).to_dict()

