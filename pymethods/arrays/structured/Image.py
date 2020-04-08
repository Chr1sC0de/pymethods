import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import skimage.transform as skt
import cv2
import scipy.ndimage.morphology as snm
from skimage import measure as measure
import skimage.morphology as skm


class Image(np.ndarray):

    def __new__(cls, imagePathOrArray, rescale=True, **kwargs):
        """__new__

        initialization of the image object

        Args:
            imagePathOrArray (str or np.ndarray): np.ndarray subclass or
                string. If array it must be of shape MxNx3 or MxN
            rescale (bool, optional): originally pixel intensity is from 0 to
                255, if true rescale from 0 to 1. Defaults to True.

        Returns:
            Image: returns image object
        """
        if any(
            [isinstance(imagePathOrArray, objType) for objType in [str, Path]]
        ):
            image = plt.imread(imagePathOrArray)
        elif isinstance(imagePathOrArray, np.ndarray):
            image = imagePathOrArray

        image = np.asarray(image).view(cls)*1.0

        if len(image.shape) > 3:
            image = image.squeeze()
            if len(image.shape) > 3:
                raise Exception(
                        'image tensor must have len(shape) < 2')

        if image.shape[-1] == 4:
            image = image[:, :, 0:3]

        if rescale:
            image = image*1.0/image.max()

        return image

    def resize(self, newSize, *args, **kwargs):
        """resize

        resize image using skimage.transform.resize

        Args:
            newSize (iterable): list or array of [height, width]
            args, kwargs: inputs to
                https://scikit-image.org/docs/dev/api/skimage.transform.html#skimage.transform.resize

        Returns:
            Image: image reshaped to newSize
        """
        return self.__class__(skt.resize(self, newSize))

    def to_gray(self):
        """to_gray

        convert the image to grayscale

        Returns:
            Image: grayscale of dims MxN
        """
        r, g, b = self[:, :, 0], self[:, :, 1], self[:, :, 2]
        gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
        return gray.view(self.__class__)

    def to_polar(self, retainRandC=True):
        """to_polar

        convert the image into a polar image using cv2 linear polar method
        https://docs.opencv.org/2.4/modules/imgproc/doc/geometric_transformations.html

        Args:
            ret_mval_shape (bool, optional): [description]. Defaults to True.
        Returns:
            either image in polar or tuple containing polar image and mean val (center) and radius
        """
        im_as_float64 = self.astype(np.float64)
        Mvalue = np.sqrt(
                ((im_as_float64.shape[0]/2.0)**2.0) +
                ((im_as_float64.shape[1]/2.0)**2.0)
            )
        ima_shape = (im_as_float64.shape[0]/2, im_as_float64.shape[1]/2)
        polar_image = cv2.linearPolar(
            im_as_float64, ima_shape, Mvalue, cv2.WARP_FILL_OUTLIERS)

        if retainRandC:
            return self.__class__(polar_image), [Mvalue, ima_shape]
        else:
            return self.__class__(polar_image)

    def to_cartesian(self, center, radius):
        """to_cartesian

        for given centroid and radius convert image into a cartesian image
        using cv2.linearPolar

        Args:
            center (List[float]): [x,y]  co-ordinates of image centroid
            radius (float): radius of image

        Returns:
            Image: Cartesian image
        """
        im_as_float64 = self.astype(np.float64)
        cart_image = cv2.linearPolar(
            im_as_float64, center, radius, cv2.WARP_INVERSE_MAP)
        return self.__class__(cart_image)

    def show(self, *args, ax=None, axisOn=False, **kwargs):
        """show

        Args:
            ax (plt.ax, optional): axis to plot figure, if none create get
                current axis. Defaults to None.
            axis_on (bool, optional): axis on or off. Defaults to False.
        Return:
            matplotlib figure and axis objects
        """
        ax = plt.gca()
        ax.imshow(self, *args, **kwargs)
        if not axisOn:
            ax.axis('off')
        fig = plt.gcf()
        return fig, ax

    @staticmethod
    def le(image, threshhold):
        """le

        for the given image values <= threshhold == True

        Args:
            image (array):
            threshhold (float):

        Returns:
            Image: threshholded image
        """
        return Image(image < threshhold)

    @staticmethod
    def ge(image, threshhold):
        """ge

        or the given image values >= threshhold == True

        Args:
            image (array):
            threshhold (float):

        Returns:
            Image: threshholded image
        """
        return Image(image > threshhold)

    @staticmethod
    def eq(image, threshhold):
        """eq

        for the given image values == threshhold == True

        Args:
            image (array):
            threshhold (float):

        Returns:
            Image: threshholded image
        """
        return Image(image == threshhold)

    def threshholdRGBToBinary(self, rgb, check=['ge', 'le', 'le']):
        """threshholdRGBToBinary

        Create binary image using threshholds (rgb) and checks. For example if
        rgb = [1,0,0] and check = ['ge','le','le'] return binary image where 1
        is red and 0 is all other colors. 'ge'<= and 'le'>=

        Args:
            rgb (list or array): values to threshhold
            check (list, optional): checks to be performed. Defaults to
            ['ge', 'le', 'le'].

        Returns:
            BinaryImage: array of shape MxN
        """
        assert len(self.shape) == 3, Exception(
            'the following is not satisfied len(shape) == 3'
        )
        RGB = []
        for i, (chk, thresh) in enumerate(zip(check, rgb)):
            RGB.append(getattr(self, chk)(self[:, :, i], thresh))
        return BinaryImage(np.logical_and.reduce(RGB))


