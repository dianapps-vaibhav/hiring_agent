from openai import OpenAI
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks import StreamlitCallbackHandler
import uuid
from datetime import datetime
from typing import Dict, Any
import random

class AIService:
    def __init__(self, db_client):
        self.db_client = db_client
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.7
        )
        
        # Add job selection responses
        self.job_selection_responses = [
            "Great choice! I'd be happy to help you with your application for the {job_title} position. To get started, could you tell me about your relevant experience?",
            "Excellent! The {job_title} role is an exciting opportunity. To help with your application, could you share your background in this field?",
            "Perfect! I'll help you explore the {job_title} position. First, I'd love to hear about your experience and skills that align with this role.",
            "Wonderful choice! Let's discuss your application for the {job_title} position. Could you start by telling me about your relevant work experience?",
        ]
        
        # Add candidate information gathering prompts
        self.info_gathering_prompts = {
            'experience': [
                "Could you elaborate on your experience with {skill}?",
                "What specific projects have you worked on that relate to {skill}?",
                "How many years of experience do you have with {skill}?"
            ],
            'education': [
                "Could you tell me about your educational background?",
                "What relevant certifications or degrees do you hold?",
            ],
            'skills': [
                "What technical skills would you highlight for this role?",
                "Could you describe your proficiency with the required technologies?",
            ]
        }
        
        # Initial greeting variations
        self.initial_greetings = [
            "Welcome! I see you're exploring opportunities with us. Take a look at our open positions on the right and let me know which one catches your eye!",
            "Hello there! Ready to start an exciting career journey? Browse through our available positions and tell me which role interests you.",
            "Hi! Thanks for stopping by. Check out our current openings on the right - I'd love to help you find your perfect role!",
            "Great to meet you! I'm here to help you land your ideal position. Have any of our current openings caught your attention?",
            "Welcome aboard! Let's find you an amazing opportunity. Take a peek at our open positions and let me know which one speaks to you."
        ]
        
        # Role selection prompt variations
        self.role_selection_prompts = [
            "Which position would you like to learn more about?",
            "Have you spotted a role that interests you?",
            "Which of our open positions aligns with your career goals?",
            "See any roles that match what you're looking for?",
            "Which opportunity would you like to explore further?"
        ]
        
        # Initialize or get session ID
        if 'session_id' not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
        self.memory = ConversationBufferMemory(
            memory_key="history",
            input_key="input",
            return_messages=True
        )
        
        prompt = PromptTemplate(
            input_variables=["history", "input"],
            template="""You are AI hiring assistant named 'Recruiter'. Follow these guidelines:

1. Response Style:
   - Be professional yet friendly and conversational
   - Use varied language and expressions
   - Include appropriate emojis occasionally
   - Keep responses concise and focused

2. Initial Interaction:
   - If user hasn't selected a role, encourage them to browse positions
   - Vary your responses while maintaining the same core message
   - Don't repeat exact phrases from previous messages

3. After Role Selection:
   - Guide the conversation to gather key information:
     * Relevant experience
     * Technical skills
     * Educational background
     * Current work situation
   - Ask one question at a time
   - Keep the conversation flowing naturally

Current conversation:
{history}
        
Human: {input}
Assistant: """
        )
        
        self.chain = ConversationChain(
            llm=self.llm,
            prompt=prompt,
            memory=self.memory,
            verbose=False
        )

    def generate_career_response(self, user_input, message_history, user_context):
        """Generate varied responses based on conversation state"""
        
        # Handle new job selection
        if st.session_state.get('selected_job') and not st.session_state.get('job_acknowledged'):
            st.session_state.job_acknowledged = True
            return random.choice(self.job_selection_responses).format(
                job_title=st.session_state.selected_job
            )
        
        # If this is a new conversation or generic greeting
        if not message_history or len(message_history) <= 1:
            if self._is_greeting(user_input.lower()):
                return random.choice(self.initial_greetings)
        
        # If no role selected yet
        if not st.session_state.get('selected_job'):
            if self._is_greeting(user_input.lower()) or self._is_generic_response(user_input.lower()):
                return f"{random.choice(self.initial_greetings)} {random.choice(self.role_selection_prompts)}"
        
        # Continue with normal conversation flow for other cases
        if message_history and len(message_history) > 1:
            for msg in message_history[1:]:
                if msg["role"] == "user":
                    self.memory.chat_memory.add_user_message(msg["content"])
                elif msg["role"] == "assistant":
                    self.memory.chat_memory.add_ai_message(msg["content"])
        
        response = self.chain.run(input=user_input)
        return response

    def _is_greeting(self, text):
        """Check if input is a greeting"""
        greetings = {'hi', 'hello', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening'}
        return any(greeting in text.lower() for greeting in greetings)

    def _is_generic_response(self, text):
        """Check if input is a generic response"""
        generic_responses = {'ok', 'okay', 'sure', 'yes', 'no', 'thanks', 'thank you'}
        return any(response in text.lower() for response in generic_responses)

    def get_chat_response(self, messages, temperature=0.7, max_tokens=150):
        """
        Legacy method for direct OpenAI API calls (can be used as fallback)
        """
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
