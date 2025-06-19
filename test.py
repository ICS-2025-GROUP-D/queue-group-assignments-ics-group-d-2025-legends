def show_status(queue):  # Replace 'self' with 'queue'
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Queue Status")
    table.add_column("User ID", style="cyan")
    table.add_column("Job ID", style="magenta")
    table.add_column("Priority", style="green")
    table.add_column("Wait Time", style="yellow")
    
    for job in queue:
        table.add_row(job.user_id, job.job_id, str(job.priority), str(job.wait_time))
    
    console.print(table)

# Test with dummy data
dummy_queue = [
    type("Job", (), {"user_id": "U1", "job_id": "J1", "priority": 3, "wait_time": 2}),
    type("Job", (), {"user_id": "U2", "job_id": "J2", "priority": 1, "wait_time": 5}),
]
show_status(dummy_queue)