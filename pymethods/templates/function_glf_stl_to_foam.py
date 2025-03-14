# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 00:34:27 2019

@author: chris
"""
import os
from pathlib import Path

def make_glf_stl_to_foam(
    load_stl                      = 'OCTPostProcessed.stl',
    delta_s                       = 0.1,
    TRexGrowthRate1               = 1.3,
    TRexGrowthRate                = 1.1,
    TRexMaximumLayers             = 6,
    TRexSkewCriteriaMaximumAngle1 = 180,
    TRexSkewCriteriaMaximumAngle  = 170,
    setSpacing                    = 0.025,
    polymesh_folder               = 'constant/polyMesh',
    pointwise_name                = 'foam_project.pw',
    file_name                     = 'stl_to_foam.glf'
    ):
    """make_glf_stl_to_foam
    Creates a glyph to convert the stl to a foam file
    Args:
        load_stl (str, optional): stl file to be converted. Defaults to 'OCTPostProcessed.stl'.
        delta_s (float, optional): . Defaults to 0.1.
        TRexGrowthRate1 (float, optional): . Defaults to 1.3.
        TRexGrowthRate (float, optional): . Defaults to 1.1.
        TRexMaximumLayers (int, optional): . Defaults to 6.
        TRexSkewCriteriaMaximumAngle1 (int, optional): . Defaults to 180.
        TRexSkewCriteriaMaximumAngle (int, optional): . Defaults to 170.
        setSpacing (float, optional): . Defaults to 0.025.
        polymesh_folder (str, optional): where to save converted stl. Defaults to 'constant/polyMesh'.
        pointwise_name (str, optional): name of pointwise file to save. Defaults to 'foam_project.pw'.
        file_name (str, optional): name of output file. Defaults to 'stl_to_foam.glf'.
    """
    #%%
    load_stl          = Path(load_stl).absolute()
    save_mesh_folder  = Path(polymesh_folder)
    pointwise_folder  = Path(pointwise_name)

    if not pointwise_folder.parent.exists(): pointwise_folder.parent.mkdir()
    if not save_mesh_folder.exists(): save_mesh_folder.mkdir()
    load_stl          = load_stl.as_posix()
    save_mesh_folder  = save_mesh_folder.as_posix()
    pointwise_folder  = pointwise_folder.as_posix()

    array  =[
'# Pointwise V18.2R2 Journal file - Fri Apr  5 15:31:18 2019\n',
'\n',
'package require PWI_Glyph 2.18.2\n',
'pw::Application setUndoMaximumLevels 5\n',
'pw::Application reset\n',
'pw::Application markUndoLevel {Journal Reset}\n',
'\n',
'pw::Application clearModified\n',
'\n',
'set _TMP(mode_1) [pw::Application begin DatabaseImport]\n',
'  $_TMP(mode_1) initialize -strict -type Automatic {'+load_stl+'}\n',
'  $_TMP(mode_1) setAttribute ShellCellMode MergeCoplanar\n',
'  $_TMP(mode_1) read\n',
'  $_TMP(mode_1) convert\n',
'$_TMP(mode_1) end\n'
'unset _TMP(mode_1)\n'
'pw::Application markUndoLevel {Import Database}\n',
'\n',
'pw::Connector setCalculateDimensionMethod Spacing\n',
'pw::Connector setCalculateDimensionSpacing {}\n'.format(delta_s),
'pw::Application setGridPreference Unstructured\n',
'set _DB(1)  [pw::DatabaseEntity getBySequence 1]\n',
'set _TMP(PW_33) [pw::DomainUnstructured createOnDatabase -parametricConnectors Aligned -merge 0 -reject _TMP(unused) [list $_DB(1)]]\n',
'unset _TMP(unused)\n',
'unset _TMP(PW_33)\n',
'pw::Application markUndoLevel {Domains On DB Entities}\n',
'\n',
'set _CN(1) [pw::GridEntity getByName "con-1"]\n',
'set _CN(2) [pw::GridEntity getByName "con-2"]\n',
'set _TMP(PW_34) [pw::DomainUnstructured createFromConnectors -reject _TMP(unusedCons)  [list $_CN(1) $_CN(2)]]\n',
'unset _TMP(unusedCons)\n',
'unset _TMP(PW_34)\n',
'pw::Application markUndoLevel {Assemble Domains}\n',
'\n',
'set _CN(3) [pw::GridEntity getByName "con-3"]\n',
'set _CN(4) [pw::GridEntity getByName "con-4"]\n',
'set _TMP(PW_35) [pw::DomainUnstructured createFromConnectors -reject _TMP(unusedCons)  [list $_CN(3) $_CN(4)]]\n',
'unset _TMP(unusedCons)\n',
'unset _TMP(PW_35)\n',
'pw::Application markUndoLevel {Assemble Domains}\n',
'\n',
'set _DM(1) [pw::GridEntity getByName "dom-3"]\n',
'set _DM(2) [pw::GridEntity getByName "dom-2"]\n',
'set _TMP(mode_10) [pw::Application begin UnstructuredSolver [list $_DM(1) $_DM(2)]]\n',
'  set _TMP(ENTS) [pw::Collection create]\n',
'$_TMP(ENTS) set [list $_DM(1) $_DM(2)]\n',
'  $_TMP(ENTS) do setUnstructuredSolverAttribute ShapeConstraint Free\n',
'  $_TMP(ENTS) delete\n',
'  unset _TMP(ENTS)\n',
'  $_TMP(mode_10) run Initialize\n',
'$_TMP(mode_10) end\n',
'unset _TMP(mode_10)\n',
'pw::Application markUndoLevel {Solve}\n',
'\n',
'set _DM(3) [pw::GridEntity getByName "dom-1"]\n',
'set _TMP(PW_36) [pw::BlockUnstructured createFromDomains -reject _TMP(unusedDoms) -voids _TMP(voidBlocks) -baffles _TMP(baffleFaces) [concat [list] [list $_DM(1) $_DM(3) $_DM(2)]]]\n',
'unset _TMP(unusedDoms)\n',
'unset _TMP(PW_36)\n',
'pw::Application markUndoLevel {Assemble Blocks}\n',
'\n',
'set _BL(1) [pw::GridEntity getByName "blk-1"]\n',
'set _TMP(mode_10) [pw::Application begin UnstructuredSolver [list $_BL(1)]]\n',
'  set _TMP(ENTS) [pw::Collection create]\n',
'$_TMP(ENTS) set [list $_BL(1)]\n',
'  $_BL(1) setUnstructuredSolverAttribute TRexMaximumLayers 6\n',
'  $_BL(1) setUnstructuredSolverAttribute TRexGrowthRate %f\n'%TRexGrowthRate1,
'  $_BL(1) setUnstructuredSolverAttribute TRexGrowthRate %f\n'%TRexGrowthRate,
'  $_BL(1) setUnstructuredSolverAttribute TRexPushAttributes True\n',
'  $_BL(1) setUnstructuredSolverAttribute TRexSkewCriteriaMaximumAngle %d\n'%TRexSkewCriteriaMaximumAngle1,
'  $_BL(1) setUnstructuredSolverAttribute TRexSkewCriteriaMaximumAngle %d\n'%TRexSkewCriteriaMaximumAngle,
'  $_TMP(ENTS) delete\n',
'  unset _TMP(ENTS)\n',
'  set _TMP(PW_37) [pw::TRexCondition getByName {Unspecified}]\n',
'  set _TMP(PW_38) [pw::TRexCondition create]\n',
'  set _TMP(PW_39) [pw::TRexCondition getByName {bc-2}]\n',
'  unset _TMP(PW_38)\n',
'  set _TMP(PW_40) [pw::TRexCondition create]\n',
'  set _TMP(PW_41) [pw::TRexCondition getByName {bc-3}]\n',
'  unset _TMP(PW_40)\n',
'  $_TMP(PW_39) setConditionType {Wall}\n',
'  $_TMP(PW_41) setConditionType {Match}\n',
'  $_TMP(PW_39) apply [list [list $_BL(1) $_DM(3) Same]]\n',
'  $_TMP(PW_41) apply [list [list $_BL(1) $_DM(2) Opposite] [list $_BL(1) $_DM(1) Opposite]]\n',
'  $_TMP(PW_39) setSpacing %f\n'%setSpacing,
'  $_TMP(mode_10) run Initialize\n',
'$_TMP(mode_10) end\n',
'unset _TMP(mode_10)\n',
'pw::Application markUndoLevel {Solve}\n',
'\n',
'unset _TMP(PW_37)\n',
'unset _TMP(PW_39)\n',
'unset _TMP(PW_41)\n',
'pw::Application setCAESolver {OpenFOAM} 3\n',
'pw::Application markUndoLevel {Select Solver}\n',
'\n',
'set _TMP(PW_42) [pw::BoundaryCondition getByName {Unspecified}]\n',
'set _TMP(PW_43) [pw::BoundaryCondition create]\n',
'pw::Application markUndoLevel {Create BC}\n',
'\n',
'set _TMP(PW_44) [pw::BoundaryCondition getByName {bc-2}]\n',
'unset _TMP(PW_43)\n',
'set _TMP(PW_45) [pw::BoundaryCondition create]\n',
'pw::Application markUndoLevel {Create BC}\n',
'\n',
'set _TMP(PW_46) [pw::BoundaryCondition getByName {bc-3}]\n',
'unset _TMP(PW_45)\n',
'set _TMP(PW_47) [pw::BoundaryCondition create]\n',
'pw::Application markUndoLevel {Create BC}\n',
'\n',
'set _TMP(PW_48) [pw::BoundaryCondition getByName {bc-4}]\n',
'unset _TMP(PW_47)\n',
'$_TMP(PW_44) setName "WALL"\n',
'pw::Application markUndoLevel {Name BC}\n',
'\n',
'$_TMP(PW_46) setName "INLET"\n',
'pw::Application markUndoLevel {Name BC}\n',
'\n',
'$_TMP(PW_48) setName "OUTLET"\n',
'pw::Application markUndoLevel {Name BC}\n',
'\n',
'$_TMP(PW_44) setPhysicalType -usage CAE {wall}\n',
'pw::Application markUndoLevel {Change BC Type}\n',
'\n',
'$_TMP(PW_46) setPhysicalType -usage CAE {patch}\n',
'pw::Application markUndoLevel {Change BC Type}\n',
'\n',
'$_TMP(PW_48) setPhysicalType -usage CAE {patch}\n',
'pw::Application markUndoLevel {Change BC Type}\n',
'\n',
'pw::Display setShowDatabase 0\n',
'$_TMP(PW_44) apply [list [list $_BL(1) $_DM(3)]]\n',
'pw::Application markUndoLevel {Set BC}\n',
'\n',
'$_TMP(PW_46) apply [list [list $_BL(1) $_DM(2)]]\n',
'pw::Application markUndoLevel {Set BC}\n',
'\n',
'$_TMP(PW_48) apply [list [list $_BL(1) $_DM(1)]]\n',
'pw::Application markUndoLevel {Set BC}\n',
'\n',
'unset _TMP(PW_42)\n',
'unset _TMP(PW_44)\n',
'unset _TMP(PW_46)\n',
'unset _TMP(PW_48)\n',
'set _BL(1) [pw::GridEntity getByName blk-1]\n',
'set _TMP(mode_1) [pw::Application begin Modify [list $_BL(1)]]\n',
'pw::Entity transform [pwu::Transform scaling -anchor {0 0 0} {0.001 0.001 0.001}] [$_TMP(mode_1) getEntities]\n',
'	$_TMP(mode_1) end\n',
'unset _TMP(mode_1)\n',
'pw::Application markUndoLevel {Scale}\n',
'\n',
'set _TMP(mode_1) [pw::Application begin CaeExport]\n',
'  $_TMP(mode_1) addAllEntities\n',
'  $_TMP(mode_1) initialize -strict -type CAE {'+save_mesh_folder+'}\n',
'  $_TMP(mode_1) verify\n',
'  $_TMP(mode_1) write\n',
'$_TMP(mode_1) end\n',
'unset _TMP(mode_1)\n',
'\n',
'pw::Application save {'+pointwise_folder+'}\n',
'pw::Application exit'
    ]

    #%% save the glyph
    with open(file_name,'w') as filehandle: filehandle.writelines(array)





