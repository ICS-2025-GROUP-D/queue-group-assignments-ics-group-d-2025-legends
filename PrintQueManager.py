import threading  # Allows multiple operations to run simultaneously (concurrency)
from collections import deque  # Double-ended queue - efficient for adding/removing from both ends

# Define a class to represent a single print job
class PrintJob:
    def __init__(self, user_id, job_id, priority, waiting_time=0):
        self.user_id = user_id #Who submitted this print job
        self.job_id = job_id #Unique identifier for this specific job
        self.priority = priority #How important this job is
        self.waiting_time = waiting_time #How long this job has been waiting

# Define the main class that manages the entire print queue
class PrintQueueManager:
    def __init__(self, capacity=10, expiry_time=60, aging_interval=10, aging_increment=1):
        """
        - capacity: Maximum number of jobs the queue can hold
        - expiry_time: Seconds after which a job gets removed automatically 
        - aging_interval: Seconds to wait before increasing a job's priority 
        - aging_increment: How much to increase priority during aging 
        """
        self.capacity = capacity
        self.expiry_time = expiry_time
        self.aging_interval = aging_interval
        self.aging_increment = aging_increment
        
        # Create the actual queue using deque (double-ended queue)
        # maxlen=capacity means it can't grow beyond this size
        self.queue = deque(maxlen=capacity)
        
        # Create a lock for thread safety - prevents multiple threads from modifying the queue at the same time
        self.lock = threading.Lock()
    
    def enqueue_job(self, user_id, job_id, priority):
        """
        Add a new job to the queue, maintaining priority order.
        Higher priority jobs go toward the front of the queue.
        
        Returns: True if job was added successfully, False if queue is full
        """
        # Use 'with' statement to automatically acquire and release the lock This ensures thread safety - only one thread can modify queue at a time
        
        with self.lock:
            # Check if queue is at maximum capacity
            if len(self.queue) >= self.capacity:
                print(f"Queue is full! Cannot add job {job_id} for user {user_id}.")
                return False  
            
            # Create a new PrintJob object
            job = PrintJob(user_id, job_id, priority)

            inserted = False  # Flag to track if we've inserted the job
            
            # Loop through existing jobs to find insertion point
            for i, existing_job in enumerate(self.queue):
                # enumerate() gives us both index (i) and the job object
                
                # Insert new job if it has higher priority OR
                # same priority but has waited less time (fairness)
                if existing_job.priority < job.priority or (
                    existing_job.priority == job.priority and existing_job.waiting_time > job.waiting_time
                ):
                    # deque.rotate() moves items - negative number moves left
                    self.queue.rotate(-i)  # Move items so position i is at the end
                    self.queue.append(job)  # Add our job at the end
                    self.queue.rotate(i)   # Move items back to original positions
                    inserted = True
                    break  # Exit the loop since we've inserted the job
            
            # If we didn't insert anywhere, add to the end (lowest priority)
            if not inserted:
                self.queue.append(job)
            
            print(f"Job {job_id} for user {user_id} added with priority {priority}.")
            return True  

    def dequeue_job(self):
        """
        Remove and return the highest-priority job from the queue.
        This is typically called when a printer is ready to print the next job.
        
        Returns: PrintJob object if available, None if queue is empty
        """
        with self.lock:  # Ensure thread safety
            # Check if queue is empty
            if not self.queue:  # Empty deque evaluates to False
                print("Queue is empty! No job to dequeue.")
                return None  
            
            # Remove and return the first job (highest priority due to our ordering)
            job = self.queue.popleft()  # popleft() removes from left end
            print(f"Job {job.job_id} for user {job.user_id} dequeued with priority {job.priority}.")
            return job

    def get_status(self):
        """
        Return a copy of the current queue state for internal use.
        
        Returns: list of PrintJob objects currently in queue
        """
        with self.lock:
            # Convert deque to list to create a snapshot
            # This prevents external code from accidentally modifying our queue
            return list(self.queue)

    
    def apply_priority_aging(self):
        """
        Increase priority of jobs that have waited longer than aging_interval.
        This prevents low-priority jobs from waiting forever (starvation prevention).
        """
        with self.lock:
            # Loop through all jobs in the queue
            for job in self.queue:
                # Check if job has waited long enough for a priority boost
                if job.waiting_time >= self.aging_interval:
                    # Increase the job's priority
                    job.priority += self.aging_increment
                    print(f"Job {job.job_id} priority increased to {job.priority} due to aging.")
            
            # Re-sort the entire queue to maintain priority order
            # sorted() creates a new sorted list from the queue
            # key= parameter tells sorted() how to compare items
            # lambda is an anonymous function that takes a job (x) and returns a tuple
            # We sort by (priority, -waiting_time) - higher priority first,
            # then by negative waiting time (so longer waits come first for same priority)
            # reverse=True means highest values first
            sorted_queue = sorted(self.queue, key=lambda x: (x.priority, -x.waiting_time), reverse=True)
            
            # Replace our queue with the newly sorted one
            self.queue = deque(sorted_queue, maxlen=self.capacity)

    # ==================== Module 3: Job Expiry & Cleanup ====================
    
    def remove_expired_jobs(self):
        """
        Remove jobs that have exceeded the expiry time and notify users.
        This prevents the queue from being clogged with very old jobs.
        
        Returns: list of expired jobs that were removed
        """
        with self.lock:
            expired_jobs = []  # List to store jobs that expired
            remaining_jobs = deque(maxlen=self.capacity)  # New queue for non-expired jobs
            
            # Go through each job and check if it's expired
            for job in self.queue:
                if job.waiting_time >= self.expiry_time:
                    # Job has expired - add to expired list and notify
                    expired_jobs.append(job)
                    print(f"Job {job.job_id} for user {job.user_id} expired (waited {job.waiting_time}s).")
                else:
                    # Job is still valid - keep it in the queue
                    remaining_jobs.append(job)
            
            # Replace old queue with only the remaining (non-expired) jobs
            self.queue = remaining_jobs
            return expired_jobs  # Return expired jobs so calling code can handle notifications

    # ==================== Module 4: Concurrent Job Submission Handling ====================
    
    def handle_simultaneous_submissions(self, jobs):
        """
        Handle multiple job submissions concurrently using threading.
        This allows multiple users to submit jobs at the same time without blocking.
        
        Parameters:
        - jobs: list of tuples, each containing (user_id, job_id, priority)
        """
        threads = []  # List to keep track of all threads we create
        
        # Create a separate thread for each job submission
        for user_id, job_id, priority in jobs:
            # threading.Thread creates a new thread that will run the specified function
            # target= specifies which function to run
            # args= specifies what arguments to pass to that function
            thread = threading.Thread(target=self.enqueue_job, args=(user_id, job_id, priority))
            threads.append(thread)  # Add to our list
            thread.start()  # Start the thread running
        
        # Wait for all threads to complete before continuing
        for thread in threads:
            thread.join()  # join() blocks until this thread finishes
    
    def tick(self):
        """
        Simulate one second passing in the system.
        This would typically be called every second by a timer or scheduler.
        
        Updates waiting times, applies aging, removes expired jobs, and shows status.
        """
        with self.lock:
            # Increment waiting time for all jobs by 1 second
            for job in self.queue:
                job.waiting_time += 1
            
            # Apply the aging system (increase priority for jobs that have waited long enough)
            self.apply_priority_aging()  # Call Member 2's module
            
            # Remove any jobs that have expired
            expired_jobs = self.remove_expired_jobs()  # Call Member 3's module
            
            # Display current status after all updates
            self.show_status()  # Call Member 6's module for snapshot

    # ==================== Module 6: Visualization & Reporting ====================
    
    def show_status(self):
        """
        Display the current queue state in a formatted table.
        This helps users and administrators see what's in the queue.
        """
        with self.lock:
            # Check if queue is empty
            if not self.queue:
                print("Queue is empty.")
                return  # Exit early if nothing to display
            
            # Print a formatted header
            print("\nCurrent Queue State:")
            # Use string formatting to create aligned columns
            # :<10 means left-align in a field of width 10 characters
            print(f"{'Job ID':<10} {'User ID':<10} {'Priority':<10} {'Waiting Time (s)':<15}")
            print("-" * 45)  # Print a line of dashes for separation
            
            # Print each job's information in the same format
            for job in self.queue:
                print(f"{job.job_id:<10} {job.user_id:<10} {job.priority:<10} {job.waiting_time:<15}")
    
    def print_job(self):
        """
        Simulate actually printing a job by dequeuing the highest-priority job.
        In a real system, this would send the job to a physical printer.
        """
        # Get the next job to print
        job = self.dequeue_job()
        
        # If we got a job (queue wasn't empty), simulate printing it
        if job:
            print(f"Printing job {job.job_id} for user {job.user_id} with priority {job.priority}.")

# Example usage (this code would run if you execute this file directly):
if __name__ == "__main__":
    # Create a new print queue manager
    pqm = PrintQueueManager()
    
    # Add some jobs
    pqm.enqueue_job("user1", "job1", 5)
    pqm.enqueue_job("user2", "job2", 3)
    pqm.enqueue_job("user3", "job3", 7)
    
    # Show current status
    pqm.show_status()
    
    # Print the highest priority job
    pqm.print_job()