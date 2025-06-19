def show_status(self):
    """Display the current queue state in a table format. 
    Assumes self.queue exists and is iterable."""
    if not hasattr(self, 'queue') or not self.queue:
        print("Queue is empty.")
        return

    print("\n=== Current Queue Status ===")
    print("-" * 50)
    print(f"| {'User ID':<8} | {'Job ID':<6} | {'Priority':<8} | {'Wait Time':<10} |")
    print("-" * 50)
    
    for job in self.queue:
        # Default attributes 
        user_id = getattr(job, 'user_id', 'N/A')
        job_id = getattr(job, 'job_id', 'N/A')
        priority = getattr(job, 'priority', 'N/A')
        wait_time = getattr(job, 'wait_time', 'N/A')
        print(f"| {user_id:<8} | {job_id:<6} | {priority:<8} | {wait_time:<10} |")
    
    print("-" * 50)