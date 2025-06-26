import time
from datetime import datetime, timedelta

class JobManager:
    def __init__(self):
        self.jobs = []

    def add_job(self, job_id, expiry_minutes):
        job = {
            "job_id": job_id,
            "created_at": datetime.now(),
            "expiry_minutes": expiry_minutes
        }
        self.jobs.append(job)
        print(f"[INFO] Job {job_id} added. Expires in {expiry_minutes} minutes.")

    def cleanup_expired_jobs(self):
        current_time = datetime.now()
        active_jobs = []

        for job in self.jobs:
            expiry_time = job["created_at"] + timedelta(minutes=job["expiry_minutes"])
            if current_time >= expiry_time:
                print(f"[NOTIFY] Job {job['job_id']} has expired and will be removed.")
            else:
                active_jobs.append(job)

        self.jobs = active_jobs  # update job list

    def display_jobs(self):
        print(f"\n[STATE] Remaining Jobs: {[job['job_id'] for job in self.jobs]}")
if __name__ == "__main__":
    manager = JobManager()
    
    try:
        num_jobs = int(input("How many jobs do you want to add? "))
        
        for _ in range(num_jobs):
            job_id = input("Enter Job ID: ")
            try:
                expiry = float(input("Enter expiry time (in minutes): "))
                manager.add_job(job_id, expiry)
            except ValueError:
                print("[ERROR] Please enter a valid number for expiry time.")
        
        print("\n[WAIT] Waiting 10 seconds...\n")
        time.sleep(10)

        print("[CLEANUP] Checking for expired jobs...\n")
        manager.cleanup_expired_jobs()

        manager.display_jobs()

    except ValueError:
        print("[ERROR] Invalid input for number of jobs.")

