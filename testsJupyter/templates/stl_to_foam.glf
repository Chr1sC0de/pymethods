# Pointwise V18.2R2 Journal file - Fri Apr  5 15:31:18 2019

package require PWI_Glyph 2.18.2
pw::Application setUndoMaximumLevels 5
pw::Application reset
pw::Application markUndoLevel {Journal Reset}

pw::Application clearModified

set _TMP(mode_1) [pw::Application begin DatabaseImport]
  $_TMP(mode_1) initialize -strict -type Automatic {d:/Github/pymethods/testsJupyter/templates/shape.stl}
  $_TMP(mode_1) setAttribute ShellCellMode MergeCoplanar
  $_TMP(mode_1) read
  $_TMP(mode_1) convert
$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Import Database}

pw::Connector setCalculateDimensionMethod Spacing
pw::Connector setCalculateDimensionSpacing 0.1
pw::Application setGridPreference Unstructured
set _DB(1)  [pw::DatabaseEntity getBySequence 1]
set _TMP(PW_33) [pw::DomainUnstructured createOnDatabase -parametricConnectors Aligned -merge 0 -reject _TMP(unused) [list $_DB(1)]]
unset _TMP(unused)
unset _TMP(PW_33)
pw::Application markUndoLevel {Domains On DB Entities}

set _CN(1) [pw::GridEntity getByName "con-1"]
set _CN(2) [pw::GridEntity getByName "con-2"]
set _TMP(PW_34) [pw::DomainUnstructured createFromConnectors -reject _TMP(unusedCons)  [list $_CN(1) $_CN(2)]]
unset _TMP(unusedCons)
unset _TMP(PW_34)
pw::Application markUndoLevel {Assemble Domains}

set _CN(3) [pw::GridEntity getByName "con-3"]
set _CN(4) [pw::GridEntity getByName "con-4"]
set _TMP(PW_35) [pw::DomainUnstructured createFromConnectors -reject _TMP(unusedCons)  [list $_CN(3) $_CN(4)]]
unset _TMP(unusedCons)
unset _TMP(PW_35)
pw::Application markUndoLevel {Assemble Domains}

set _DM(1) [pw::GridEntity getByName "dom-3"]
set _DM(2) [pw::GridEntity getByName "dom-2"]
set _TMP(mode_10) [pw::Application begin UnstructuredSolver [list $_DM(1) $_DM(2)]]
  set _TMP(ENTS) [pw::Collection create]
$_TMP(ENTS) set [list $_DM(1) $_DM(2)]
  $_TMP(ENTS) do setUnstructuredSolverAttribute ShapeConstraint Free
  $_TMP(ENTS) delete
  unset _TMP(ENTS)
  $_TMP(mode_10) run Initialize
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Solve}

set _DM(3) [pw::GridEntity getByName "dom-1"]
set _TMP(PW_36) [pw::BlockUnstructured createFromDomains -reject _TMP(unusedDoms) -voids _TMP(voidBlocks) -baffles _TMP(baffleFaces) [concat [list] [list $_DM(1) $_DM(3) $_DM(2)]]]
unset _TMP(unusedDoms)
unset _TMP(PW_36)
pw::Application markUndoLevel {Assemble Blocks}

set _BL(1) [pw::GridEntity getByName "blk-1"]
set _TMP(mode_10) [pw::Application begin UnstructuredSolver [list $_BL(1)]]
  set _TMP(ENTS) [pw::Collection create]
