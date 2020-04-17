def makeRaijinscriptA(
    filename,
    jobName  = '00000' ,
    ncpus    = '16',
    mem      = '10GB',
    jobfs    = '40GB',
    walltime = '20:00:00'
):
    script = [
        '#!/bin/bash\n',
        '\n',
        '### Job name (default is name of pbs script file)\n',
        f'#PBS -N {jobName}\n',
        '\n',
        '### Resource limits: amount of memory and CPU time ([[h:]m:]s).\n',
        f'#PBS -l ncpus={ncpus}\n',
        f'#PBS -l mem={mem}\n',
        f'#PBS -l jobfs={jobfs}\n',
        f'#PBS -l walltime={walltime}\n',
        '\n',
        "### This job's working directory\n",
        '#PBS -l wd\n',
        ' \n',
        '### Unload modules.\n',
        ' \n',
        '### Load modules.\n',
        'module unload openmpi\n',
        'module load openmpi/3.1.1\n',
        '\n',
        '### Run your executable\n',
        'source ~/OpenFOAM/OpenFOAM-2.1.1/etc/bashrc\n',
        f'mpirun -np {ncpus} ericNonNewtonianImplicitFoam -parallel   > $PBS_JOBID.out\n',
        'reconstructPar -latestTime > reconstruct.out\n',
        'ericWallTractionShearStress -latestTime > wallshearstress.out\n',
        'foamToVTK -latestTime > foamToVTKLog.out\n',
        'rm -rf processor*'
        ]

    with open(filename,'w',newline='\n') as f:
        f.writelines(script)

if __name__ == '__main__':
    import os
    from pathlib import Path
    from tqdm import tqdm
    mainFolder      = Path(r'F:\NON NEWT')
    foamFolders = [f for f in mainFolder.glob('*') if f.is_dir()]

    for folder in tqdm(foamFolders):
        name     = folder.name
        foamPath = folder.joinpath('run.sh')
        makeRaijinscriptA(
            foamPath,
            jobName  = name ,
            ncpus    = '16',
            mem      = '5GB',
            jobfs    = '25GB',
            walltime = '20:00:00'
        )
    print('done')


