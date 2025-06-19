import tkinter as tk
from tkinter import ttk

def show_status(self):
    root = tk.Tk()
    root.title("Queue Status")
    
    tree = ttk.Treeview(root, columns=("User ID", "Job ID", "Priority", "Wait Time"), show="headings")
    tree.heading("User ID", text="User ID")
    tree.heading("Job ID", text="Job ID")
    tree.heading("Priority", text="Priority")
    tree.heading("Wait Time", text="Wait Time")
    
    for job in self.queue:
        tree.insert("", "end", values=(job.user_id, job.job_id, job.priority, job.wait_time))
    
    tree.pack()
    root.mainloop()