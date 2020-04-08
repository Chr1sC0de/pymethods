try:
    from pymethods import arrays, math
    import pymethods.pyplot as plt
except ImportError:
    from ... import arrays, math
    from ... import pyplot as plt
import numpy as np


class Image(arrays.structured.Image):

    def get_contour(
            self,
            color=[0.5, 0.3, 0.3],
            check=['ge', 'le', 'le']):
        binary = self.threshholdRGBToBinary(
            color, check,
        ).fill_holes()
        contour = binary.grab_contour().T
        contour = math.make_3d(contour)
        contour = arrays.Contour(contour)
        return contour

    def get_landmark_vector(
        self, color=[0.3, 0.3, 0.5], check=['le', 'le', 'ge'],
    ):
        binary = self.threshholdRGBToBinary(
            color, check
        )
        landmark = binary.measure(0.8)[0]
        if len(landmark) > 0:
            vector = arrays.ColumnVector(np.mean(landmark, 0).T).make_3d()
            return vector
        else:
            return None


if __name__ == "__main__":
    import pathlib as pt
    if False:
        path = pt.Path(
            r'D:\Github\pymethods\Datasets\oct\pr2_00000.jpg'
        )
        oct_image = Image(path)
        contour = oct_image.get_contour()
        filtered = contour.filter(21, 3)
        plt.plot(*contour)
        plt.plot(*filtered)
        oct_image.show()
        plt.show()

    if True:
        path_bifur = r'D:\Github\pymethods\Datasets\test_1\oct\pr2_00059.jpg'
        oct_image = Image(path_bifur)
        vector = oct_image.get_landmark_vector()
        plt.scatter(*vector)
        oct_image.show()
        plt.show()
