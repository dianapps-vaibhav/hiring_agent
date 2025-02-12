# Copyright 2024-present MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Re-import of synchronous Database API for compatibility."""
from __future__ import annotations

from pymongo.synchronous.database import *  # noqa: F403
from pymongo.synchronous.database import __doc__ as original_doc

__doc__ = original_doc
__all__ = ["Database"]  # noqa: F405

from pymongo import MongoClient
import streamlit as st
from datetime import datetime

class Database:
    def __init__(self):
        # Try to get MongoDB URI from Streamlit secrets, fallback to default local URI
        try:
            self.mongo_uri = st.secrets["MONGODB_URI"]
        except:
            self.mongo_uri = "mongodb://localhost:27017/"
        
        # Initialize MongoDB client and database
        self.client = MongoClient(self.mongo_uri)
        self.db = self.client.hiring_agent_db  # database name
        
    def get_all_jobs(self):
        """Retrieve all jobs from the database"""
        return list(self.db.jobs.find())
    
    def get_jobs_by_criteria(self, criteria):
        """Retrieve jobs matching specific criteria"""
        return list(self.db.jobs.find(criteria))
    
    def add_job(self, job_data):
        """Add a single job to the database"""
        return self.db.jobs.insert_one(job_data)
    
    def add_jobs(self, jobs_data):
        """Add multiple jobs to the database"""
        return self.db.jobs.insert_many(jobs_data)
    
    def clear_jobs(self):
        """Remove all jobs from the database"""
        return self.db.jobs.delete_many({})
    
    def get_job_by_id(self, job_id):
        """Retrieve a specific job by its ID"""
        return self.db.jobs.find_one({"_id": job_id})
    
    def update_job(self, job_id, update_data):
        """Update a specific job"""
        return self.db.jobs.update_one({"_id": job_id}, {"$set": update_data})
    
    def delete_job(self, job_id):
        """Delete a specific job"""
        return self.db.jobs.delete_one({"_id": job_id})
    
    def get_user_context(self, user_id):
        """Retrieve user context from the database"""
        user_context = self.db.user_contexts.find_one({"user_id": user_id})
        if not user_context:
            # Initialize empty context if none exists
            user_context = {
                "user_id": user_id,
                "preferences": {},
                "last_interaction": None,
                "application_stage": None,
                "selected_job": None
            }
            self.db.user_contexts.insert_one(user_context)
        return user_context
    
    def save_user_interaction(self, user_id, user_input, assistant_response):
        """Save user interaction to the database"""
        interaction = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "user_input": user_input,
            "assistant_response": assistant_response
        }
        self.db.interactions.insert_one(interaction)
        
        # Update last interaction in user context
        self.db.user_contexts.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_interaction": datetime.utcnow()
                }
            },
            upsert=True
        )
