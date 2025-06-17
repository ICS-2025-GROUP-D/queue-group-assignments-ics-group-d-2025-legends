import time
from datetime import datetime, timedelta

# Simulated job list
jobs = []

# Add a job
def add_job(job_id, expiry_minutes):
    job = {
        "job_id": job_id,
        "created_at": datetime.now(),
        "expiry_minutes": expiry_minutes
    }
    jobs.append(job)
    print(f"[INFO] Job {job_id} added. Expires in {expiry_minutes} minutes.")

# Check and remove expired jobs
def cleanup_expired_jobs():
    current_time = datetime.now()
    active_jobs = []
    
    for job in jobs:
        expiry_time = job["created_at"] + timedelta(minutes=job["expiry_minutes"])
        if current_time >= expiry_time:
            print(f"[NOTIFY] Job {job['job_id']} has expired and will be removed.")
        else:
            active_jobs.append(job)
    
    # Replace original job list with active jobs only
    return active_jobs

# Example run
if __name__ == "__main__":
    # Add some jobs
    add_job("JobA", 0.1)  # expires quickly for demo
    add_job("JobB", 1)    # expires in 1 minute

    print("\n[WAIT] Waiting 10 seconds...\n")
    time.sleep(10)  # simulate waiting

    print("[CLEANUP] Checking for expired jobs...\n")
    jobs = cleanup_expired_jobs()

    print(f"\n[STATE] Remaining Jobs: {[job['job_id'] for job in jobs]}")
