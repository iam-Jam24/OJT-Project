import threading
import time
from scheduler.recurrence import next_run_time
from scheduler.job_store import save_jobs
from scheduler.utils import now, parse_time
from scheduler.notifications import notify_job_execution, notify_job_completed

class JobRunner:
    def __init__(self, jobs):
        self.jobs = jobs
        self.running = True
        self.lock = threading.Lock()

    def run_job(self, job):
        print(f"\n▶ Running job: {job['name']}")
        
        # Trigger notification with sound and pop-up
        notify_job_execution(job['name'], with_sound=True, with_popup=True)

        # simulate job execution
        time.sleep(2)
        print(f"✔ Completed job: {job['name']}")

    def start(self):
        print("Scheduler started...")
        while self.running:
            with self.lock:
                for job in self.jobs:
                    t = now()
                    # Parse the next_run string to datetime for comparison
                    next_time = parse_time(job["next_run"])

                    if t >= next_time and not job.get("running", False):
                        job["running"] = True
                        thread = threading.Thread(target=self.execute_and_reschedule, args=(job,))
                        thread.start()
            time.sleep(1)

    def execute_and_reschedule(self, job):
        self.run_job(job)
        job["running"] = False

        # Parse the string to datetime for recurrence calculation
        last_run = parse_time(job["next_run"])
        job["next_run"] = next_run_time(job["rule"], last_run).isoformat()

        # Notify job completion with next run time
        notify_job_completed(job['name'], job["next_run"])

        save_jobs(self.jobs)

    def stop(self):
        print("Shutting down scheduler...")
        self.running = False