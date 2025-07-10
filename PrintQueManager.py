import time
from threading import Lock

class Job:
    def __init__(self, job_id, user_id, priority, timestamp):
        self.job_id = job_id          # Unique ID for the job
        self.user_id = user_id        # Who submitted the job
        self.priority = priority      # Job priority (higher = more urgent)
        self.timestamp = timestamp    # Time when job was added to the queue
        self.expired = False          # Whether this job is expired

    def __str__(self):
        # String format for printing the job (e.g., in logs)
        age = int(time.time() - self.timestamp)
        return f"Job[{self.job_id}] (User: {self.user_id}, Priority: {self.priority}, Age: {age}s)"


class JobExpiryManager:
    def __init__(self, queue, expiry_time_seconds):
        self.queue = queue                    # The shared job queue (e.g., list or custom queue object)
        self.expiry_time = expiry_time_seconds  # How long a job can wait before expiring (in seconds)
        self.lock = Lock()                    # Lock for thread-safe operations

    def cleanup_expired_jobs(self):
        current_time = time.time()
        expired_jobs = []

        with self.lock:  # Ensure thread-safe access to the shared queue
            i = 0
            while i < len(self.queue):
                job = self.queue[i]
                age = current_time - job.timestamp

                if age >= self.expiry_time:
                    # Job has expired → remove it from the queue
                    expired_job = self.queue.pop(i)
                    expired_job.expired = True
                    expired_jobs.append(expired_job)
                    print(f"[Expiry Notice] Removed expired job: {expired_job}")

                    # We do NOT increment 'i' because we removed an item, so the next job shifts to this index
                else:
                    i += 1  # Move to the next job

        return expired_jobs

    def monitor_and_cleanup_loop(self, interval=1):
       
        while True:
            time.sleep(interval)  # Wait for a bit before checking again
            self.cleanup_expired_jobs()  # Remove expired jobs
