from . import common

class OF211File(common.FileCommon):
    foamVersion      = '2.1.1'
    foamFileVersion  = 2.0
    fileClass        = None
    fileLocation     = None
    fileObj          = None
    varList          = []

    def __init__(self,foamDirectory,**kwargs):
        [
            setattr(OF211File,item._name,common._varDescriptor(i) )
            for i,item in enumerate(self.varList)
        ]
        self.setAttribs(kwargs)
        super().__init__(
            foamDirectory,
            self.fileClass,
            self.fileLocation,
            self.fileObj
            )

    def make(self):
        self.initializeFile()
        self.appendToFile('\n')
        self.appendToFile('body')
        self.appendToFile('\n\n')
        self.appendToFile('closeString')
        return self

    def setAttribs(self,dictionary):
        for key in dictionary.keys():
            if hasattr(self,key):
                setattr(self,key,dictionary[key])

    @property
    def body(self):
        body   = [repr(item) for item in self.varList]
        return common.miscellaneous.smartSpaceListOfStrings(
            body,'='
        )

class _SystemDict(OF211File):
    fileClass        = 'dictionary'
    fileLocation     = 'system'

class _ConstantDict(OF211File):
    fileClass        = 'dictionary'
    fileLocation     = 'constant'

class _ZeroField(OF211File):
    fileLocation = 0


class ControlDict(_SystemDict):
    fileObj          = 'controlDict'

    varList          = [
        common.FileString_Var(application       = 'implicitFoam'),
        common.FileString_Var(startFrom         = 'latestTime'),
        common.FileString_Var(stopAt            = 'endTime'),
        common.FileString_Var(endTime           = 0.4),
        common.FileString_Var(deltaT            = 1e-03),
        common.FileString_Var(writeControl      =  'runTime'),
        common.FileString_Var(writeInterval     = 0.01),
        common.FileString_Var(purgeWrite        = 0),
        common.FileString_Var(writePrecision    = 6),
        common.FileString_Var(writeCompression  = 'off'),
        common.FileString_Var(timeFormat        = 'general'),
        common.FileString_Var(timePrecision     = '6'),
        common.FileString_Var(runTimeModifiable = 'true')
    ]

class DecomposeParDict(_SystemDict):
    varList            = [
        common.FileString_Var(numberOfSubdomains       = '32'),
        common.FileString_Var(method                   = 'scotch'),
        common.FileString_VarDict(
            'simplerCoeffs',
            n     = '( 2 1 1 )',
            delta = '0.001'
        ),
        common.FileString_VarDict(
            'hierarchicalCoeffs',
            n     = '( 2 1 1 )',
            delta = '0.001',
            order = 'xyz',
        ),
        common.FileString_Var(distributed = 'no'),
        common.FileString_Var(roots       = '()')
    ]
    fileObj          = 'decomposeParDict'



class FvSchemes(_SystemDict):
    varList = [
        common.FileString_VarDict(
            'ddtSchemes' ,
            default    = 'backward'
        ),
        common.FileString_VarDict(
            'gradSchemes',
            dict = {
                'default' : 'Gauss linear',
                'grad(p)' : 'Gauss linear'
                }
        ),
        common.FileString_VarDict(
            'divSchemes',
            dict = {
                'default'                      : 'none',
                'div(phi,U)'                   : 'Gauss linearUpwind grad(U)',
                'div(phi,nuTilda)'             : 'Gauss linearUpwind grad(nuTilda)',
                r'div((nuEff*dev(T(grad(U)))))' : 'Gauss linear'
            }
        ),
        common.FileString_VarDict(
            'laplacianSchemes',
            default                = 'none',
            dict = {
                'laplacian(nu,U)'                : 'Gauss linear corrected',
                'laplacian(nuEff,U)'             : 'Gauss linear corrected',
                'laplacian((1|A(U)),p)'          : 'Gauss linear corrected',
                'laplacian(DnuTildaEff,nuTilda)' : 'Gauss linear corrected',
                'laplacian(1,p)'                 : 'Gauss linear corrected'
            }
        ),
        common.FileString_VarDict(
            'interpolationSchemes',
            dict = {
                'default'                        : 'linear',
                'interpolate(HbyA)'              : 'linear'
            }
        ),
        common.FileString_VarDict(
            'snGradSchemes',
            default = 'corrected'
        ),
        common.FileString_VarDict(
            'snGradSchemes',
            default = 'no',
            p       = ''
        )
    ]
    fileObj          = 'fvSchemes'

