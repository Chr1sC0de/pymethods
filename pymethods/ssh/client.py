import paramiko as _po
import scp as _scp
import logging as logging
import multiprocessing as mp
import pathlib as _pt
from pymethods.ssh import job_templates
import logging
import time
level = logging.INFO
logging.basicConfig(level=level)
import shutil

class Client:

    def __init__(self, host, username=None, password=None, port=22, retryLimit=10):
        self.ssh = _po.SSHClient()
        self.ssh.load_system_host_keys()
        self.port = port
        self.ssh.connect(host, username=username, password=password)
        self.transport = self.ssh.get_transport()
        self._scp =  _scp.SCPClient(self.transport)
        self._host = host
        self._username = username
        self._password = password
        self.retryLimit = retryLimit

    def connect(self, *args, remoteTries=0, **kwargs):
        remoteTries += 1
        try:
            self.ssh.connect(
                self._host, username=self._username, password=self._password
            )
            self.transport = self.ssh.get_transport()
            self._scp = _scp.SCPClient(self.transport)
        except ConnectionResetError:
            if remoteTries > self.retryLimit:
                raise ConnectionError(
                    "Number of retries, %d, greater than retry limit %d, \
                        cannot connect"%(remoteTries, retryLimit))
            logging.info('Retrying Connect')
            self.connect(remoteTries=remoteTries)

    def disconnect(self):
        self.ssh.close()
        self._scp.close()
        self.transport.close()

    def copyLocalToRemote_Directory(
            self, localFolder, remoteFolder, remoteTries=0):
        localFolder = _pt.Path(localFolder)
        remoteFolder = _pt.Path(remoteFolder)
        remoteTries += 1
        if remoteTries == 1:
            logging.info(
                'Copying Local %s To Remote %s'%(localFolder, remoteFolder))
        try:
            self._scp.put(
                localFolder.as_posix(), remote_path=remoteFolder.as_posix(),
                recursive=True
            )
            logging.info(
                'Completed Copy Local %s To Remote %s' % (localFolder, remoteFolder))
            return True
        except ConnectionAbortedError:
            if not self.ssh.get_transport().is_active():
                self.connect()
            logging.info('Retrying Copy Local %s To Remote %s'%(localFolder, remoteFolder))
            if remoteTries > self.retryLimit:
                raise ConnectionError("Number of retries, %d, greater than retry limit %d"% (remoteTries, retryLimit) )
            self.copyLocalToRemote_Directory(localFolder, remoteFolder, remoteTries=remoteTries)

    def copyRemoteToLocal_Directory(self, remoteFolder, localFolder, remoteTries=0):
        localFolder = _pt.Path(localFolder)
        remoteFolder = _pt.Path(remoteFolder)
        remoteTries += 1
        if remoteTries == 1:
            logging.info('Copying Remote %s To Local %s'%(remoteFolder, localFolder))
        try:
            self._scp.get(
                    remoteFolder.as_posix(),
                    local_path=localFolder.as_posix(), recursive=True
                )
            logging.info('Completed Copying Remote %s To Local %s'%(remoteFolder, localFolder))
        except:
            if not self.ssh.get_transport().is_active():
                self.connect()
            logging.info('Retrying Copy Remote %s To Local %s'%(remoteFolder, localFolder))
            if remoteTries > self.retryLimit:
                raise ConnectionError("Number of retries, %d, greater than retry limit %d"% (remoteTries, retryLimit) )
            self.copyRemoteToLocal_Directory(localFolder, remoteFolder, remoteTries=remoteTries)

    def deleteRemote_Directory(self, remoteDirectory):
        logging.info('Removing %s from %s'%(remoteDirectory,self._host))
        self.ssh.exec_command(
            "rm -rf %s"%(remoteDirectory.as_posix())
        )
        logging.info('Completed Removing %s from %s'%(remoteDirectory,self._host))

class FOAM(Client):
    def __init__(self, host, localFoam, remoteMain, **kwargs):
        self.localFoam = _pt.Path(localFoam)
        self.remoteMain = _pt.Path(remoteMain)
        self.remoteFoam = self.remoteMain/self.localFoam.name
        self.job_template = kwargs.get(
            'job_template', job_templates.spartanQuemada
        )
        super().__init__(host, **kwargs)

    def copyLocalToRemote_Directory(self, remoteTries=0):
        super().copyLocalToRemote_Directory(
            self.localFoam, self.remoteMain, remoteTries=remoteTries)

    def copyRemoteToLocal_Directory(self, remoteTries=0):
        super().copyRemoteToLocal_Directory(
            self.remoteFoam, self.localFoam.parent, remoteTries=remoteTries)

    def make_job_script(self):
        assert hasattr(self, 'localFoam')
        logging.info("Creating Job Slurm")
        with open(self.localFoam/"foam/submit.slurm", 'w', newline='\n') as f:
            lines = self.modify_lines()
            f.writelines(lines)
        logging.info("Created Job Slurm")

    def modify_lines(self):
        self.job_template[5] = '#SBATCH --job-name=\"%s\"\n'%self.localFoam.name
        return self.job_template

    def run_foam(self, sleep_time=100):
        _, stdout, stderr = self.ssh.exec_command(
            "cd %s; sbatch submit.slurm"%((self.remoteFoam/'foam').as_posix())
        )

        stderr = stderr.read()
        if not len(stderr) == 0:
            raise Exception(stderr)

        stdout = str(stdout.read())
        self.job_id = int(stdout.split(' ')[-1][0:-3])

        logging.info('Running %s On %s'%(self.remoteFoam.name ,self._host))
        # check that the job has run properly
        while True:
            try:
                _, stdout, _ = self.ssh.exec_command(
                    "squeue -u %s"%self._username
                )

                lines = stdout.read()

                if not str(self.job_id) in str(lines):
                    break
                time.sleep(sleep_time)
            except:
                logging.info('disconnected, attempting to reconnect')
                self.connect()

        logging.info('Completed Running %s On %s'%(self.remoteFoam.name ,self._host))

    def clean_remote(self):
        logging.info('Removing %s from %s'%(self.remoteFoam.name ,self._host))
        self.ssh.exec_command(
            "rm -rf %s"%(self.remoteFoam.as_posix())
        )
        logging.info('Completed Removing %s from %s'%(self.remoteFoam.name ,self._host))

    def clean_local(self):
        foam_folder = self.localFoam/'foam'
        if "0.8" in [folder.name for folder in foam_folder.glob("*")]:
            for folder in foam_folder.glob('*'):
                if all(
                    [folder.is_dir(), (folder/"U").exists(),
                     not '0.4' in folder.name, not '0.8' in folder.name,
                     not '0' == folder.name]
                ):
                    shutil.rmtree(folder)
        else:
            logging.info(
                "foam case %s is incomplete" % self.localFoam.name
            )

    def quick_run(self):
        self.make_job_script()
        self.copyLocalToRemote_Directory()
        self.run_foam()
        self.copyRemoteToLocal_Directory()
        self.clean_remote()
        self.disconnect()
        self.clean_local()
        logging.info("finished process %s"%self.localFoam.name)

class MetaClient(type):

    def __new__(cls, classname, host, superClient):
        newclass = super().__new__(cls, classname, (superClient,), {})

        def __init__(self, *args, **kwargs):
            super(newclass, self).__init__(host, *args, **kwargs)

        setattr(newclass, "__init__", __init__)

        return newclass

SpartanFOAM = MetaClient("SpartanFOAM", "spartan.hpc.unimelb.edu.au", FOAM)




