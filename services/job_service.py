from database import Database

class JobService:
    def __init__(self, db: Database):
        self.db = db

    def get_all_jobs(self):
        """Get all jobs from the database"""
        jobs = self.db.get_all_jobs()
        print(f"Retrieved {len(jobs)} jobs from database: {jobs}")  # Debug print
        return jobs

    def match_jobs(self, query):
        """Match jobs based on query"""
        if not query:
            return self.get_all_jobs()
        
        criteria = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"location": {"$regex": query, "$options": "i"}},
                {"categories": {"$regex": query, "$options": "i"}}
            ]
        }
        jobs = self.db.get_jobs_by_criteria(criteria)
        print(f"Matched {len(jobs)} jobs for query '{query}': {jobs}")  # Debug print
        return jobs

    def save_application(self, application_data):
        """
        Save job application to database
        """
        return self.db.save_application(application_data)

    def save_interaction(self, user_id, user_input, response):
        """
        Save user interaction to database
        """
        return self.db.save_user_interaction(user_id, user_input, response)

    def get_user_context(self, user_id):
        """
        Get user context from database
        """
        return self.db.get_user_context(user_id)
