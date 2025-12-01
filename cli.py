import argparse
from scheduler.engine import SchedulerEngine

engine = SchedulerEngine()

parser = argparse.ArgumentParser(description="Scheduler & Alarms CLI")
sub = parser.add_subparsers(dest="command")

# add job
add = sub.add_parser("add")
add.add_argument("--name", required=True)
add.add_argument("--time")
add.add_argument("--freq", choices=["once", "daily", "weekly", "hourly", "interval"], default="once")
add.add_argument("--seconds", type=int)

# start
sub.add_parser("start")

# list jobs
sub.add_parser("list")

args = parser.parse_args()

if args.command == "add":
    rule = {"frequency": args.freq}

    if args.freq == "interval":
        rule["seconds"] = args.seconds
    else:
        rule["time"] = args.time

    engine.add_job(args.name, "echo task", rule)
    print("Job added successfully.")

elif args.command == "list":
    for job in engine.list_jobs():
        print(f"- {job['name']} | next run: {job['next_run']}")

elif args.command == "start":
    try:
        engine.start()
    except KeyboardInterrupt:
        engine.stop()