from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route("/queue_status")
def queue_status():
    
    jobs = [
        {"user_id": job.user_id, "job_id": job.job_id, "priority": job.priority, "wait_time": job.wait_time}
        for job in self.queue
    ]
    return jsonify(jobs)

@app.route("/")
def dashboard():
    return render_template("queue_dashboard.html")