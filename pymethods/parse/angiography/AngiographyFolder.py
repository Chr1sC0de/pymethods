import pathlib as pt
try:
    from pymethods.parse.angiography import Data
    from pymethods.arrays import Curve, FlatContour
    from pymethods import math
except ImportError:
    from .angiography import Data
    from ...arrays import Curve, FlatContour
    from ... import math
from abc import abstractmethod
import numpy as np
import os


class _FolderDescriptor:

    def __init__(self, filename, post_process=None):
        self.filename = filename
        self.post_process = post_process

    def __get__(self, obj, objtype):
        output = obj.parse_filepath(self.filename)
        if self.post_process is None:
            return output
        else:
            output.data = self.post_process(output.data)
            return output


def post_process_ellipse(parsed_data):
    return [FlatContour(contour) for contour in parsed_data]


class Folder:

    parsable_classes = ['LkebCurve', 'LkebCurveSet']

    bifCenterline1 = _FolderDescriptor(
        'bifCenterline1.data', post_process=Curve)
    bifCenterline2 = _FolderDescriptor(
        'bifCenterline2.data', post_process=Curve)

    centerline1 = _FolderDescriptor(
        'centerline1.data', post_process=Curve)
    centerline2 = _FolderDescriptor(
        'centerline2.data', post_process=Curve)

    BifCoreEllipseSetellipseSet = _FolderDescriptor(
        'BifCoreEllipseSetellipseSet.data', post_process=post_process_ellipse)
    BifCoreEllipseSetellipseSet = _FolderDescriptor(
        'BifCoreEllipseSetellipseSet.data', post_process=post_process_ellipse)

    CrossSectionEllipseSet1 = _FolderDescriptor(
        'CrossSectionEllipseSet1.data', post_process=post_process_ellipse)
    CrossSectionEllipseSet2 = _FolderDescriptor(
        'CrossSectionEllipseSet2.data', post_process=post_process_ellipse)

    def __init__(self, folderPath):
        self.folderPath = pt.Path(folderPath)

    @abstractmethod
    def grabParseSave(self):
        NotImplemented

    @abstractmethod
    def quickrun(self):
        NotImplemented

    def get_filepath(self, filename):
        for filePath in self.files:
            if filename == filePath.name:
                reqFilePath = filePath
                break
        return reqFilePath

    def parse_filepath(self, filename):
        return Data(self.get_filepath(filename))

    def save(self, filePath):
        np.save(
            filePath,
            self
        )

    @staticmethod
    def fromNP(np_path):
        np_path = pt.Path(np_path)
        if np_path.suffix.lower() == '.npy':
            return np.load(np_path, allow_pickle=True).item()
        if np_path.suffix.lower() == '.npz':
            return np.load(np_path).item()

    @property
    def files(self):
        return list(self.folderPath.glob('*.data'))

    @property
    def filenames(self):
        return [filePath.name for filePath in self.files]

    @property
    def numpy_files(self):
        files = list(self.folderPath.glob('*'))
        return [
            item for item in files if item.suffix.lower() in ['.npy', '.npz']
        ]

    def clean(self):
        [
            os.remove(file) for file
            in self.folderPath.glob('*')
            if file.name not in angiography_files
        ]


class OrientCenterlinesBase(Folder):
    main_centerline_id = None
    bifur_centerline_id = None

    def parse(self, resolution=0.001):
        interped = np.linspace(0, 1, int(1/resolution))
        self._mainCenterline = Curve(self.parse_filepath(
            self.main_centerline_id).data)(interped)
        self._bifurCenterline = Curve(self.parse_filepath(
            self.bifur_centerline_id).data)(interped)

        self._sorMainDistalToProximal()
        self._sortBifurCenterlinebyMainCenterline()

        return self.data()

    def data(self):
        return dict(
            main=Curve(self._mainCenterline),
            bifur=Curve(self._bifurCenterline),
        )

    def _sortBifurCenterlinebyMainCenterline(self):
        am = self._mainCenterline[:, 0]
        ab, bb = self._bifurCenterline[:, 0], self._bifurCenterline[:, -1]

        if math.l2_norm(am - ab) > math.l2_norm(am - bb):
            self._bifurCenterline = Curve(np.flipud(self._bifurCenterline.T).T)

    def _sorMainDistalToProximal(self):
        am, bm = self._mainCenterline[:, 0], self._mainCenterline[:, -1]
        ab, bb = self._bifurCenterline[:, 0], self._bifurCenterline[:, -1]

        shortestDistanceStart = min(
            math.l2_norm(am-ab),
            math.l2_norm(am-bb)
        )
        shortestDistanceEnd = min(
            math.l2_norm(bm-ab),
            math.l2_norm(bm-bb)
        )

        if shortestDistanceStart < shortestDistanceEnd:
            self._mainCenterline = Curve(np.flipud(self._mainCenterline.T).T)


