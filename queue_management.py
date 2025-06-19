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

    def is_full(self) -> bool:
        return self.size == self.capacity

    def is_empty(self) -> bool:
        return self.size == 0

    def enqueue(self, user_id: str, priority: int) -> bool:
        if self.is_full():
            return False

        self.job_counter += 1
        new_job = PrintJob(user_id, self.job_counter, priority)
        self.rear = (self.rear + 1) % self.capacity
        self.queue[self.rear] = new_job
        self.size += 1
        return True

    def dequeue(self) -> PrintJob:
        if self.is_empty():
            return None

        job = self.queue[self.front]
        self.queue[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return job

    def update_waiting_times(self):
        for i in range(self.capacity):
            if self.queue[i] is not None:
                self.queue[i].waiting_time += 1

    def get_status(self) -> list:
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
        index = self.front
        for _ in range(self.size):
            if self.queue[index] is not None and self.queue[index].job_id == job_id:
                return self.queue[index]
            index = (index + 1) % self.capacity
        return None