class FvSolutions(_SystemDict):
    fileObj          = 'fvSolution'
    varList          = [
        common.FileString_VarDict(
            'solvers',
            p = common.FileString_VarDict(
                None,
                solver          = 'PCG',
                preconditioner  = 'DIC',
                tolerance       =  1e-06,
                relTol          =  1e-06,
                maxIter         = 3000
            ),
            U = common.FileString_VarDict(
                None,
                solver          = 'PBiCG',
                preconditioner  = 'DILU',
                tolerance       = 1e-06,
                relTol          = 1e-06
            )
        ),
        common.FileString_VarDict(
            'PISO',
            nCorrectors = 2,
            nNonOrthogonalCorrectors  = 1,
            pRefCell        = 0,
            pRefValue       = 0
        ),
        common.FileString_VarDict(
            'SIMPLE',
            nNonOrthogonalCorrectors  = 2,
            pRefCell          = 0,
            pRefValue         = 0,
            residualControl   = common.FileString_VarDict(
                    None,
                    p  = 1e-5,
                    U  = 1e-5,
                    nuTilda = 1e-5,
            )
        ),
        common.FileString_VarDict(
            'relaxationFactors',
            fields   = common.FileString_VarDict(
                None,
                p  = 0.5,
            ),
            equations   = common.FileString_VarDict(
                None,
                U       = 0.7,
                nuTilda = 0.7
            )
        )
    ]

class TransportProperties_NewtonianQuemadaSwitch(_ConstantDict):
    fileObj          = 'transportProperties'
    varList =[
        common.FileString_Var(transportModel = 'Newtonian'),
        common.FileString_Var(nu = 'nu [ 0 2 -1 0 0 0 0 ] 3.302E-06'),
        common.FileString_VarDict(
            'CrossPowerLawCoeffs',
            nu0   = 'nu0 [ 0 2 -1 0 0 0 0 ] 0.01',
            nuInf = 'nuInf [ 0 2 -1 0 0 0 0 ] 10',
            m     = 'm [ 0 0 1 0 0 0 0 ] 0.4',
            n     = 'n [ 0 0 0 0 0 0 0 ] 3',
        ),
        common.FileString_VarDict(
            'BirdCarreauCoeffs',
            nu0             ='nu0 [ 0 2 -1 0 0 0 0 ] 0.025',
            nuInf           ='nuInf [ 0 2 -1 0 0 0 0 ] 0.0025',
            k               ='k [ 0 0 1 0 0 0 0 ] 0.11',
            n               ='n [ 0 0 0 0 0 0 0 ] 0.395'
        ),
        common.FileString_VarDict(
            'CarreauYasudaCoeffs',
            nu0             ='nu0 [ 0 2 -1 0 0 0 0 ] 0.025',
            nuInf           ='nuInf [ 0 2 -1 0 0 0 0 ] 0.0025',
            k               ='k [ 0 0 1 0 0 0 0 ] 0.11',
            n               ='n [ 0 0 0 0 0 0 0 ] 0.395',
            alpha           ='alpha [ 0 0 0 0 0 0 0 ] 0.644'
        ),
        common.FileString_VarDict(
            'QuemadaCoeffs',
            tau0             ='tau0 [ 1 -1 -2 0 0 0 0 ] 7.160E-03',
            muInf            ='muInf [ 1 -1 -1 0 0 0 0 ] 4.204E-03',
            rho              ='rho [1 -3 0 0 0 0 0] 1060',
            dict = {
                'lambda':'lambda [ 0 0 -1 0 0 0 0 ] 4.367E-03',
            }
        )
    ]
    def make(self):
        self.initializeFile()
        self.appendToFile('\n')
        self.appendToFile('//transportModel  Quemada\n')
        self.appendToFile('body')
        self.appendToFile('\n\n')
        self.appendToFile('closeString')
        return self

class P_OCT(_ZeroField):
    fileObj          = 'p'
    fileClass        = 'volScalarField'
    varList =[
        common.FileString_Var(dimensions = '[0 2 -2 0 0 0 0]'),
        common.FileString_Var(internalField = 'uniform 0'),
        common.FileString_VarDict(
            'boundaryField',
            WALL   = common.FileString_VarDict(
                None,
                type       ='zeroGradient'
            ),
            INLET   = common.FileString_VarDict(
                None,
                type       = 'zeroGradient'
            ),
            OUTLET   = common.FileString_VarDict(
                None,
                type       = 'zeroGradient',
                value      = 'uniform 0'
            )
        )
    ]


