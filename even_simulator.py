import time

class Event:
    def __init__(self, name, expiry_time, priority=0):
        self.name = name
        self.waiting_time = 0
        self.expiry_time = expiry_time
        self.priority = priority

    def tick(self):
        self.waiting_time += 1

    def should_age(self):
        return self.waiting_time % 3 == 0  # Age every 3 ticks

    def apply_aging(self):
        self.priority += 1  # Increase priority as it waits

    def is_expired(self):
        return self.waiting_time >= self.expiry_time

    def display(self):
        print(f"{self.name} (Wait: {self.waiting_time}, Expire: {self.expiry_time}, Priority: {self.priority})")

class EventSimulator:
    def __init__(self):
        self.events = []
        self.tick_count = 0

    def add_event(self, name, expiry_time, priority=0):
        self.events.append(Event(name, expiry_time, priority))

    def tick(self):
        self.tick_count += 1
        print(f"\n--- Tick {self.tick_count} ---")

        for event in self.events[:]:
            event.tick()

            if event.is_expired():
                print(f" EXPIRED: {event.name}")
                self.events.remove(event)
            elif event.should_age():
                event.apply_aging()
                print(f" AGED: {event.name} (Priority: {event.priority})")

        for i in range(len(self.events)):
            for j in range(0, len(self.events) - i - 1):
                if self.events[j].priority < self.events[j + 1].priority:
                    self.events[j], self.events[j + 1] = self.events[j + 1], self.events[j]

        print(" Active Events:")
        for event in self.events:
            print(" - ", end="")
            event.display()


# ---------- Example Usage ----------

if __name__ == "__main__":
    sim = EventSimulator()
    sim.add_event("Apple", expiry_time=5, priority=1)
    sim.add_event("Bread", expiry_time=8, priority=2)
    sim.add_event("Milk", expiry_time=3, priority=0)

    for _ in range(10):
        sim.tick()
        time.sleep(1)  #1-second delay for realism
