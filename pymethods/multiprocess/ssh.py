
from pymethods.ssh.client import SpartanFOAM as SpartanFOAMClient
import multiprocessing as mp


def remote_runner(local, remote, username, password):
    client = SpartanFOAMClient(
            local, remote,
            username=username, password=password
    )
    client.quick_run()
    return None

class SpartanFOAM:

    def __init__(self, foam_folders, *, username, password, max_jobs=10):
        self.max_jobs = max_jobs
        self.foam_folders = foam_folders
        self._username = username
        self._password = password

    def run(self, remote):
        processes = {}

        foam_folders = self.foam_folders.copy()

        n = 0
        if self.max_jobs > 1:
            while len(foam_folders) > 0:

                while len(processes) < self.max_jobs:

                    if not len(foam_folders) == 0:
                        p = mp.Process(
                            target=remote_runner,
                            args=(
                                foam_folders.pop(0),
                                remote, self._username, self._password
                            )
                        )
                        p.start()
                        processes[n] = p
                        n += 1
                    else:
                        break

                keys = list(processes.keys())

                for key in keys:
                    p = processes[key]
                    if not p.is_alive():
                        p.join()
                        del processes[key]
        else:
            remote_runner(
                foam_folders.pop(0),
                remote, self._username, self._password
            )