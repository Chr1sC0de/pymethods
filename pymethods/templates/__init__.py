import re
from pathlib import Path
import shutil
from abc import abstractmethod
import numpy as np
from .function_glf_stl_to_foam import make_glf_stl_to_foam
from .raijinAngio import makeRaijinscriptA
import subprocess
from . import of211
from . import common

class FoamTemplateGenerator:

    def __init__(self,core):
        self.coreDirectory      = Path(__file__).parent.joinpath(core)
        self.templateGenerated  = False

    def makeTemplate(self,destinationFolder = '.',destinationName = 'template'):
        self.destinationName   = destinationName
        self.destinationFolder = Path(destinationFolder)
        if not self.destinationFolder.exists(): self.destinationFolder.mkdir()
        self.saveDestination   = self.destinationFolder.joinpath(self.destinationName)
        if not self.saveDestination.exists():
            shutil.copytree(self.coreDirectory,self.saveDestination)
        else:
            print(f'{self.saveDestination} already exists delete the existing folder to generate a new template')
        self.templateGenerated = True

    @abstractmethod
    def modify(self):
        assert self.templateGenerated
    @abstractmethod
    def makeGlypFromStl(self):pass

class LADAngioCNNSteadyTemplate(FoamTemplateGenerator):

    def __init__(self,surface):
        core = 'MainArterySteady'
        super().__init__(core)
        self.stlLocation   = surface.stlLocation
        self.inletArea     = surface.get_contours(0).area()
        #circular assumed diameter
        self.inletDiameter = np.sqrt(self.inletArea/np.pi)*2
        self.inletArea     = self.inletArea*10**(-6)

    def scalingLaw(self,d):
        q_in = 1.43*d**2.55
        return q_in

    def run(self):
        self.modify()
        self.makeGlypFromStl()
        self.runGlyph()

    def modify(self):
        super().modify()
        self.inletFlowrate = self.scalingLaw(self.inletDiameter)
        self.UFile         = self.saveDestination.joinpath('0').joinpath('U')
        with open(self.UFile ,'r') as f: fileOriginal  = f.read()
        fileNew = re.sub("Qm[=][0-9]*.[0-9]*", 'Qm=%0.5f'%self.inletFlowrate, fileOriginal)
        fileNew = re.sub("Area[=][0-9]*.[0-9]*e[+-][0-9]*", 'Area=%0.5e'%self.inletArea, fileNew)
        with open(self.UFile,'w') as f: f.write(fileNew)

    def makeGlypFromStl(self):

        make_glf_stl_to_foam(
            load_stl          = self.stlLocation,
            delta_s           = 0.1,
            TRexGrowthRate1   = 1.3,
            TRexGrowthRate    = 1.1,
            TRexMaximumLayers = 6,
            TRexSkewCriteriaMaximumAngle1 = 180,
            TRexSkewCriteriaMaximumAngle = 170,
            setSpacing        = 0.025,
            polymesh_folder   = self.saveDestination.joinpath('constant').joinpath('polyMesh'),
            pointwise_name    = self.destinationFolder.joinpath('foam_project.pw'),
            file_name         = self.destinationFolder.joinpath('stl_to_foam.glf')
        )

    def runGlyph(self):
        fileName = self.destinationFolder.joinpath('stl_to_foam.glf').as_posix()
        subprocess.run(fileName,shell=True, check=True)











