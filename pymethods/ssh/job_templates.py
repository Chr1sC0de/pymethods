spartanQuemada = [
    "#!/bin/sh\n",
    '#SBATCH --time=40:00:00\n',
    '#SBATCH -p snowy\n',
    '#SBATCH --nodes=1\n',
    '#SBATCH --ntasks-per-node=32\n',
    '#SBATCH --job-name=\"00004\"\n',
    '#SBATCH --output=\"QuemadaLog\"\n',
    '\n',
    'module load OpenFOAM/2.1.1-iompi-2016.u3\n',
    'source $FOAM_BASH\n',
    '\n',
    'srun decomposePar\n',
    'srun ericNonNewtonianImplicitFoam -parallel > quemada.Log\n',
    'srun reconstructPar\n',
    'srun ericWallTractionShearStress -latestTime\n',
    'srun foamToVTK -latestTime\n',
    'rm -rf processor*\n'
]