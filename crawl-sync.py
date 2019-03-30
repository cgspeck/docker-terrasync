from pathlib import Path

import os
import subprocess


def runner():
    print('Running HTTrack')
    connections = os.environ.get('CONNECTION_COUNT', 8)
    url = os.environ['URL']
    filter_path = f'+{url.split("//")[1]}'

    if not filter_path.endswith('/'):
        filter_path += '/'
    filter_path += '*'

    target = os.environ['TARGET_DIR']
    print(f'Syncing {url} to {target} with filter path {filter_path} with {connections} connections')
    subprocess.run([
            '/usr/bin/httrack',
            f'"{url}"',
            '-O',
            f'"{target}"',
            f'"{filter_path}"',
            f'-c{connections}',
            '--disable-security-limits',
            '-s0',
            '-v'
        ],
        check=True
    )
    print("Downloading .dirindex files")
    raise NotImplementedError
    Path(os.environ['TARGET_DIR'], ".full-sync-complete").touch()


if __name__ == '__main__':
    runner()