class MetaOrientCenterlines:
    def __new__(cls, typename, main, bifur):
        return type(
            typename, (OrientCenterlinesBase,), dict(
                main_centerline_id=main,
                bifur_centerline_id=bifur
            )
        )


CenterlinesA = MetaOrientCenterlines(
    'CenterlinesA', 'bifCenterline1.data', 'bifCenterline2.data')

CenterlinesB = MetaOrientCenterlines(
    'CenterlinesB', 'centerline1.data', 'centerline2.data')

angiography_files = [
    'attribCurve1.data',
    'attribCurve2.data',
    'BifAnalysisInfo.data',
    'bifAttrib1Curve.data',
    'bifAttrib2Curve.data',
    'bifBranch1DiameterCurve.data',
    'bifBranch1StenosisCurve.data',
    'bifBranch2DiameterCurve.data',
    'bifBranch2StenosisCurve.data',
    'bifCenterline1.data',
    'bifCenterline1CorCurve.data',
    'bifCenterline2.data',
    'bifCenterline2CorCurve.data',
    'bifCoreAttribCurve.data',
    'BifCoreEllipseSetellipseSet.data',
    'BifCoreEllipseSetnumPerSlice.data',
    'BifCoreEllipseSetrefEllipseSet.data',
    'BifCoreEllipseSetRefSurface.data',
    'BifCoreEllipseSetstenosisCurve.data',
    'BifCoreEllipseSetSurface.data',
    'bifDistal11AttribCurve.data',
    'bifDistal12AttribCurve.data',
    'BifDistalEllipseSet1ellipseSet.data',
    'BifDistalEllipseSet1numPerSlice.data',
    'BifDistalEllipseSet1refEllipseSet.data',
    'BifDistalEllipseSet1RefSurface.data',
    'BifDistalEllipseSet1stenosisCurve.data',
    'BifDistalEllipseSet1Surface.data',
    'BifDistalEllipseSet2ellipseSet.data',
    'BifDistalEllipseSet2numPerSlice.data',
    'BifDistalEllipseSet2refEllipseSet.data',
    'BifDistalEllipseSet2RefSurface.data',
    'BifDistalEllipseSet2stenosisCurve.data',
    'BifDistalEllipseSet2Surface.data',
    'bifProAttribCurve.data',
    'BifProximalEllipseSetellipseSet.data',
    'BifProximalEllipseSetnumPerSlice.data',
    'BifProximalEllipseSetrefEllipseSet.data',
    'BifProximalEllipseSetRefSurface.data',
    'BifProximalEllipseSetstenosisCurve.data',
    'BifProximalEllipseSetSurface.data',
    'BifurcationAnalysis.txt',
    'centerline1.data',
    'centerline1CorCurve.data',
    'centerline2.data',
    'centerline2CorCurve.data',
    'CrossSectionEllipseSet1.data',
    'CrossSectionEllipseSet2.data',
    'frontalBifContourLeft.data',
    'frontalBifContourMiddle.data',
    'frontalBifContourRight.data',
    'frontalDiameterList1.data',
    'frontalDiameterList2.data',
    'FrontalImage.image',
    'lateralBifContourLeft.data',
    'lateralBifContourMiddle.data',
    'lateralBifContourRight.data',
    'lateralDiameterList1.data',
    'lateralDiameterList2.data',
    'LateralImage.image',
    'refBifCenterline1.data',
    'refBifCenterline2.data',
    'refCenterline1.data',
    'refCenterline2.data',
    'view3D.png'
]

if __name__ == "__main__":
    path_angio = pt.Path(r'D:\Github\pymethods\testsReconstruction\test_1\angiography')
    path_oct = pt.Path(r'D:\Github\pymethods\testsReconstruction\test_1\oct')

    folder_angio = CenterlinesA(path_angio)

    folder_angio.parse().values()

    centerline_main.plot3d()
    main_tangents = centerline_main.transport_frames()[:, :, -1]
    centerline_bifur.plot3d()
    main_tangents = centerline_main.transport_frames()[:, :, -1]

    for center, tangent in zip(centerline_main.T, main_tangents.T):
        pma.arrays.Vector(tangent).quiver3d(origin=center)

