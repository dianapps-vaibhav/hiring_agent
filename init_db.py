from database import Database
import json

def transform_job(job_data):
    """Transform the job data from jd.json format to our database format"""
    # Extract location information
    location_str = job_data.get('location', '')
    
    return {
        "title": job_data.get('job_title', ''),
        "location": location_str,
        "type": job_data.get('employment_types', ['FULL_TIME'])[0] if job_data.get('employment_types') else 'FULL_TIME',
        "description": job_data.get('description', ''),
        "categories": job_data.get('categories', []),
        "requisition_id": job_data.get('requisition_id', ''),
        # New fields added
        "apply_url": job_data.get('apply_url', ''),
        "employment_types": job_data.get('employment_types', []),
        "job_location": job_data.get('js_result_data', {}).get('job_location', [])[0] if job_data.get('js_result_data', {}).get('job_location') else {},
    }

def init_jobs():
    db = Database()
    
    # Clear existing jobs
    db.db.jobs.delete_many({})
    
    try:
        # Read jobs from jd.json
        with open('jd.json', 'r') as file:
            json_data = json.load(file)
            
        # Get jobs from the data array
        jobs = json_data.get('data', [])
        
        if not jobs:
            print("No jobs found in the data array!")
            return
            
        # Transform and insert jobs
        transformed_jobs = [transform_job(job) for job in jobs]
        db.db.jobs.insert_many(transformed_jobs)
            
        print("Database initialized with jobs from jd.json!")
        
        # Print summary of imported jobs
        jobs_count = db.db.jobs.count_documents({})
        print(f"Total jobs imported: {jobs_count}")
        
        # Print sample job titles
        print("\nImported job titles:")
        for job in db.db.jobs.find({}, {"title": 1, "location": 1, "_id": 0}):
            print(f"- {job['title']} ({job['location']})")
            
    except FileNotFoundError:
        print("Error: jd.json file not found!")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in jd.json!")
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")

if __name__ == "__main__":
    init_jobs()  # Changed from init_db() to init_jobs()
