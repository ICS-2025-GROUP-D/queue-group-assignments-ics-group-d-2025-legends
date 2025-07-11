import time
import threading
from queue_management import CircularPrintQueue, PrintJob
from jobManager import JobManager
from concurrent_job_handler import ConcurrentJobHandler
from PrintQueManager import Job, JobExpiryManager
from show_status import show_status
from event_simulator import EventSimulator

class PrintSystem:
    def __init__(self, queue_capacity=10, expiry_time_seconds=60, max_threads=5):
        self.print_queue = CircularPrintQueue(queue_capacity)
        self.job_manager = JobManager()
        self.concurrent_handler = ConcurrentJobHandler(max_threads)
        self.job_expiry_manager = JobExpiryManager([], expiry_time_seconds)
        self.event_simulator = EventSimulator()
        self.job_counter = 0
        self.running = True
        self.lock = threading.Lock()

    def add_job(self, user_id: str, priority: int, expiry_minutes: float):
        with self.lock:
            self.job_counter += 1
            job_id = self.job_counter
            success = self.print_queue.enqueue(user_id, priority)
            if success:
                self.job_manager.add_job(job_id, expiry_minutes)
                # Add to PrintQueManager's queue for expiry tracking
                job = Job(job_id, user_id, priority, time.time())
                self.job_expiry_manager.queue.append(job)
                # Add to event simulator
                self.event_simulator.add_event(f"Job_{job_id}", expiry_time=int(expiry_minutes * 60), priority=priority)
                print(f"[INFO] Added job {job_id} for {user_id} with priority {priority}")
                return True
            else:
                print(f"[ERROR] Failed to add job for {user_id}: Queue is full")
                return False

    def add_simultaneous_jobs(self, job_data: str):
        try:
            jobs = self.concurrent_handler.parse_simultaneous_command(job_data)
            result = self.concurrent_handler.handle_simultaneous_submissions(self.print_queue, jobs)
            for job in jobs:
                user_id, priority = job
                self.job_manager.add_job(self.print_queue.job_counter, expiry_minutes=10)  # Default 10 min expiry
                job_obj = Job(self.print_queue.job_counter, user_id, priority, time.time())
                self.job_expiry_manager.queue.append(job_obj)
                self.event_simulator.add_event(f"Job_{self.print_queue.job_counter}", expiry_time=600, priority=priority)
            print(self.concurrent_handler.format_submission_results(result, len(jobs)))
        except ValueError as e:
            print(f"[ERROR] Invalid job data format: {str(e)}")

    def process_jobs(self):
        while self.running:
            if not self.print_queue.is_empty():
                job = self.print_queue.dequeue()
                if job:
                    print(f"[PROCESSING] Processing {job}")
            self.print_queue.update_waiting_times()
            self.event_simulator.tick()
            self.job_expiry_manager.cleanup_expired_jobs()
            time.sleep(1)

    def display_status(self):
        show_status(self.print_queue)
        self.job_manager.display_jobs()

    def start_expiry_monitor(self):
        def monitor():
            self.job_expiry_manager.monitor_and_cleanup_loop()
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()

    def run(self):
        self.start_expiry_monitor()
        processing_thread = threading.Thread(target=self.process_jobs, daemon=True)
        processing_thread.start()

        print("Print System Started. Commands: add, simultaneous, status, exit")
        while self.running:
            command = input("> ").strip().lower()
            if command == "exit":
                self.running = False
                print("[INFO] Shutting down print system...")
                break
            elif command == "add":
                try:
                    user_id = input("Enter User ID: ")
                    priority = int(input("Enter Priority: "))
                    expiry = float(input("Enter Expiry Time (minutes): "))
                    self.add_job(user_id, priority, expiry)
                except ValueError:
                    print("[ERROR] Invalid input. Priority must be an integer, expiry a number.")
            elif command == "simultaneous":
                job_data = input("Enter jobs (format: user1:priority1,user2:priority2,...): ")
                self.add_simultaneous_jobs(job_data)
            elif command == "status":
                self.display_status()
            else:
                print("[ERROR] Unknown command. Use: add, simultaneous, status, exit")

if __name__ == "__main__":
    system = PrintSystem(queue_capacity=10, expiry_time_seconds=60, max_threads=5)
    system.run()