class PipeNewtonianFixedNormal(_ZeroField):
    __postFix__      = ''
    fileObj          = 'U'
    fileClass        = 'volVectorField'
    varList =[
        common.FileString_Var(dimensions = '[0 1 -1 0 0 0 0]'),
        common.FileString_Var(internalField = 'uniform (0 0 0)'),
        common.FileString_VarDict(
            'boundaryField',
            WALL   = common.FileString_VarDict(
                None,
                type       ='noSlip',
            ),
            INLET   = common.FileString_VarDict(
                None,
                type       = "surfaceNormalFixedValue",
                refValue   = "0"
            ),
            OUTLET   = common.FileString_VarDict(
                None,
                type = 'zeroGradient'
            )
        )
    ]
    def __init__(self,
        foamDirectory,
        *,
        velocity,
        **kwargs):
        super().__init__(foamDirectory,**kwargs)
        self.boundaryField.INLET.refValue = self._generateVariablesString(velocity)

    def _generateVariablesString(self, velocity):
        return velocity

    def make(self):
        self.initializeFile()
        self.appendToFile('\n')
        self.appendToFile('body')
        self.appendToFile('\n\n')
        self.appendToFile('closeString')
        return self


class U_OCT_NEWTONIAN(_ZeroField):
    __postFix__      = '_NEWTONIAN'
    fileObj          = 'U'
    fileClass        = 'volVectorField'
    varList =[
        common.FileString_Var(dimensions = '[0 1 -1 0 0 0 0]'),
        common.FileString_Var(internalField = 'uniform (0 0 0)'),
        common.FileString_VarDict(
            'boundaryField',
            WALL   = common.FileString_VarDict(
                None,
                type       ='fixedValue',
                value      ='uniform (0 0 0)'
            ),
            INLET   = common.FileString_VarDict(
                None,
                type       = 'groovyBC',
                variables = \
                    '"Qm=82.0876;CC=1.0374;PI=3.14159;cubicMeterPerSecond2mlPerMin=6e+07;Area=9.01669e-06;centroid=sum(pos()*mag(Sf()))/sum(mag(Sf()));coordi=pos() - centroid;profile=-normal();"',
                valueExpression      = '"(Qm)/cubicMeterPerSecond2mlPerMin/Area*profile"',
                value                = 'uniform (0 0 0)'
            ),
            OUTLET   = common.FileString_VarDict(
                None,
                type = 'zeroGradient'
            )
        )
    ]
    def __init__(self,
        foamDirectory,
        *,
        Qm,CC,inletArea,
        **kwargs):
        super().__init__(foamDirectory,**kwargs)
        self.boundaryField.OUTLET.variables = self._generateVariablesString(Qm,CC,inletArea)

    def _generateVariablesString(self,Qm,CC,Area):
        variables = \
            f'"Qm={Qm};CC={CC};PI=3.14159;cubicMeterPerSecond2mlPerMin=6e+07;Area={Area};centroid=sum(pos()*mag(Sf()))/sum(mag(Sf()));coordi=pos() - centroid;profile=-normal();"'
        return variables

    @property
    def pulsatileValueExpressionCommented(self):
        return r'valueExpression "(Qm-2.83586*cos((1*2*PI/CC)*time())+1.13367*sin((1*2*PI/CC)*time())-1.09937*cos((2*2*PI/CC)*time())-0.85915*sin((2*2*PI/CC)*time())+0.70761*cos((3*2*PI/CC)*time())-1.04898*sin((3*2*PI/CC)*time())+0.48890*cos((4*2*PI/CC)*time())+0.71584*sin((4*2*PI/CC)*time())-0.29543*cos((5*2*PI/CC)*time())-0.06778*sin((5*2*PI/CC)*time())+0.11454*cos((6*2*PI/CC)*time())+0.22741*sin((6*2*PI/CC)*time())-0.37011*cos((7*2*PI/CC)*time())-0.13848*sin((7*2*PI/CC)*time())+0.23613*cos((8*2*PI/CC)*time())-0.15284*sin((8*2*PI/CC)*time())-0.04670*cos((9*2*PI/CC)*time())+0.08242*sin((9*2*PI/CC)*time())+0.08075*cos((10*2*PI/CC)*time())-0.07041*sin((10*2*PI/CC)*time())+0.00550*cos((11*2*PI/CC)*time())+0.12147*sin((11*2*PI/CC)*time())-0.07736*cos((12*2*PI/CC)*time())-0.03547*sin((12*2*PI/CC)*time())+0.04093*cos((13*2*PI/CC)*time())-0.01490*sin((13*2*PI/CC)*time())-0.03809*cos((14*2*PI/CC)*time())+0.01484*sin((14*2*PI/CC)*time())+0.03868*cos((15*2*PI/CC)*time())-0.05287*sin((15*2*PI/CC)*time()))/cubicMeterPerSecond2mlPerMin/Area*profile";'

    def make(self):
        self.initializeFile()
        self.appendToFile('\n')
        self.appendToFile('body')
        self.appendToFile('\n\n')
        self.appendToFile('closeString')
        return self


