import threading
from scheduler.runner import JobRunner
from scheduler.job_store import load_jobs
from scheduler.utils import parse_time, now
from scheduler.recurrence import next_run_time

class SchedulerEngine:
    def __init__(self):
        self.jobs = load_jobs()
        # Keep next_run as ISO format strings in the jobs list

        self.runner = JobRunner(self.jobs)
        self.thread = None

    def add_job(self, name, command, rule):
        first_run = now() if rule["frequency"] == "interval" else parse_time(rule["time"])

        job = {
            "name": name,
            "command": command,
            "rule": rule,
            "next_run": first_run.isoformat()
        }
        self.jobs.append(job)

        from scheduler.job_store import save_jobs
        save_jobs(self.jobs)

    def start(self):
        self.thread = threading.Thread(target=self.runner.start)
        self.thread.start()

    def stop(self):
        self.runner.stop()
        if self.thread:
            self.thread.join()

    def list_jobs(self):
        return self.jobs