class BinaryImage(Image):
    """BinaryImage

    Mirror class to Image. Allows for fast binary operations

    Args:
        array (Image): Image to be converted into binary Image

    """
    def __new__(cls, array):

        array = np.squeeze(array)
        array[array > 0.5] = 1.0
        array[array < 0.5] = 0.0
        return np.asarray(array.astype(int)).view(BinaryImage).astype(int)

    def removeSmallObjects(self, **kwargs):
        """removeSmallObjects

        scipy.ndimage.morphology.remove_small_objects wrapper

        Returns:
            BinaryImage:
        """
        return BinaryImage(skm.remove_small_objects(self, **kwargs))

    def morhpClose(self, **kwargs):
        """close

        morphological closing
        https://en.wikipedia.org/wiki/Closing_(morphology)

        Args:
            iterations (int, optional): . Defaults to 1.
        Returns:
            BinaryImage:
        """
        return BinaryImage(snm.binary_closing(self, **kwargs))

    def fill_holes(self, origin='center', **kwargs):
        """fill_holes

        https://docs.scipy.org/doc/scipy-0.15.1/reference/generated/scipy.ndimage.morphology.binary_fill_holes.html

        Args:
            structure (_np.array, optional):
                [description]. Defaults to _np.ones((3,3)).
        """
        if isinstance(origin, str):
            if origin.lower() == 'center':
                h, w = self.shape
                origin = (h//2, w//2)

        image = skm.flood_fill(self, origin, 1, **kwargs)
        return image

    def morph_open(self, **kwargs):
        """open

        Morphological opening

        Args:
            iterations (int, optional):. Defaults to 1.
        Returns:
            BinaryImage:
        """
        return BinaryImage(snm.binary_opening(self, **kwargs))

    def detect_edges(self):
        """edge_detection

        detect edge via dilation followed by erosion

        Returns:
            BinaryImage:
        """
        dilation = snm.binary_dilation(self)
        erosion = snm.binary_erosion(self)
        return BinaryImage(
            dilation.astype(np.float32)-erosion.astype(np.float32))

    def measure(self, *args, **kwargs):
        return [np.fliplr(m) for m in measure.find_contours(self, *args, **kwargs)]

    def grab_contour(self):
        """grab_contour

        returns first
        https://scikit-image.org/docs/dev/auto_examples/edges/plot_contours.html

        Returns:
            CartContour:
        """
        contours = measure.find_contours(self, 0.8)[0]
        return np.fliplr(contours)
