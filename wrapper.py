#! /usr/bin/env python3
import os
from datetime import datetime
from pathlib import Path

from vendor.terrasync import main

def runner():
    args = main.parseCommandLine()

    fp = Path(os.environ['TARGET_DIR'], ".full-sync-complete")
    args.quick = fp.exists()

    if args.quick:
        print("A previously completed full sync exists, doing a quick sync", flush=True)

    dt_start = datetime.now()

    print(f"Starting run at {dt_start}", flush=True)

    terraSync = main.TerraSync(args.mode, args.report, args.url, args.target,
                          args.quick, args.removeOrphan,
                          main.DownloadBoundaries(args.top, args.left, args.bottom,
                                             args.right))
    report = terraSync.start(args.virtualSubdir)

    if args.report:
        report.printReport()
    from time import sleep; sleep(10)

    fp.touch()
    dt_end = datetime.now()
    elapsed = dt_end - dt_start
    print(f"Sync complete at {dt_end}, elapsed: {elapsed}")
    print(f"Sync took {elapsed.days} days, {elapsed.seconds // 3600} hours, {elapsed.seconds // 60} minutes and {elapsed.seconds} seconds")

if __name__ == '__main__':
    runner()