class U_OCT_QUEMADA(_ZeroField):
    __postFix__      = '_QUEMADA'
    fileObj          = 'U'
    fileClass        = 'volVectorField'
    varList =[
        common.FileString_Var(dimensions = '[0 1 -1 0 0 0 0]'),
        common.FileString_Var(internalField = 'uniform (0 0 0)'),
        common.FileString_VarDict(
            'boundaryField',
            WALL   = common.FileString_VarDict(
                None,
                type       ='fixedValue',
                value      ='uniform (0 0 0)'
            ),
            INLET   = common.FileString_VarDict(
                None,
                type       = 'groovyBC',
                variables  = \
                    '"Qm=82.0876;CC=1.0374;PI=3.14159;cubicMeterPerSecond2mlPerMin=6e+07;Area=9.01669e-06;centroid=sum(pos()*mag(Sf()))/sum(mag(Sf()));coordi=pos() - centroid;profile=-normal();"',
                valueExpression      = r'"(Qm-2.83586*cos((1*2*PI/CC)*time())+1.13367*sin((1*2*PI/CC)*time())-1.09937*cos((2*2*PI/CC)*time())-0.85915*sin((2*2*PI/CC)*time())+0.70761*cos((3*2*PI/CC)*time())-1.04898*sin((3*2*PI/CC)*time())+0.48890*cos((4*2*PI/CC)*time())+0.71584*sin((4*2*PI/CC)*time())-0.29543*cos((5*2*PI/CC)*time())-0.06778*sin((5*2*PI/CC)*time())+0.11454*cos((6*2*PI/CC)*time())+0.22741*sin((6*2*PI/CC)*time())-0.37011*cos((7*2*PI/CC)*time())-0.13848*sin((7*2*PI/CC)*time())+0.23613*cos((8*2*PI/CC)*time())-0.15284*sin((8*2*PI/CC)*time())-0.04670*cos((9*2*PI/CC)*time())+0.08242*sin((9*2*PI/CC)*time())+0.08075*cos((10*2*PI/CC)*time())-0.07041*sin((10*2*PI/CC)*time())+0.00550*cos((11*2*PI/CC)*time())+0.12147*sin((11*2*PI/CC)*time())-0.07736*cos((12*2*PI/CC)*time())-0.03547*sin((12*2*PI/CC)*time())+0.04093*cos((13*2*PI/CC)*time())-0.01490*sin((13*2*PI/CC)*time())-0.03809*cos((14*2*PI/CC)*time())+0.01484*sin((14*2*PI/CC)*time())+0.03868*cos((15*2*PI/CC)*time())-0.05287*sin((15*2*PI/CC)*time()))/cubicMeterPerSecond2mlPerMin/Area*profile"',
                value                = 'uniform (0 0 0)'
            ),
            OUTLET   = common.FileString_VarDict(
                None,
                type = 'zeroGradient'
            )
        )
    ]


if __name__ == '__main__':
    from pathlib import Path
    mainFolder = Path(r'F:\GitHub\foamTemplate\testConstructor')

    foamDirectory = common.FoamDirectory(mainFolder)
    foamDirectory.buildDirectory()
    controlDict   = ControlDict(foamDirectory).make()
    decomposeFile = DecomposeParDict(foamDirectory).make()
    fvSchemes     = FvSchemes(foamDirectory).make()
    fvSolutions   = FvSolutions(foamDirectory).make()
    tpProp        = TransportProperties_NewtonianQuemadaSwitch(foamDirectory).make()
    p             = P_OCT(foamDirectory).make()

    U_OCT(foamDirectory,1,1,1).make()

    print('done')




