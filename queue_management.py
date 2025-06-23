import threading
from concurrent_job_handler import ConcurrentJobHandler


class PrintJob:
    def __init__(self, user_id: str, job_id: int, priority: int):
        self.user_id = user_id
        self.job_id = job_id
        self.priority = priority
        self.waiting_time = 0

    def __str__(self):
        return f"Job(user={self.user_id}, id={self.job_id}, pri={self.priority}, wait={self.waiting_time})"


class CircularPrintQueue:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = [None] * capacity
        self.front = 0
        self.rear = -1
        self.size = 0
        self.job_counter = 0

        # Thread synchronization for module 4 compatibility
        self._lock = threading.RLock()

    def is_full(self) -> bool:
        with self._lock:
            return self.size == self.capacity

    def is_empty(self) -> bool:
        with self._lock:
            return self.size == 0

    def enqueue(self, user_id: str, priority: int) -> bool:
        with self._lock:
            if self.is_full():
                return False

            self.job_counter += 1
            new_job = PrintJob(user_id, self.job_counter, priority)
            self.rear = (self.rear + 1) % self.capacity
            self.queue[self.rear] = new_job
            self.size += 1
            return True

    def dequeue(self) -> PrintJob:
        with self._lock:
            if self.is_empty():
                return None

            job = self.queue[self.front]
            self.queue[self.front] = None
            self.front = (self.front + 1) % self.capacity
            self.size -= 1
            return job

    def update_waiting_times(self):
        with self._lock:
            for i in range(self.capacity):
                if self.queue[i] is not None:
                    self.queue[i].waiting_time += 1

    def get_status(self) -> list:
        with self._lock:
            status = []
            if self.is_empty():
                return status

            index = self.front
            for _ in range(self.size):
                if self.queue[index] is not None:
                    status.append(str(self.queue[index]))
                index = (index + 1) % self.capacity
            return status

    def get_job_by_id(self, job_id: int) -> PrintJob:
        with self._lock:
            index = self.front
            for _ in range(self.size):
                if self.queue[index] is not None and self.queue[index].job_id == job_id:
                    return self.queue[index]
                index = (index + 1) % self.capacity
            return None


class PrintQueueManager:
    """docstring for ClassName."""

    def __init__(self, capacity: int = 10):
        self.print_queue = CircularPrintQueue(capacity)

    """
        Initialize each module here for the task you have been doing from module
        1 to the last module 6 that way we have combined them to work together thus completed the 
        assignment
    """

    # Initializing Module 4 here: Concurrent Job Handler
    self.concurrent_handler = ConcurrentJobHandler(max_threads=5)


def send_simultaneous(self, job_data: str) -> str:
    """
        Handle simultaneous job submissions

        Args:
            job_data (str): Comma-separated string like "user1:priority1, user2:priority2"

        Returns:
            str: Formatted result string
    """
    try:
        # parsing the job data using module 4
        jobs = self.concurrent_handler.parse_simultaneous_command(job_data)

        if not jobs:
            return f"Error: No valid jobs found in simultaneous submission"

            # Execute simultaneous submissions using module 4
        result = self.concurrent_handler.handle_simultaneous_submissions(
            self.print_queue, jobs
        )

        # Format and return the results using module 4
        return self.concurrent_handler.format_submissions_results(
            result, len(jobs)
        )

    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error processing simultaneous submission: {str(e)}"