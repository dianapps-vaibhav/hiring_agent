import streamlit as st
from dotenv import load_dotenv
import os
import uuid
from database import Database
from services.ai_service import AIService
from services.job_service import JobService
from services.ui_service import UIService

# Load environment variables
load_dotenv()

def apply_custom_styles():
    st.markdown("""
        <style>
        .stTextInput input {
            border-radius: 2rem;
            padding-left: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def display_chat():
    # Create a container for messages
    chat_container = st.container()
    
    # Display messages in the container
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "assistant":
                with st.chat_message("assistant", avatar="👩‍💼"):
                    st.write(message["content"])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.write(message["content"])

def main():
    apply_custom_styles()
    
    # Initialize services
    db = Database()
    job_service = JobService(db)
    ui_service = UIService(job_service)
    ai_service = AIService(db_client=db)
    
    # Initialize additional session state variables
    if 'job_acknowledged' not in st.session_state:
        st.session_state.job_acknowledged = False
    
    # Create three columns with custom widths
    tips_col, chat_col, jobs_col = st.columns([0.25, 0.45, 0.30])
    
    # Left column - Tips and Guidelines
    with tips_col:
        st.markdown("### 💡 Tips & Guidelines")
        st.markdown("---")
        
        st.markdown("""
        **Getting Started:**
        1. Browse available positions
        2. Click 'I'm Interested' on roles you like
        3. Chat with our AI assistant
        
        **Tips for Success:**
        - Be specific about your experience
        - Ask questions about the role
        - Share your relevant skills
        - Discuss your career goals
        """)
        
        st.markdown("---")
    
    # Middle column - Chat Interface
    with chat_col:
        st.title("Careers Assistant 👩‍💼")
        st.markdown("---")
        
        # Initialize session state for messages if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        # Display chat messages
        display_chat()
        
        # Chat input
        if prompt := st.chat_input("Type your message here...", key="chat_input"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            response = ai_service.generate_career_response(
                user_input=prompt,
                message_history=st.session_state.messages,
                user_context={}
            )
            
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Right column - Jobs Display
    with jobs_col:
        st.markdown("### 📋 Available Positions")
        st.markdown("---")
        
        # Search box for jobs
        search_term = st.text_input("🔍 Search positions", key="job_search")
        
        # Get all jobs
        all_jobs = job_service.match_jobs(search_term)
        
        if not all_jobs:
            st.info("No positions are currently available.")
        else:
            for idx, job in enumerate(all_jobs):
                with st.expander(f"🔸 {job['title']}", expanded=False):
                    st.markdown(f"""
                        **Location:** {job.get('location', 'Not specified')}  
                        **Type:** {job.get('type', 'Not specified')}
                    """)
                    
                    if job.get('description'):
                        st.markdown("**Description:**")
                        description = job['description']
                        if len(description) > 150:
                            st.markdown(f"{description[:150]}...")
                        else:
                            st.markdown(description)
                    
                    # Make the "I'm Interested" button more prominent
                    if st.button("📝 I'm Interested in This Role", 
                               key=f"interest_{idx}_{job['title']}", 
                               use_container_width=True):
                        st.session_state.selected_job = job['title']
                        st.session_state.job_acknowledged = False
                        st.session_state.application_stage = 'initial'
                        
                        # Add the job selection message
                        st.session_state.messages.append({
                            "role": "system",
                            "content": f"You have selected the {job['title']} position."
                        })
                        
                        # Immediately add the name request message
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Great choice! I'll help you with your application for the {job['title']} position. To get started, could you please tell me your full name?"
                        })
                        
                        st.rerun()

if __name__ == "__main__":
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Welcome! 👋 Please take a look at our available positions on the right and select the role you're interested in. I'll help guide you through the application process."
        }]
    
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    
    if "application_stage" not in st.session_state:
        st.session_state.application_stage = None
    
    st.set_page_config(
        page_title="Careers Assistant",
        page_icon="💼",
        layout="wide"
    )
    main()

