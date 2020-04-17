
from pathlib import Path
from .. import utils as miscellaneous
from abc import abstractmethod
import re

class _varDescriptor:
    def __init__(self,ID):
        self._id = ID
    def __get__(self,instance,owner):
        return instance.varList[self._id]
    def __set__(self,instance,value):
        if hasattr(instance.varList[self._id],'_val'):
            instance.varList[self._id]._val = value
        else:
            raise Exception(f'{instance.varList[self._id]} cannot be set')

class FileString_VarDict:
    def __init__(self,propertyName,dict = None,**kwargs):
        self._name = propertyName
        self.dict = dict
        for key,item in kwargs.items():
            setattr(self,key,item)
        self._keys = kwargs.keys()

    def __repr__(self):
        items = []; setter = items.append
        for key in self._keys:
            item = getattr(self,key)
            if not isinstance(item,FileString_VarDict):
                if 'comment' not in key:
                    item = miscellaneous.tablines(f'{key}={getattr(self,key)};')
                else:
                    item = miscellaneous.tablines(f'//={getattr(self,key)}')
            else:
                item = miscellaneous.tablines(f'{key}{getattr(self,key)}')
            setter(item)

        if self.dict is not None:
            for key,item in self.dict.items():
                if not isinstance(item,FileString_VarDict):
                    if 'comment' not in key:
                        item = miscellaneous.tablines(f'{key}={item};')
                    else:
                        item = miscellaneous.tablines(f'//={item}')
                else:
                    item = miscellaneous.tablines(f'{key}{item};')
                setter(item)

        items = miscellaneous.smartSpaceListOfStrings(items,'=',joiner = '\n')
        if not self._name == None: text = [f'{self._name}','{']
        else: text = ['\n{']

        text.extend([items])
        text.extend('}')
        main = '\n'.join(text)
        return main

class FileString_Var:
    def __init__(self,**kwargs):
        self._name,self._val = list(kwargs.items())[0]

    def __repr__(self):
        return f'{self._name}={self._val};'

class FoamDirectory:
    makeParents      = True
    allowedLocations = ['constant', 'system', 'polyMesh']
    def __init__(self,mainFolder):
        self.mainFolder     = Path(mainFolder)
        numberedFolders      = miscellaneous.getNunmberedFolders(self.mainFolder)
        if len(numberedFolders) == 0: numberedFolders      = [self.mainFolder.joinpath('0')]
        self.timeStepDict   = dict([
            (folder.name,folder) for folder in numberedFolders
        ])

        self.constantFolder = self.mainFolder.joinpath('constant')
        self.systemFolder   = self.mainFolder.joinpath('system')
        self.polyMeshFolder = self.constantFolder.joinpath('polyMesh')

    def buildDirectory(self):
        try:
            self.mainFolder.mkdir(parents = True)
            self.constantFolder.mkdir()
            self.systemFolder.mkdir()
            self.polyMeshFolder.mkdir()
            for key in self.timeStepDict.keys(): self.timeStepDict[key].mkdir()
        except:
            print(f'{self.mainFolder} already exists')

    def createTimestep(self,timeStep):
        timeStep = str(timeStep)
        if hasattr(self.timeStepDict,timeStep):
            print(f'timestep {timeStep} already exists at {self.timeStepDict[timeStep]}')
        else:
            self.timeStepDict[timeStep] = self.mainFolder.joinpath(timeStep)
            try:
                self.timeStepDict[timeStep].mkdir()
            except:
                print(f'{self.timeStepDict[timeStep]} already exists')

class FileCommon:
    foamVersion      = 'xxxxx'
    foamFileVersion  = 9.9
    fileFormat       = 'ascii'
    dividerStarFar   = '// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //'
    dividerStarClose = '// ************************************************************************* //'

    def __init__(self,
        directoryObj,
        fileClass,
        fileLocation,
        fileObj,
    ):
        assert isinstance(directoryObj,FoamDirectory), f'directoryObj must subclass from {FoamDirectory}'
        self.directory = directoryObj

        if miscellaneous.isNumber(fileLocation):
            fileLocation = str(fileLocation)
            if hasattr(self.directory.timeStepDict,fileLocation):
                self._fileFolder   = self.directory.timeStepDict[fileLocation]
                self._fileLocation = fileLocation
            else:
                self.directory.createTimestep(fileLocation)
                self._fileFolder = self.directory.timeStepDict[fileLocation]
                self._fileLocation = fileLocation
        else:
            assert fileLocation in self.directory.allowedLocations, \
                    f'fileLocation must either be timestep or {self.directory.allowedLocations}'
            self._fileFolder = getattr(self.directory,fileLocation+'Folder')
            self._fileLocation = fileLocation

        self._fileClass = fileClass
        self._fileObj   = fileObj

        if 'field'      in fileClass.lower(): self.foamfileString       = self.fieldFoamFileString
        if 'dictionary' in fileClass.lower(): self.foamfileString       = self.dictionaryFoamFileString

    @abstractmethod
    def make(self): NotImplemented

    def initializeFile(self):
        with open(self.filePath,'w',newline='\n') as f:f.write(self.heading)
        self.appendToFile('foamfileString')
        self.appendToFile('dividerStarFar')
        self.appendToFile('\n')

    def appendToFile(self,string):
        with open(self.filePath,'a+',newline='\n') as f:
            if hasattr(self,string):
                f.write(getattr(self,string))
            else:
                f.write(string)

    @property
    def closeString(self): return self.dividerStarClose
    @property
    def fileClass(self): return self._fileClass
    @property
    def fileLocation(self): return self._fileLocation
    @property
    def fileObject(self):
        return self._fileObj

    @property
    def fileFolder(self): return self._fileFolder
    @property
    def filePath(self):
        if hasattr(self,'__postFix__'):
            name = self.fileObject+self.__postFix__
        else:
            name = self.fileObject
        return self.fileFolder.joinpath(name)

    @property
    def heading(self):
        heading = \
r'''/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  %s                                 |
|   \\  /    A nd           | Web:      www.OpenFOAM.org                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
'''%self.foamVersion
        return heading

    @property
    def dictionaryFoamFileString(self):
        foamFile = \
'''FoamFile
{
    version     %0.1f;
    format      %s;
    class       dictionary;
    location    "%s";
    object      %s;
}
'''%(self.foamFileVersion,self.fileFormat,self.fileLocation,self.fileObject)
        return foamFile

    @property
    def fieldFoamFileString(self):
        foamFile = \
'''FoamFile
{
    version     %0.1f;
    format      %s;
    class       %s;
    object      %s;
}
'''%(self.foamFileVersion,self.fileFormat,self.fileClass,self.fileObject)
        return foamFile
