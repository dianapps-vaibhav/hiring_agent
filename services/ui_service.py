import streamlit as st
from datetime import datetime

class UIService:
    def __init__(self, job_service):
        self.job_service = job_service

    def display_chat_messages(self, messages):
        """
        Display chat messages in Streamlit
        """
        for message in messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    def display_open_positions(self):
        """Display all open positions in a dedicated section"""
        st.header("📋 Open Positions")
        
        # Get all jobs from the job service
        all_jobs = self.job_service.match_jobs("")  # Empty string to get all jobs
        st.write(f"DEBUG: Found {len(all_jobs)} jobs")  # Debug print
        
        if not all_jobs:
            st.warning("No jobs found in the database. Please add some jobs first.")
            return
            
        # Create columns for job categories
        cols = st.columns(3)
        
        # Group jobs by category
        jobs_by_category = {}
        for job in all_jobs:
            categories = job.get('categories', ['Uncategorized'])
            if isinstance(categories, str):
                categories = [categories]  # Convert string to list if necessary
            
            for category in categories:
                if category not in jobs_by_category:
                    jobs_by_category[category] = []
                jobs_by_category[category].append(job)
        
        st.write(f"DEBUG: Categories found: {list(jobs_by_category.keys())}")  # Debug print
        
        # Distribute categories across columns
        categories = list(jobs_by_category.keys())
        for idx, category in enumerate(categories):
            col_idx = idx % 3
            with cols[col_idx]:
                st.subheader(category)
                for job in jobs_by_category[category]:
                    with st.expander(f"{job['title']} - {job.get('location', 'No location')}"):
                        st.write(f"**Type:** {job.get('type', 'Not specified')}")
                        if job.get('description'):
                            st.write("**Description:**")
                            st.write(job['description'][:200] + "..." if len(job['description']) > 200 else job['description'])
                        if job.get('apply_url'):
                            st.write(f"[Apply Here]({job['apply_url']})")
                        if st.button("Learn More", key=f"learn_more_{job['title']}_{idx}"):
                            st.session_state.selected_job = job['title']

    def display_jobs(self, matched_jobs):
        """
        Display matched jobs in sidebar
        """
        if matched_jobs:
            st.sidebar.header("Matching Jobs")
            for idx, job in enumerate(matched_jobs):
                with st.sidebar.expander(f"{job['title']} - {job['location']}"):
                    st.write(f"Type: {job['type']}")
                    st.write(f"Categories: {', '.join(job['categories'])}")
                    if job.get('description'):
                        st.write("Description:")
                        st.write(job['description'][:200] + "..." if len(job['description']) > 200 else job['description'])
                    if job.get('apply_url'):
                        st.write(f"[Apply Here]({job['apply_url']})")
                    if st.button("Apply Now", key=f"apply_button_{idx}_{job['title']}"):
                        st.session_state.application_stage = job['title']

    def display_application_form(self, user_id):
        """
        Display and handle job application form
        """
        with st.form("job_application"):
            st.write("### Job Application Form")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            experience = st.text_area("Relevant Experience")
            resume_url = st.text_input("Resume Link (Optional)")
            
            submitted = st.form_submit_button("Submit Application")
            
            if submitted and full_name and email and phone:
                application_data = {
                    "user_id": user_id,
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "experience": experience,
                    "resume_url": resume_url,
                    "submission_date": datetime.utcnow(),
                    "status": "submitted"
                }
                self.job_service.save_application(application_data)
                st.success("Application submitted successfully!")
                return True
        return False
