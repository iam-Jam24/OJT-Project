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
        if rule["frequency"] == "interval":
            first_run = now()
        else:
            # Handle HH:MM format by converting to today's date
            time_str = rule.get("time", "00:00")
            if "T" not in time_str:  # HH:MM format
                today = now().date()
                time_str = f"{today}T{time_str}:00"
            first_run = parse_time(time_str)

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