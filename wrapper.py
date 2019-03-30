import os
import sys
from pathlib import Path

from vendor.terrasync import main

def runner():
    args = main.parseCommandLine()

    fp = Path(os.environ['TARGET_DIR'], ".full-sync-complete")
    args.quick = fp.exists()

    terraSync = main.TerraSync(args.mode, args.report, args.url, args.target,
                          args.quick, args.removeOrphan,
                          main.DownloadBoundaries(args.top, args.left, args.bottom,
                                             args.right))
    report = terraSync.start(args.virtualSubdir)

    if args.report:
        report.printReport()

    fp.touch()

if __name__ == '__main__':
    runner()