$_TMP(ENTS) set [list $_BL(1)]
  $_BL(1) setUnstructuredSolverAttribute TRexMaximumLayers 6
  $_BL(1) setUnstructuredSolverAttribute TRexGrowthRate 1.300000
  $_BL(1) setUnstructuredSolverAttribute TRexGrowthRate 1.100000
  $_BL(1) setUnstructuredSolverAttribute TRexPushAttributes True
  $_BL(1) setUnstructuredSolverAttribute TRexSkewCriteriaMaximumAngle 180
  $_BL(1) setUnstructuredSolverAttribute TRexSkewCriteriaMaximumAngle 170
  $_TMP(ENTS) delete
  unset _TMP(ENTS)
  set _TMP(PW_37) [pw::TRexCondition getByName {Unspecified}]
  set _TMP(PW_38) [pw::TRexCondition create]
  set _TMP(PW_39) [pw::TRexCondition getByName {bc-2}]
  unset _TMP(PW_38)
  set _TMP(PW_40) [pw::TRexCondition create]
  set _TMP(PW_41) [pw::TRexCondition getByName {bc-3}]
  unset _TMP(PW_40)
  $_TMP(PW_39) setConditionType {Wall}
  $_TMP(PW_41) setConditionType {Match}
  $_TMP(PW_39) apply [list [list $_BL(1) $_DM(3) Same]]
  $_TMP(PW_41) apply [list [list $_BL(1) $_DM(2) Opposite] [list $_BL(1) $_DM(1) Opposite]]
  $_TMP(PW_39) setSpacing 0.025000
  $_TMP(mode_10) run Initialize
$_TMP(mode_10) end
unset _TMP(mode_10)
pw::Application markUndoLevel {Solve}

unset _TMP(PW_37)
unset _TMP(PW_39)
unset _TMP(PW_41)
pw::Application setCAESolver {OpenFOAM} 3
pw::Application markUndoLevel {Select Solver}

set _TMP(PW_42) [pw::BoundaryCondition getByName {Unspecified}]
set _TMP(PW_43) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_44) [pw::BoundaryCondition getByName {bc-2}]
unset _TMP(PW_43)
set _TMP(PW_45) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_46) [pw::BoundaryCondition getByName {bc-3}]
unset _TMP(PW_45)
set _TMP(PW_47) [pw::BoundaryCondition create]
pw::Application markUndoLevel {Create BC}

set _TMP(PW_48) [pw::BoundaryCondition getByName {bc-4}]
unset _TMP(PW_47)
$_TMP(PW_44) setName "WALL"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_46) setName "INLET"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_48) setName "OUTLET"
pw::Application markUndoLevel {Name BC}

$_TMP(PW_44) setPhysicalType -usage CAE {wall}
pw::Application markUndoLevel {Change BC Type}

$_TMP(PW_46) setPhysicalType -usage CAE {patch}
pw::Application markUndoLevel {Change BC Type}

$_TMP(PW_48) setPhysicalType -usage CAE {patch}
pw::Application markUndoLevel {Change BC Type}

pw::Display setShowDatabase 0
$_TMP(PW_44) apply [list [list $_BL(1) $_DM(3)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_46) apply [list [list $_BL(1) $_DM(2)]]
pw::Application markUndoLevel {Set BC}

$_TMP(PW_48) apply [list [list $_BL(1) $_DM(1)]]
pw::Application markUndoLevel {Set BC}

unset _TMP(PW_42)
unset _TMP(PW_44)
unset _TMP(PW_46)
unset _TMP(PW_48)
set _BL(1) [pw::GridEntity getByName blk-1]
set _TMP(mode_1) [pw::Application begin Modify [list $_BL(1)]]
pw::Entity transform [pwu::Transform scaling -anchor {0 0 0} {0.001 0.001 0.001}] [$_TMP(mode_1) getEntities]
	$_TMP(mode_1) end
unset _TMP(mode_1)
pw::Application markUndoLevel {Scale}

set _TMP(mode_1) [pw::Application begin CaeExport]
  $_TMP(mode_1) addAllEntities
  $_TMP(mode_1) initialize -strict -type CAE {.}
  $_TMP(mode_1) verify
  $_TMP(mode_1) write
$_TMP(mode_1) end
unset _TMP(mode_1)

pw::Application save {foam_project.pw}
pw::Application exit